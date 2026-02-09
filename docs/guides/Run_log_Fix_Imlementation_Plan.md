Pipeline Reliability Implementation Plan
Summary
Based on run log analysis (run_1770457296), the system has critical failures that result in charging users for worthless output. The user paid 10 credits (~$4 USD), but received a generic video with:

Empty Visual DNA (model not found error)
Generic fallback script (model not found error)
75% Ken Burns static animations (3/4 scenes rejected by celebrity filter)
Default voice (model not found error)
No brand-specific content
Root Cause: The code currently logs model errors but continues execution with generic fallbacks, treating failures as successes.

User Review Required
WARNING

Breaking Change: User Experience With this implementation, users will start receiving failure notifications and automatic refunds when Visual DNA extraction fails. This is a significant UX change from silent failures.

IMPORTANT

Critical Missing Function The 
db_service.py
 has 
deduct_credits()
 but NO refund_credits() function. We must create an idempotent refund system to prevent double refunds and ensure audit trail.

CAUTION

LLM Model Name Issue The log shows errors for gemini-2.0-flash-exp, but 
llm_factory.py
 uses gemini-2.5-flash-image for images. The TEXT model reference must be configured elsewhere (likely via env vars or config files). Need to locate and fix.

Proposed Changes
Phase 1: Critical Model Fix (P0 - Immediate)
[MODIFY] 
llm_factory.py
Changes:

Update 
get_model_name()
 to return gemini-2.5-flash for text generation (not just image)
Add fallback model chain: Gemini → GPT-4o-mini → GPT-3.5-turbo
Create generate_content_json_with_fallback() that tries multiple models
Log which model tier was used in metadata
Reasoning: The current implementation only has single model per provider. We need multi-model fallback to handle model deprecation and API failures.

Phase 2: Credit Refund System (P0)
[MODIFY] 
db_service.py
New Method:

python
def refund_credits(self, user_id: str, amount: int, reason: str, run_id: str) -> bool:
    """
    Refunds credits to user with idempotency check.
    Returns True if refund processed, False if already refunded.
    """
Changes:

Add refund_credits() method with transaction safety
Store refund record in refunds collection for audit trail
Check for duplicate refunds using run_id as idempotency key
Log refund event
Phase 3: Visual DNA Failure Detection (P0)
[MODIFY] 
visual_dna.py
Current Behavior:

python
except Exception as e:
    print(f"Error extracting Visual DNA: {e}")
    # Fallback to a basic template if API fails
    return { "character": {"description": "Generic creator"}, ... }
New Behavior:

python
except Exception as e:
    print(f"Error extracting Visual DNA: {e}")
    # NO FALLBACK - raise exception to trigger pipeline failure
    raise PipelineFailureException(
        stage="visual_dna",
        reason=str(e),
        user_message="❌ Failed to analyze product image. Your credits have been refunded.",
        requires_refund=True
    )
Post-exception Handler (in 
workflow.py
):

Catch PipelineFailureException
Call db_service.refund_credits()
Send WebSocket failure notification
Mark run as failed in Firestore with failure_reason
Stop pipeline execution
Phase 4: Script Generation Fallback (P0)
[MODIFY] 
script_generation.py
Current Fallback:

python
except Exception as e:
    return {
        "script": "Experience the ultimate upgrade...",
        "scenes": [
            {"id": "Hook", "description": "Product shot in bright light (Fallback)"},
            ...
        ]
    }
New Multi-Model Fallback:

python
def generate_script_and_shots(...):
    models = [
        ("gemini-2.5-flash", "primary"),
        ("gpt-4o-mini", "backup"),
        ("gpt-3.5-turbo", "fallback")
    ]
    
    for model, tier in models:
        try:
            data = generate_content_json_with_fallback(...)
            if validate_script_quality(data):
                return {..., "model_used": model, "tier": tier}
        except:
            continue
    
    # All models failed - raise pipeline failure
    raise PipelineFailureException(...)
Phase 5: Celebrity Filter Pre-Flight Check (P0)
[NEW] 
face_detection.py
Purpose: Detect faces in uploaded images BEFORE credit deduction to warn about Veo celebrity filter rejections.

Dependencies:

opencv-python (cv2)
Haar Cascade model (built-in with OpenCV)
Function:

python
def pre_flight_image_check(image_path: str) -> dict:
    """
    Returns:
    {
        "safe_to_proceed": bool,
        "warnings": [
            {
                "severity": "high",
                "code": "FACES_DETECTED",
                "message": "2 face(s) detected. Veo may reject this image.",
                "recommendation": "Use product-only image or illustration"
            }
        ]
    }
    """
Phase 6: Workflow Exception Handling (P0)
[MODIFY] 
workflow.py
New Exception Class:

python
class PipelineFailureException(Exception):
    def __init__(self, stage, reason, user_message, requires_refund=True):
        self.stage = stage
        self.reason = reason
        self.user_message = user_message
        self.requires_refund = requires_refund
Workflow Error Handler:

python
try:
    result = run_pipeline(state)
except PipelineFailureException as e:
    # Refund credits
    if e.requires_refund:
        db_service.refund_credits(
            user_id=state["user_id"],
            amount=state["credits_charged"],
            reason=f"{e.stage}: {e.reason}",
            run_id=state["run_id"]
        )
    
    # Save failed run
    db_service.save_run(
        run_id=state["run_id"],
        user_id=state["user_id"],
        status="failed",
        failure_reason=e.user_message
    )
    
    # Notify user via WebSocket
    send_websocket_event(state["run_id"], {
        "status": "failed",
        "stage": e.stage,
        "message": e.user_message,
        "refunded": e.requires_refund
    })
    
    raise  # Re-raise to stop execution
