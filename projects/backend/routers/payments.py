from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import razorpay
import os
from datetime import datetime
from projects.backend.dependencies import get_current_user
from projects.backend.services.db_service import db_service
from projects.backend.services.email_service import email_service

router = APIRouter()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_API_KEY")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_API_SECRET")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

PRICING_TIERS = {
    "starter": {"amount": 4900, "credits": 50, "currency": "USD", "name": "Starter Pack"},
    "growth": {"amount": 14900, "credits": 200, "currency": "USD", "name": "Growth Pack"},
    "agency": {"amount": 49700, "credits": 800, "currency": "USD", "name": "Agency Pack"}
}

class CreateOrderRequest(BaseModel):
    tier: str  # "starter", "builder", or "scale"

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    # amount is no longer needed from client as we fetch it from Razorpay

@router.post("/create-order")
async def create_order(request: CreateOrderRequest, user: dict = Depends(get_current_user)):
    try:
        # Validate tier
        if request.tier not in PRICING_TIERS:
            raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {', '.join(PRICING_TIERS.keys())}")
        
        tier_info = PRICING_TIERS[request.tier]
        user_id = user.get("uid")
        
        # Razorpay receipt max length is 40 chars.
        # Firebase UID is ~28 chars.
        # Format: {tier[:4]}_{timestamp(10)}_{uid[-6:]} 
        # Example: star_1705758000_abc123
        ts = int(datetime.now().timestamp())
        short_uid = user_id[-6:] if user_id else "anon"
        receipt_id = f"{request.tier[:4]}_{ts}_{short_uid}"
        
        order_data = {
            "amount": tier_info["amount"],
            "currency": tier_info["currency"],
            "receipt": receipt_id,
            "payment_capture": 1  # Auto capture
        }
        order = client.order.create(data=order_data)
        
        # Return order with tier info for frontend reference
        order["tier"] = request.tier
        order["credits"] = tier_info["credits"]
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify")
async def verify_payment(request: VerifyPaymentRequest, user: dict = Depends(get_current_user)):
    try:
        user_id = user.get("uid")
        
        # 1. Verify signature first (Client side integrity)
        params_dict = {
            'razorpay_order_id': request.razorpay_order_id,
            'razorpay_payment_id': request.razorpay_payment_id,
            'razorpay_signature': request.razorpay_signature
        }
        
        client.utility.verify_payment_signature(params_dict)
        
        # 2. Fetch payment details from Razorpay (Server side integrity)
        # CRITICAL: Do not trust amount sent by client
        payment_details = client.payment.fetch(request.razorpay_payment_id)
        
        # 3. Verify payment status
        if payment_details['status'] != 'captured':
             # Try to capture if authorized but not captured
            if payment_details['status'] == 'authorized':
                 try:
                     payment_details = client.payment.capture(request.razorpay_payment_id, payment_details['amount'])
                 except Exception as capture_err:
                     raise HTTPException(status_code=400, detail=f"Payment authorized but capture failed: {str(capture_err)}")
            else:
                raise HTTPException(status_code=400, detail=f"Invalid payment status: {payment_details['status']}")

        # 4. Use trusted amount from Razorpay
        amount_in_paise = payment_details['amount']
        
        # Record payment with trusted details
        db_service.record_payment(user_id, {**params_dict, 'amount': amount_in_paise, 'currency': payment_details['currency']})
        
        credits_to_add = 0
        package_name = "Custom Tier"
        
        # Match exact tier amounts
        for tier_key, tier_info in PRICING_TIERS.items():
            if abs(amount_in_paise - tier_info["amount"]) < 100:  # Allow 1 rupee tolerance
                credits_to_add = tier_info["credits"]
                package_name = tier_info["name"]
                break
        
        # Fallback for custom amounts ($1 ~ 1 credit)
        if credits_to_add == 0:
            # amount_in_cents / 100 = Dollars. * 1 = credits.
            credits_to_add = max(1, int((amount_in_paise / 100)))
            
        db_service.add_credits(user_id, credits_to_add)
        
        # Get new balance and user info for email
        new_balance = db_service.get_credits(user_id)
        user_data = db_service.get_user_profile(user_id)
        
        # --- SEND EMAIL NOTIFICATION (Credit Purchase Confirmation) ---
        try:
            if user_data and user_data.get("email"):
                await email_service.send_credit_purchase_confirmation(
                    user_email=user_data.get("email"),
                    user_name=user_data.get("name", "there"),
                    transaction={
                        "transaction_id": request.razorpay_payment_id,
                        "amount": amount_in_paise / 100, # Display in Rupees
                        "credits_purchased": credits_to_add,
                        "new_balance": new_balance,
                        "timestamp": datetime.now(),
                        "payment_method": "Razorpay",
                        "package": package_name
                    }
                )
                print(f"Credit purchase confirmation email sent to {user_data.get('email')}")
        except Exception as email_err:
            print(f"Error sending credit purchase email: {email_err}")
        
        return {
            "status": "success", 
            "message": f"Payment verified. {credits_to_add} credits added.",
            "credits_added": credits_to_add,
            "new_balance": new_balance
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Payment verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payment or signature")

@router.get("/credits")
async def get_user_credits(user: dict = Depends(get_current_user)):
    user_id = user.get("uid")
    balance = db_service.get_credits(user_id)
    return {"credits": balance}
