from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
import razorpay
import os
import json
from datetime import datetime, timedelta
import asyncio
from projects.backend.services.email_service import email_service
from projects.backend.dependencies import get_current_user
from projects.backend.services.db_service import db_service

router = APIRouter()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_API_KEY")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_API_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

# Initialize Razorpay client (reuse existing credentials)
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Razorpay Plan IDs (will be configured after creating plans in dashboard)
SUBSCRIPTION_PLANS = {
    "starter_monthly": os.getenv("RAZORPAY_PLAN_STARTER_MONTHLY", ""),
    "starter_annual": os.getenv("RAZORPAY_PLAN_STARTER_ANNUAL", ""),
    "growth_monthly": os.getenv("RAZORPAY_PLAN_GROWTH_MONTHLY", ""),
    "growth_annual": os.getenv("RAZORPAY_PLAN_GROWTH_ANNUAL", ""),
    "agency_monthly": os.getenv("RAZORPAY_PLAN_AGENCY_MONTHLY", ""),
    "agency_annual": os.getenv("RAZORPAY_PLAN_AGENCY_ANNUAL", "")
}

# Credits per tier (monthly allocation)
TIER_CREDITS = {
    'starter': 40,
    'growth': 150,
    'agency': 600
}


class CreateSubscriptionRequest(BaseModel):
    tier: str  # "starter", "growth", or "agency"
    period: str  # "monthly" or "annual"


class UpdateSubscriptionRequest(BaseModel):
    new_tier: str


