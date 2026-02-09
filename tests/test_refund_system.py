"""
Test script for credit refund system.
Tests the idempotent refund logic and ensures no double refunds occur.
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projects.backend.services.db_service import db_service

def test_refund_credits():
    """Test credit refund system"""
    print("=" * 60)
    print("Testing Credit Refund System")
    print("=" * 60)
    
    # Test parameters
    test_user_id = "test_user_refund_123"
    test_run_id = "run_" + str(int(__import__('time').time()))
    refund_amount = 10
    refund_reason = "TEST: Visual DNA extraction failed"
    
    print(f"\n1. Getting initial credit balance for test user: {test_user_id}")
    initial_credits = db_service.get_credits(test_user_id)
    print(f"   Initial credits: {initial_credits}")
    
    print(f"\n2. First refund attempt (should succeed)...")
    result1 = db_service.refund_credits(
        user_id=test_user_id,
        amount=refund_amount,
        reason=refund_reason,
        run_id=test_run_id
    )
    print(f"   Result: {result1}")
    
    # Check new balance
    new_credits = db_service.get_credits(test_user_id)
    print(f"   New credit balance: {new_credits}")
    expected = initial_credits + refund_amount
    assert new_credits == expected, f"Expected {expected}, got {new_credits}"
    print(f"   ✅ Credits correctly increased by {refund_amount}")
    
    print(f"\n3. Second refund attempt with same run_id (should be idempotent - no double refund)...")
    result2 = db_service.refund_credits(
        user_id=test_user_id,
        amount=refund_amount,
        reason=refund_reason,
        run_id=test_run_id
    )
    print(f"   Result: {result2}")
    assert result2 == False, "Second refund should return False (already processed)"
    
    # Check balance didn't change
    final_credits = db_service.get_credits(test_user_id)
    print(f"   Final credit balance: {final_credits}")
    assert final_credits == new_credits, "Credits should not change on duplicate refund"
    print(f"   ✅ Idempotency check passed - no double refund occurred")
    
    print(f"\n4. Verifying audit trail exists...")
    refund_doc_id = f"{test_run_id}_refund"
    refund_ref = db_service.db.collection('refunds').document(refund_doc_id)
    refund_data = refund_ref.get().to_dict()
    
    assert refund_data is not None, "Refund record should exist"
    assert refund_data['user_id'] == test_user_id
    assert refund_data['amount'] == refund_amount
    assert refund_data['run_id'] == test_run_id
    print(f"   ✅ Audit trail verified:")
    print(f"      - User ID: {refund_data['user_id']}")
    print(f"      - Amount: {refund_data['amount']}")
    print(f"      - Reason: {refund_data['reason']}")
    print(f"      - Timestamp: {refund_data['timestamp']}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        test_refund_credits()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
