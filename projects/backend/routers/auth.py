"""
Authentication Router
Handles email verification, email preferences, and free tier signup
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import secrets
import time
from projects.backend.dependencies import get_current_user
from projects.backend.services.db_service import db_service
from projects.backend.services.email_service import email_service
from projects.backend.firebase_setup import auth

router = APIRouter()

# Rate limiting storage (in-memory, use Redis in production)
signup_attempts = {}

# ============= Models =============

class FreeSignupRequest(BaseModel):
    uid: str
    email: EmailStr
    name: str
    provider: str  # 'google' or 'email'

class EmailPreferences(BaseModel):
    operational: bool = True
    marketing: bool = True

class VerifyEmailRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: str

# ============= Free Tier Signup =============

@router.post("/free-signup")
async def free_signup(request: FreeSignupRequest, req: Request):
    """
    Handle free tier signup from landing page.
    - Check rate limiting (max 3 signups per IP per day)
    - Validate email (block disposable domains)
    - Create user profile
    - Send verification email (if email provider)
    - Award 10 credits for Google users (auto-verified)
    - Return custom token for auto sign-in
    """
    try:
        client_ip = req.client.host
        
        # 1. Rate Limiting Check
        current_time = time.time()
        day_key = time.strftime("%Y-%m-%d")
        rate_key = f"{client_ip}:{day_key}"
        
        if rate_key in signup_attempts:
            if signup_attempts[rate_key] >= 3:
                raise HTTPException(status_code=429, detail="Too many signup attempts. Try again tomorrow.")
            signup_attempts[rate_key] += 1
        else:
            signup_attempts[rate_key] = 1
        
        # 2. Disposable Email Check
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'throwaway.email', 'mailinator.com', 'temp-mail.org',
            'getnada.com', 'trashmail.com', 'fakeinbox.com'
        ]
        email_domain = request.email.split('@')[1].lower()
        if email_domain in disposable_domains:
            raise HTTPException(status_code=400, detail="Disposable email addresses are not allowed.")
        
        # 3. Check if user already exists
        existing_profile = db_service.get_user_profile(request.uid)
        if existing_profile:
            # User exists, just return token
            custom_token = auth.create_custom_token(request.uid)
            return {
                "customToken": custom_token.decode(),
                "existing": True,
                "credits": existing_profile.get("credits", 0)
            }
        
        # 4. Create user profile
        is_google = (request.provider == "google")
        user_data = {
            "email": request.email,
            "name": request.name,
            "provider": request.provider,
            "created_at": current_time,
            "email_verified": is_google,  # Google emails auto-verified
            "credits": 10 if is_google else 0,  # Award credits immediately for Google
            "free_tier": True,
            "signup_ip": client_ip
        }
        
        # Save to Firestore
        db_service.db.collection('users').document(request.uid).set(user_data)
        
        # 5. Send verification email (if email provider)
        if not is_google:
            # Generate verification token
            token = secrets.token_urlsafe(32)
            
            # Store token in Firestore with 24-hour expiry
            db_service.db.collection("email_verification_tokens").document(token).set({
                "user_id": request.uid,
                "email": request.email,
                "expires_at": time.time() + (24 * 60 * 60),  # 24 hours
                "used": False,
                "created_at": time.time(),
                "reward_credits": 10  # Credits to award upon verification
            })
            
            # Send verification email
            await email_service.send_free_tier_verification_email(request.email, request.name, token)
        
        # 6. Generate custom token for auto sign-in
        custom_token = auth.create_custom_token(request.uid)
        
        # Handle both bytes and string return types
        if isinstance(custom_token, bytes):
            custom_token_str = custom_token.decode()
        else:
            custom_token_str = custom_token
        
        return {
            "customToken": custom_token_str,
            "existing": False,
            "email_verified": user_data["email_verified"],
            "credits": user_data["credits"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Free signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= Email Verification =============

@router.post("/send-verification")
async def send_verification_email(user: dict = Depends(get_current_user)):
    """Send email verification link to user"""
    try:
        user_id = user.get("uid")
        email = user.get("email")
        name = user.get("name", "there")
        
        # Check if already verified
        user_record = auth.get_user(user_id)
        if user_record.email_verified:
            return {"message": "Email already verified"}
        
        # Generate verification token
        token = secrets.token_urlsafe(32)
        
        # Store token in Firestore with 24-hour expiry
        db_service.db.collection("email_verification_tokens").document(token).set({
            "user_id": user_id,
            "email": email,
            "expires_at": time.time() + (24 * 60 * 60),  # 24 hours
            "used": False,
            "created_at": time.time()
        })
        
        # Send verification email
        await email_service.send_verification_email(email, name, token)
        
        return {"message": "Verification email sent"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """Verify email using token and award credits for free tier users"""
    try:
        # Get token from Firestore
        token_doc = db_service.db.collection("email_verification_tokens").document(request.token).get()
        
        if not token_doc.exists:
            raise HTTPException(status_code=400, detail="Invalid or expired verification link")
        
        token_data = token_doc.to_dict()
        
        # Check if token is expired
        if token_data.get("expires_at", 0) < time.time():
            raise HTTPException(status_code=400, detail="Verification link has expired")
        
        # Check if token is already used
        if token_data.get("used", False):
            raise HTTPException(status_code=400, detail="Verification link has already been used")
        
        # Update user's email verification status in Firebase Auth
        user_id = token_data.get("user_id")
        auth.update_user(user_id, email_verified=True)
        
        # Mark token as used
        db_service.db.collection("email_verification_tokens").document(request.token).update({
            "used": True,
            "verified_at": time.time()
        })
        
        # Update user document
        db_service.db.collection("users").document(user_id).set({
            "emailVerified": True,
            "emailVerifiedAt": time.time()
        }, merge=True)
        
        # Award credits if this is a free tier signup
        reward_credits = token_data.get("reward_credits", 0)
        if reward_credits > 0:
            db_service.add_credits(user_id, reward_credits)
            return {
                "message": "Email verified successfully", 
                "credits_awarded": reward_credits
            }
        
        return {"message": "Email verified successfully"}
        
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= Email Preferences =============

@router.get("/email-preferences")
async def get_email_preferences(user: dict = Depends(get_current_user)):
    """Get user's email preferences"""
    try:
        user_id = user.get("uid")
        
        # Get preferences from Firestore
        prefs_doc = db_service.db.collection("email_preferences").document(user_id).get()
        
        if prefs_doc.exists:
            return prefs_doc.to_dict()
        else:
            # Return defaults
            return {
                "operational": True,
                "marketing": True
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/email-preferences")
async def update_email_preferences(preferences: EmailPreferences, user: dict = Depends(get_current_user)):
    """Update user's email preferences"""
    try:
        user_id = user.get("uid")
        
        # Save preferences to Firestore
        db_service.db.collection("email_preferences").document(user_id).set({
            "operational": preferences.operational,
            "marketing": preferences.marketing,
            "updated_at": time.time()
        }, merge=True)
        
        return {"message": "Email preferences updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