@router.post("/create")
async def create_subscription(
    request: CreateSubscriptionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create a new Razorpay subscription for the user.
    Returns subscription ID and payment link.
    """
    try:
        user_id = user.get("uid")
        user_email = user.get("email")
        
        # Validate tier and period
        if request.tier not in ["starter", "growth", "agency"]:
            raise HTTPException(status_code=400, detail="Invalid tier")
        if request.period not in ["monthly", "annual"]:
            raise HTTPException(status_code=400, detail="Invalid period")
            
        # BLOCK AGENCY ANNUAL (Exceeds Razorpay Limits)
        if request.tier == "agency" and request.period == "annual":
             raise HTTPException(
                status_code=400, 
                detail="Agency Annual plan is currently unavailable due to payment gateway limits. Please select the Agency Monthly plan."
            )
        
        # Check if user already has active subscription
        existing_subscription = db_service.get_user_subscription(user_id)
        if existing_subscription and existing_subscription.get("status") == "active":
            raise HTTPException(
                status_code=400,
                detail="User already has an active subscription. Cancel existing subscription first."
            )
        
        # Get plan ID
        plan_key = f"{request.tier}_{request.period}"
        plan_id = SUBSCRIPTION_PLANS.get(plan_key)
        
        if not plan_id:
            configured_plans = {k: bool(v) for k, v in SUBSCRIPTION_PLANS.items()}
            raise HTTPException(
                status_code=400,
                detail=f"Subscription plan not configured for {plan_key}. Please contact support. Configured plans: {configured_plans}"
            )
        
        # Create Razorpay subscription
        subscription_data = {
            "plan_id": plan_id,
            "customer_notify": 1,
            "total_count": 12 if request.period == "annual" else 120,  # Annual: 12 months, Monthly: 120 months (~10 years)
            "notes": {
                "user_id": user_id,
                "tier": request.tier,
                "period": request.period
            }
        }

        subscription = client.subscription.create(subscription_data)
        
        # Save subscription to database
        db_service.create_subscription(user_id, {
            "razorpay_subscription_id": subscription["id"],
            "tier": request.tier,
            "period": request.period,
            "status": "created",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        return {
            "subscription_id": subscription["id"],
            "short_url": subscription.get("short_url"),
            "tier": request.tier,
            "period": request.period,
            "monthly_credits": TIER_CREDITS[request.tier]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create subscription: {str(e)}")


@router.post("/webhook")
async def subscription_webhook(request: Request):
    """
    Handle Razorpay subscription webhooks.
    Main events:
    - subscription.charged: Reset monthly credits
    - subscription.cancelled: Deactivate subscription
    - subscription.paused: Handle pause
    """
    try:
        payload = await request.body()
        signature = request.headers.get("X-Razorpay-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # Verify webhook signature
        try:
            client.utility.verify_webhook_signature(
                payload.decode("utf-8"),
                signature,
                RAZORPAY_WEBHOOK_SECRET
            )
        except Exception as e:
            print(f"Webhook signature verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        event = json.loads(payload)
        event_type = event.get("event")
        
        print(f"Received webhook event: {event_type}")
        
        if event_type == "subscription.charged":
            # Payment successful - reset monthly credits
            subscription_entity = event["payload"]["subscription"]["entity"]
            subscription_id = subscription_entity["id"]
            
            # Get user subscription from database
            user_subscription = db_service.get_subscription_by_razorpay_id(subscription_id)
            
            if user_subscription:
                tier = user_subscription["tier"]
                user_id = user_subscription["user_id"]
                
                # Reset credits to tier amount
                credits_to_set = TIER_CREDITS.get(tier, 40)
                db_service.set_credits(user_id, credits_to_set)
                
                # Update subscription status
                db_service.update_subscription(user_id, {
                    "status": "active",
                    "current_period_end": datetime.now() + timedelta(days=30),
                    "updated_at": datetime.now()
                })
                
                print(f"Reset credits for user {user_id} to {credits_to_set} (tier: {tier})")

                # Send Invoice Email
                try:
                    # Get payment details from payload if available, else usage defaults
                    payment_id = event["payload"]["payment"]["entity"]["id"] if "payment" in event["payload"] else "PAY-" + str(int(datetime.now().timestamp()))
                    amount = event["payload"]["payment"]["entity"]["amount"] / 100 if "payment" in event["payload"] else 0
                    currency = event["payload"]["payment"]["entity"]["currency"] if "payment" in event["payload"] else "USD"
                    
                    # Fetch user email - we need to get user profile first
                    user_profile = db_service.get_user_profile(user_id)
                    user_email = user_profile.get("email") if user_profile else None
                    user_name = user_profile.get("name", "Valued Customer") if user_profile else "Valued Customer"

                    if user_email:
                         asyncio.create_task(email_service.send_invoice_email(
                            user_email=user_email,
                            user_name=user_name,
                            invoice_details={
                                "invoice_number": payment_id,
                                "date": datetime.now().strftime("%B %d, %Y"),
                                "plan_name": tier.title(),
                                "period_start": datetime.now().strftime("%b %d, %Y"),
                                "period_end": (datetime.now() + timedelta(days=30)).strftime("%b %d, %Y"),
                                "currency": currency,
                                "amount": amount
                            }
                        ))
                except Exception as e:
                    print(f"Error sending invoice email: {e}")

            
        elif event_type == "subscription.cancelled":
            # Subscription cancelled
            subscription_entity = event["payload"]["subscription"]["entity"]
            subscription_id = subscription_entity["id"]
            
            user_subscription = db_service.get_subscription_by_razorpay_id(subscription_id)
            
            if user_subscription:
                user_id = user_subscription["user_id"]
                
                db_service.update_subscription(user_id, {
                    "status": "cancelled",
                    "cancel_at_period_end": True,
                    "updated_at": datetime.now()
                })
                
                print(f"Subscription cancelled for user {user_id}")
        
        elif event_type == "subscription.paused":
            # Subscription paused
            subscription_entity = event["payload"]["subscription"]["entity"]
            subscription_id = subscription_entity["id"]
            
            user_subscription = db_service.get_subscription_by_razorpay_id(subscription_id)
            
            if user_subscription:
                user_id = user_subscription["user_id"]
                
                db_service.update_subscription(user_id, {
                    "status": "paused",
                    "updated_at": datetime.now()
                })
                
                print(f"Subscription paused for user {user_id}")
        
        return {"status": "success", "event": event_type}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/status")
async def get_subscription_status(user: dict = Depends(get_current_user)):
    """
    Get current user's subscription status.
    """
    try:
        user_id = user.get("uid")
        subscription = db_service.get_user_subscription(user_id)
        
        if not subscription:
            return {
                "has_subscription": False,
                "tier": None,
                "status": None
            }
        
        return {
            "has_subscription": True,
            "tier": subscription.get("tier"),
            "status": subscription.get("status"),
            "period": subscription.get("period"),
            "current_period_end": subscription.get("current_period_end"),
            "cancel_at_period_end": subscription.get("cancel_at_period_end", False),
            "monthly_credits": TIER_CREDITS.get(subscription.get("tier"), 0)
        }
        
    except Exception as e:
        print(f"Error fetching subscription status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscription status")


@router.post("/cancel")
async def cancel_subscription(user: dict = Depends(get_current_user)):
    """
    Cancel user's subscription (at end of billing period).
    """
    try:
        user_id = user.get("uid")
        subscription = db_service.get_user_subscription(user_id)
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        if subscription.get("status") != "active":
            raise HTTPException(status_code=400, detail="Subscription is not active")
        
        razorpay_subscription_id = subscription.get("razorpay_subscription_id")
        
        # Cancel in Razorpay (at end of period)
        client.subscription.cancel(razorpay_subscription_id, {
            "cancel_at_cycle_end": 1
        })
        
        # Update in database
        db_service.update_subscription(user_id, {
            "cancel_at_period_end": True,
            "updated_at": datetime.now()
        })
        
        return {
            "status": "success",
            "message": "Subscription will be cancelled at the end of the billing period"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")


@router.post("/update")
async def update_subscription(
    request: UpdateSubscriptionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Update subscription tier (upgrade/downgrade).
    """
    try:
        user_id = user.get("uid")
        subscription = db_service.get_user_subscription(user_id)
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        if request.new_tier not in ["starter", "growth", "agency"]:
            raise HTTPException(status_code=400, detail="Invalid tier")
        
        current_tier = subscription.get("tier")
        if current_tier == request.new_tier:
            raise HTTPException(status_code=400, detail="Already on this tier")
        
        # Note: Actual tier change would require creating new subscription in Razorpay
        # and cancelling old one. This is a simplified version.
        
        db_service.update_subscription(user_id, {
            "tier": request.new_tier,
            "updated_at": datetime.now()
        })
        
        # Adjust credits immediately
        new_credits = TIER_CREDITS[request.new_tier]
        db_service.set_credits(user_id, new_credits)
        
        return {
            "status": "success",
            "new_tier": request.new_tier,
            "monthly_credits": new_credits,
            "message": "Subscription updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update subscription: {str(e)}")
