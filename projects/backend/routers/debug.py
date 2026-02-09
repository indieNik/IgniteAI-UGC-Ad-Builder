from fastapi import APIRouter, Depends
from projects.backend.dependencies import get_current_user
from pydantic import BaseModel
from projects.backend.services.email_service import email_service


router = APIRouter()

@router.get("/test-auth")
async def test_auth(user: dict = Depends(get_current_user)):
    """
    Debug endpoint to test Firebase authentication.
    Returns the decoded user token if authentication is successful.
    """
    return {
        "authenticated": True,
        "user_id": user.get("uid"),
        "email": user.get("email"),
        "user_data": user
    }

@router.get("/public-test")
async def public_test():
    """
    Public endpoint that doesn't require authentication.
    Use this to test if the backend is reachable.
    """
    return {
        "message": "Public endpoint working",
        "status": "ok"
    }

class TestInvoiceRequest(BaseModel):
    email: str

@router.post("/test-invoice")
async def test_invoice(request: TestInvoiceRequest):
    """
    Debug endpoint to send a test invoice email.
    """
    success = await email_service.send_invoice_email(
        user_email=request.email,
        user_name="Test User",
        invoice_details={
            "invoice_number": "TEST-123456",
            "date": "October 27, 2023",
            "plan_name": "Growth",
            "period_start": "Oct 27, 2023",
            "period_end": "Nov 26, 2023",
            "currency": "USD",
            "amount": "49.00"
        }
    )
    return {"success": success, "email": request.email}