Phase 7: Quality Degradation Tracking (P1)
[MODIFY] 
scene_generation.py
Track Fallback Usage:

python
# After each scene generation, record fallback type
state["scenes_metadata"] = state.get("scenes_metadata", [])
state["scenes_metadata"].append({
    "scene_id": scene["id"],
    "method": "veo-3.1" | "ken-burns",  
    "fallback_reason": "celebrity_detected" | "rate_limit" | None
})
# Calculate degradation percentage
ken_burns_count = sum(1 for s in state["scenes_metadata"] if s["method"] == "ken-burns")
degradation_pct = (ken_burns_count / total_scenes) * 100
if degradation_pct > 50:
    # Trigger quality degradation notification
    send_quality_warning(run_id, scenes_metadata, degradation_pct)
Phase 8: Update Environment Configuration
[MODIFY] .env or 
brand/configuration.json
Issue: Need to locate where gemini-2.0-flash-exp is configured since it's not in 
llm_factory.py

Action:

Search for LLM_MODEL env var or config files
Update to gemini-2.5-flash
Remove any hardcoded references to experimental models
Verification Plan
Automated Tests
1. Credit Refund Function Test
File: tests/test_db_service.py (create if doesn't exist)

bash
# Run test
cd projects/backend
pytest tests/test_db_service.py::test_refund_credits -v
Test Cases:

✅ Refund adds credits back to user account
✅ Duplicate refund for same run_id is idempotent (no double refund)
✅ Refund record is stored in refunds collection
✅ Audit trail includes timestamp, reason, run_id
2. Visual DNA Failure Test
File: tests/test_visual_dna.py

bash
# Mock LiteLLM to simulate model not found error
pytest tests/test_visual_dna.py::test_dna_extraction_failure -v
Expected:

Raises PipelineFailureException
Exception contains correct stage (
visual_dna
)
Exception has user-friendly message
3. Multi-Model Script Fallback Test
File: tests/test_script_generation.py

bash
pytest tests/test_script_generation.py::test_multimodel_fallback -v
Test Cases:

✅ Primary model (Gemini) fails → Tries GPT-4o-mini
✅ GPT-4o-mini fails → Tries GPT-3.5-turbo
✅ All models fail → Raises PipelineFailureException
✅ Metadata includes which model tier was used
4. Face Detection Test
File: tests/test_face_detection.py

bash
pytest tests/test_face_detection.py::test_celebrity_detection -v
Test Images:

Image with 2 human faces → Returns warnings with FACES_DETECTED
Product-only image → Returns safe_to_proceed: true
Low resolution image (<512px) → Returns LOW_RESOLUTION warning
Manual Verification
TIP

Test Plan for Manual Validation After implementation, test the following scenarios manually:

Manual Test 1: Simulate Visual DNA Failure
Steps:

Temporarily modify 
llm_factory.py
 to force an exception:
python
def generate_content_json(...):
    raise Exception("Simulated API failure")
Start backend: python run.py
Create a new video via API or frontend
Expected Results:
✅ WebSocket receives status: "failed" message
✅ User sees "Credits refunded" notification
✅ Check Firestore: Run document has status: "failed" and failure_reason
✅ Check user_credits collection: Credits returned
✅ Check refunds collection: Refund record exists
Manual Test 2: Verify Face Detection Warning
Steps:

Upload image with human face (e.g., selfie, stock photo with person)
Submit video generation request
Expected Results:
✅ Frontend shows warning modal: "⚠️ Face detected - video may be rejected"
✅ User can click "Proceed Anyway" to continue
✅ NO credits deducted until user confirms
Manual Test 3: Quality Degradation Notification
Steps:

Generate video where 3/4 scenes fail Veo (use image with faces to trigger celebrity filter)
Wait for Ken Burns fallback to generate
Expected Results:
✅ Frontend shows "Quality Reduced" modal
✅ Modal lists which scenes used static animations
✅ User can choose: Accept / Retry / Refund
Test Discovery
I need to check if there are existing tests before proceeding. Let me search for test files:

Search locations:

projects/backend/tests/ or tests/
execution/tests/
Look for pytest.ini or conftest.py
Action Required: Before writing implementation plan, I should discover existing test infrastructure.

Rollout Strategy
Feature Flag: ENABLE_GRACEFUL_FAILURES (default: false for Week 1)
Gradual Rollout:
Week 1: 10% of users
Week 2: 50% if refund rate < 10%
Week 3: 100% if metrics stable
Rollback Plan: If refund rate > 20%, disable feature flag and investigate
Success Metrics
After 7 days of 100% rollout:

 Credit waste rate < 5% (users charged for failed/low-quality videos)
 Pipeline success rate > 95% (no generic fallback DNA/scripts)
 Graceful failure rate = 100% (refund + notification for all failures)
 Celebrity filter pre-detection > 90% (warned before generation)
 User complaints about "worthless videos" → 0
Next Steps
✅ Review this implementation plan
User Decision: Approve plan or request changes
Discover existing test infrastructure
Implement Phase 1-6 in order
Write/update tests
Test manually with all 3 scenarios
Deploy with feature flag
Monitor metrics