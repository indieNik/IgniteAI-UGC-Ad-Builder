import sys
import os
import uuid
import time
import json
import glob
import shutil
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
import logging
from projects.backend.schemas import GenerateRequest, GenerateResponse, RegenerateSceneRequest
from fastapi import Depends
from projects.backend.dependencies import get_current_user
from projects.backend.services.db_service import db_service
from projects.backend.services.storage_service import storage_service
from projects.backend.services.throttling_service import throttling_service
from projects.backend.services.email_service import email_service

def _upload_asset(local_path: str, run_id: str) -> str:
    """Helper to upload asset to firebase storage under the run directory."""
    filename = os.path.basename(local_path)
    destination = f"runs/{run_id}/{filename}"
    return storage_service.upload_file(local_path, destination)


def calculate_credit_cost(config: dict) -> int:
    """
    Credit cost calculation based on scene count and features.
    
    Proprietary pricing algorithm (abstracted for hackathon submission).
    Actual implementation includes:
    - Per-scene base cost
    - Feature multipliers (background, voice quality, resolution)
    - Dynamic pricing based on model selection
    """
    num_scenes = config.get("num_scenes", 3)
    # Proprietary cost calculation - protected
    base_cost = num_scenes * 2
    
    # Feature-based adjustments (actual algorithm hidden)
    features = config.get("features", {})
    extra_cost = len([f for f in features.values() if f]) if features else 0
        
    return base_cost + extra_cost

def calculate_estimated_cogs(config: dict) -> float:
    """
    Calculate estimated COGS (Cost of Goods Sold) in USD.
    
    Proprietary cost estimation algorithm (abstracted for hackathon submission).
    Actual implementation includes:
    - Multi-tier API costs (Gemini, OpenAI, Veo, etc)
    - Infrastructure costs per generation
    - Dynamic pricing based on model selection and feature usage
    """
    num_scenes = config.get("num_scenes", 3)
    
    # Proprietary COGS calculation - protected
    base_cogs = num_scenes * 0.50
    
    # Feature-based cost adjustments (actual algorithm hidden)
    features = config.get("features", {})
    feature_cogs = len([f for f in features.values() if f]) * 0.10 if features else 0
        
    return round(base_cogs + feature_cogs, 2)


# sys.path modification and build_graph import moved inside run_pipeline_task
# to prevent heavy imports at startup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store
run_status: Dict[str, str] = {}
run_results: Dict[str, Any] = {}

class FileLogger:
    """Redirects writes to a file and the original stream."""
    def __init__(self, filepath, stream):
        self.file = open(filepath, 'a', buffering=1)
        self.stream = stream
        self.closed = False

    def write(self, data):
        if not self.closed:
            try:
                self.file.write(data)
            except ValueError:
                # File already closed, skip file write but continue to stream
                pass
        self.stream.write(data)

    def flush(self):
        if not self.closed:
            try:
                self.file.flush()
            except ValueError:
                # File already closed, skip
                pass
        self.stream.flush()

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                self.file.close()
            except:
                pass

# Removed save_run_status


# Removed load_run_status_from_disk

def run_pipeline_task(run_id: str, request: GenerateRequest, user_id: str = None, credits_used: int = 0):
    session_dir = f"tmp/{run_id}"
    log_file = os.path.join(session_dir, "run.log")
    
    # Redirect stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        db_service.save_run(run_id, user_id, "running")
        
        # Ensure session directory exists for logging
        os.makedirs(session_dir, exist_ok=True)
        
        # Setup Logger
        file_logger = FileLogger(log_file, original_stdout)

        sys.stdout = file_logger
        sys.stderr = file_logger
        
        print(f"--- Starting Run {run_id} ---")
        
        # Lazy load execution modules to prevent startup blocking
        # Add the root directory to sys.path to allow importing from execution
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
        from execution.workflow import build_graph

        app = build_graph()
        
        # Check if we have an uploaded product image in the session dir
        uploaded_image_path = os.path.join(session_dir, "product.png")
        product_image = uploaded_image_path if os.path.exists(uploaded_image_path) else request.product_image_path
        
        # --- PATH SANITIZATION FIX: Aggressively handle legacy /app/ paths ---
        if product_image and isinstance(product_image, str) and product_image.startswith("/app/"):
            # Strip /app/ always if it doesn't exist
            if not os.path.exists(product_image):
                 stripped = product_image.replace("/app/", "", 1)
                 # Force resolution to PROJECT ROOT 'tmp', not cwd/tmp
                 # Assuming project root is 3 levels up from this router or we just use absolute path logic
                 # Safer: Use the known project root from sys.path or relative to this file
                 # Based on file structure: projects/backend/routers/generation.py
                 # We want to point to: projects/backend/tmp
                 backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                 if stripped.startswith("tmp/"):
                     # If striped path is tmp/run_123, and we want projects/backend/tmp/run_123
                     product_image = os.path.join(backend_root, stripped)
                 else:
                     product_image = os.path.abspath(stripped)

                 print(f"DEBUG: Sanitized legacy /app/ path to: {product_image}")

        # Ensure path is absolute for the execution layer
        if product_image and not os.path.isabs(product_image):
            product_image = os.path.abspath(product_image)



        # Load Base Config from Disk
        base_config = {}
        config_path = os.path.abspath(os.path.join(os.getcwd(), "brand/configuration.json"))
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    base_config = json.load(f)
                print(f"Loaded base config from {config_path}")
            except Exception as e:
                print(f"Failed to load base config: {e}")
        
        # Merge Request Config (Frontend Overrides)
        final_config = base_config.copy()
        if request.config:
            final_config.update(request.config)
            
        # Merge Brand Config (Visual DNA Persistence)
        if user_id:
            brand = db_service.get_brand(user_id)
            if brand:
                print(f"Applying Brand DNA for user {user_id}")
                final_config["brand"] = brand
                
        # Update state and start
        print(f"\n{'='*80}")
        print(f"🚀 PIPELINE STARTING - Run ID: {run_id}")
        print(f"{'='*80}")
        print(f"User ID: {user_id}")
        print(f"Prompt: {request.prompt[:200] if request.prompt else 'N/A'}...")
        print(f"Product Image: {product_image}")
        print(f"Credits Charged: {credits_used}")
        print(f"Final Config Keys: {list(final_config.keys())}")
        print(f"{'='*80}\n")
        
        initial_state = {
            "input_data": request.prompt,
            "product_image_path": product_image,
            "run_id": run_id,
            "session_output_dir": session_dir,
            "config": final_config,
            "user_id": user_id,
            "credits_charged": credits_used,  # ← CRITICAL: Track for refund system
            "regenerate_scene_id": final_config.get("regenerate_scene_id"),
            # PERSISTENCE: Restore previous results if provided (Regeneration path)
            "visual_dna": final_config.get("visual_dna"),
            "script": final_config.get("script"),
            "scenes_list": final_config.get("scenes_list"),
            "scene_paths": final_config.get("existing_scene_paths", []),
            "remote_assets": final_config.get("remote_assets", {}),
            "history": final_config.get("history", [])
        }

        print(f"📋 Initial State Keys: {list(initial_state.keys())}\n")



        
        print(f"⚙️  INVOKING LANGGRAPH WORKFLOW...\n")
        result = app.invoke(initial_state)
        
        print(f"\n✅ WORKFLOW COMPLETED SUCCESSFULLY")
        print(f"Result Type: {type(result)}")
        print(f"Result Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        print(f"{'='*80}\n")
        
        # Update DB with result
        # Serialize result if needed (be careful with non-serializable objects)
        final_result = result if isinstance(result, dict) else {"raw": str(result)}
        
        # --- UPLOAD TO CLOUD STORAGE ---
        # Find the final video in the result string or known path
        try:
            # Simple heuristic: Look for .mp4 in the result string or assume it's in session_dir
            # Better approach: Check session_dir for the newest .mp4
            if os.path.exists(session_dir):
                files = [f for f in os.listdir(session_dir) if f.endswith(".mp4")]
                if files:
                    # Sort by mtime to get the latest
                    files.sort(key=lambda x: os.path.getmtime(os.path.join(session_dir, x)), reverse=True)
                    latest_video = files[0]
                    local_video_path = os.path.join(session_dir, latest_video)
                    
                    from projects.backend.services.storage_service import storage_service
                    
                    # 1. Zip full assets (Logs + Images + Video)
                    zip_base_name = f"tmp/{run_id}_assets"
                    zip_path = shutil.make_archive(zip_base_name, 'zip', session_dir)
                    
                    # 2. Upload Zip
                    zip_dest = f"runs/{run_id}/assets.zip"
                    assets_url = storage_service.upload_file(zip_path, zip_dest)
                    print(f"Uploaded assets zip to: {assets_url}")
                    final_result["assets_url"] = assets_url

                    # 3. Upload Video
                    destination_path = f"runs/{run_id}/{latest_video}"
                    public_url = storage_service.upload_file(local_video_path, destination_path)
                    
                    print(f"Uploaded video to: {public_url}")
                    final_result["video_url"] = public_url
                    
                    # VERSION HISTORY LOGIC
                    # We append to 'video_history' so we don't lose previous gens
                    video_history = final_result.get("video_history") or []
                    # Avoid duplicates
                    if not video_history or video_history[-1] != public_url:
                        video_history.append(public_url)
                    final_result["video_history"] = video_history
                    
                    # 4. Upload Log (God Mode)
                    sys.stdout.flush() # Ensure logs are written
                    log_url = storage_service.upload_log(log_file, f"runs/{run_id}/run.log")
                    if log_url:
                        print(f"Uploaded run log to: {log_url}")
                        final_result["log_url"] = log_url

        except Exception as upload_err:
            print(f"Error uploading assets: {upload_err}")
            # Don't fail the run, just log it
            
        cogs = calculate_estimated_cogs(final_result.get("config", {}))
        db_service.save_run(run_id, user_id, "completed", final_result, cost=cogs)
        print("--- Run Completed ---")
        
        # --- SEND EMAIL NOTIFICATION (Completion) ---
        try:
            user_data = db_service.get_user_profile(user_id)
            user_email = user_data.get("email") if user_data else None
            user_name = user_data.get("name", "there") if user_data else "there"
            
            if user_email:
                # Calculate generation time
                import time
                generation_time = "N/A"
                if final_result.get("config", {}).get("start_time"):
                    elapsed = int(time.time() - final_result["config"]["start_time"])
                    minutes = elapsed // 60
                    seconds = elapsed % 60
                    generation_time = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
                
                project_name = final_result.get("config", {}).get("project_title", request.prompt[:50] if hasattr(request, 'prompt') else "Your project")
                
                email_service.send_generation_completed(
                    user_email=user_email,
                    user_name=user_name,
                    run_id=run_id,
                    project_name=project_name,
                    video_url=final_result.get("video_url", ""),
                    stats={
                        "duration": "15s",
                        "scenes": 4,
                        "generation_time": generation_time,
                        "credits_used": 10
                    }
                )
                print(f"Completion email sent to {user_email}")
        except Exception as email_err:
            print(f"Error sending completion email: {email_err}")
        
        # --- SEND PUSH NOTIFICATION ---
        try:
            from projects.backend.firebase_setup import send_notification
            
            # Extract first scene image URL for notification
            first_scene_image = None
            if final_result.get("remote_assets"):
                # Try to get Hook image first, then any other scene
                remote_assets = final_result["remote_assets"]
                print(f"====== DEBUG: remote_assets keys: {list(remote_assets.keys())}")
                first_scene_image = (
                    remote_assets.get("Hook_image") or
                    remote_assets.get("Hook") or
                    remote_assets.get("Feature_image") or
                    remote_assets.get("Feature") or
                    next((v for k, v in remote_assets.items() if "_image" in k or k in ["Hook", "Feature", "CTA"]), None)
                )
                print(f"====== DEBUG: first_scene_image extracted: {first_scene_image}")
            
            # Fallback to first scene from scene_paths if available
            if not first_scene_image and final_result.get("scene_paths"):
                scene_paths = final_result["scene_paths"]
                if scene_paths and len(scene_paths) > 0:
                    print(f"====== DEBUG: No remote asset found, scene_paths available: {list(scene_paths.keys())}")
                    # This would be a local path, we'd need the remote URL
                    # For now, skip if no remote asset available
                    pass
            
            # Get project title or use run_id
            project_title = None
            if final_result.get("config"):
                project_title = final_result["config"].get("project_title")
            
            notification_body = project_title or f"Run {run_id}"
            click_url = f"/campaigns/{run_id}"
            
            send_notification(
                user_id=user_id,
                title="Your video is ready! 🎬",
                body=notification_body,
                image_url=first_scene_image,
                click_action=click_url,
                run_id=run_id
            )
            print(f"Push notification sent to user {user_id}")
        except Exception as notif_err:
            print(f"Error sending push notification: {notif_err}")
            # Don't fail the run if notification fails
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        error_data = {"error": str(e)}
        
        # Upload Log on Failure too
        try:
             sys.stdout.flush()
             log_url = storage_service.upload_log(log_file, f"runs/{run_id}/run.log")
             if log_url:
                 error_data["log_url"] = log_url
        except:
            pass
            
        db_service.save_run(run_id, user_id, "failed", error_data)
        logger.error(f"Run {run_id} failed: {e}")
        
        # --- SEND EMAIL NOTIFICATION (Failure) ---
        try:
            user_data = db_service.get_user_profile(user_id)
            user_email = user_data.get("email") if user_data else None
            user_name = user_data.get("name", "there") if user_data else "there"
            
            if user_email:
                project_name = "Your project"
                if hasattr(request, 'prompt'):
                    project_name = request.prompt[:50]
                elif hasattr(request, 'config') and request.config:
                    project_name = request.config.get("project_title", "Your project")
                
                # Determine credits to refund
                credits_refunded = 2 if (hasattr(request, 'config') and request.config and request.config.get("regenerate_scene_id")) else 10
                
                # Get new balance
                new_balance = db_service.get_credits(user_id)
                
                email_service.send_generation_failed(
                    user_email=user_email,
                    user_name=user_name,
                    run_id=run_id,
                    project_name=project_name,
                    error_message=str(e),
                    credits_refunded=credits_refunded,
                    new_balance=new_balance
                )
                print(f"Failure email sent to {user_email}")
        except Exception as email_err:
            print(f"Error sending failure email: {email_err}")
        
        # --- REFUND LOGIC: If regeneration fails early, refund credits ---
        if request.config and request.config.get("regenerate_scene_id"):
            REGEN_COST = 3  # Match regenerate_scene_id cost
            print(f"Refunding {REGEN_COST} credits for failed regeneration.")
            db_service.add_credits(user_id, REGEN_COST)
            db_service.track_event(user_id, "regeneration_refunded", {"run_id": run_id, "reason": str(e)})

    finally:

        # Restore streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        try:
            file_logger.close()
        except:
            pass


@router.post("/upload")
async def upload_asset(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        # Generate Run ID here
        run_id = f"run_{int(time.time())}"
        session_dir = f"tmp/{run_id}"
        os.makedirs(session_dir, exist_ok=True)
        
        # Save as product.png always
        filename = "product.png"
        file_location = os.path.join(session_dir, filename)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # --- PERSISTENCE FIX: Upload "Source Image" to Firebase Immediately ---
        remote_url = _upload_asset(file_location, run_id=run_id)
        
        # Save preliminary run record to DB so Library can see it immediately
        # We store the remote URL in a standardized field key
        initial_data = {
            "status": "draft",
            "timestamp": int(time.time()),
            "result": {
                "source_image_url": remote_url
            }
        }
        db_service.save_run(run_id, user['uid'], "draft", initial_data["result"])
            
        return {
            "run_id": run_id, 
            "filename": filename, 
            "path": os.path.abspath(file_location),
            "remote_url": remote_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=GenerateResponse)
async def trigger_generation(request: GenerateRequest, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    # Use provided run_id (from upload) or create new
    if request.config and "run_id" in request.config:
        run_id = request.config["run_id"]
    else:
        run_id = f"run_{int(time.time())}"
        
    # Ensure dir exists
    session_dir = f"tmp/{run_id}"
    os.makedirs(session_dir, exist_ok=True)
    
    # --- ANTI-SPAM: THROTTLING CHECKS ---
    user_id = user.get("uid")
    user_email = user.get("email")
    
    # 1. Check user cooldown (2 minutes between generations)
    user_cooldown = throttling_service.check_user_cooldown(user_id)
    if user_cooldown is not None:
        minutes = user_cooldown // 60
        seconds = user_cooldown % 60
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {minutes}m {seconds}s before starting another generation. This prevents system overload."
        )
    
    # 2. Check global throttle (30 seconds between ANY generation)
    global_throttle = throttling_service.check_global_throttle()
    if global_throttle is not None:
        raise HTTPException(
            status_code=429,
            detail=f"System is processing another request. Please wait {global_throttle} seconds. This ensures API compliance."
        )
    
    # --- PRODUCTION SECURITY: CREDIT CHECK ---
    COST_PER_GEN = calculate_credit_cost(request.config or {})
    
    # Check if user is an admin
    is_admin = db_service.get_user_role(user_email) == "admin"
    msg_prefix = ""

    if not is_admin:
        # 1. Check if user has enough credits
        balance = db_service.get_credits(user_id)
        if balance < COST_PER_GEN:
            raise HTTPException(
                status_code=402, 
                detail=f"Insufficient balance. You have {balance} credits, but {COST_PER_GEN} credits are required for this generation."
            )

        # 2. Transactally deduct credits
        success = db_service.deduct_credits(user_id, COST_PER_GEN)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process credits. Please try again.")
        
        msg_prefix = f"Success! {COST_PER_GEN} credits deducted. "
    else:
        # Track admin usage for audit
        db_service.track_event(user_id, "admin_generation_bypass", {
            "run_id": run_id,
            "email": user_email,
            "timestamp": time.time(),
            "prompt": request.prompt[:100] if request.prompt else "N/A",
            "estimated_cogs": COST_PER_GEN * 0.40  # Track subsidy cost
        })
        print(f"Admin Bypass: User {user_email} is generating for free.")
        msg_prefix = "Success! Administrative privileges active. "

    # --- RECORD GENERATION START (for throttling) ---
    throttling_service.record_generation(user_id)
    
    # --- START GENERATION ---
    # Store initial status
    db_service.save_run(run_id, user_id, "queued", request_data=request.dict(), credits_used=COST_PER_GEN)
    
    # --- SEND EMAIL NOTIFICATION (Generation Started) ---
    try:
        user_data = db_service.get_user_profile(user_id)
        user_email = user_data.get("email") if user_data else None
        user_name = user_data.get("name", "there") if user_data else "there"
        
        if user_email:
            project_name = request.config.get("project_title", request.prompt[:50]) if request.config else request.prompt[:50]
            new_balance = db_service.get_credits(user_id)
            
            # Store start time for generation time calculation
            if not request.config:
                request.config = {}
            request.config["start_time"] = time.time()
            
            email_service.send_generation_started(
                user_email=user_email,
                user_name=user_name,
                run_id=run_id,
                project_name=project_name,
                credits_deducted=COST_PER_GEN,
                new_balance=new_balance,
                estimated_time="3-5 minutes"
            )
            print(f"Generation started email sent to {user_email}")
    except Exception as email_err:
        print(f"Error sending generation started email: {email_err}")
    
    # --- SEND START NOTIFICATION ---
    try:
        from projects.backend.firebase_setup import send_notification
        
        # Get project title or use default
        project_title = None
        if request.config:
            project_title = request.config.get("project_title")
        
        notification_body = project_title or "Your video"
        
        send_notification(
            user_id=user_id,
            title="🎬 Video generation started!",
            body=f"Creating {notification_body}... We'll notify you when it's ready!",
            click_action=f"/campaigns/{run_id}",
            run_id=run_id
        )
        print(f"Start notification sent to user {user_id}")
    except Exception as notif_err:
        print(f"Error sending start notification: {notif_err}")
        # Don't fail the generation if notification fails
    
    # Start background task
    background_tasks.add_task(run_pipeline_task, run_id, request, user_id, COST_PER_GEN)
    
    return GenerateResponse(
        run_id=run_id, 
        status="queued", 
        message=f"{msg_prefix}Generation started."
    )

@router.get("/status/{run_id}")
async def get_status(run_id: str):
    # Check for intermediate assets
    assets = {}
    
    # 1. Check DB for Persistent Assets (Real-time Uploads)
    db_run = db_service.get_run(run_id)
    current_status = "unknown"
    current_result = None
    
    if db_run:
        current_status = db_run.get("status", "unknown")
        
        # --- ROBUSTNESS: ZOMBIE CHECK ---
        # If run is "running" or "queued" but outdated (>2 hours), mark as failed
        # This prevents infinite polling on frontend
        TIMEOUT_THRESHOLD = 1800 # 30 minutes (increased to allow longer multi-scene generations)
        updated_at = db_run.get("updated_at", 0)
        
        if current_status in ["running", "queued"] and (time.time() - updated_at > TIMEOUT_THRESHOLD):
            print(f"👻 Zombie Run Detected: {run_id}. Marking as failed.")
            current_status = "failed"
            failure_reason = "Execution timed out (Zombie Run)"
            
            # --- FAILURE RECOVERY: Try to save logs/assets before killing ---
            recovered_data = {"error": failure_reason}
            zombie_session_dir = f"tmp/{run_id}"
            
            if os.path.exists(zombie_session_dir):
                print(f"Attemping to salvage assets for zombie run {run_id}...")
                try:
                    # 1. Recover Log
                    zombie_log_file = os.path.join(zombie_session_dir, "run.log")
                    if os.path.exists(zombie_log_file):
                        log_url = storage_service.upload_log(zombie_log_file, f"runs/{run_id}/run.log")
                        if log_url:
                             print(f"Salvaged run log: {log_url}")
                             recovered_data["log_url"] = log_url
                    
                    # 2. Recover Assets (Zip)
                    # Create zip in tmp (parent) to avoid recursive zipping if we zipped inside
                    zip_base_name = f"tmp/{run_id}_zombie_assets"
                    zip_path = shutil.make_archive(zip_base_name, 'zip', zombie_session_dir)
                    
                    zip_dest = f"runs/{run_id}/assets_salvaged.zip"
                    assets_url = storage_service.upload_file(zip_path, zip_dest)
                    if assets_url:
                        print(f"Salvaged assets zip: {assets_url}")
                        recovered_data["assets_url"] = assets_url
                        
                except Exception as salvage_err:
                    print(f"Failed to salvage zombie assets: {salvage_err}")

            # Update DB source of truth
            db_run["status"] = "failed"
            db_run["failure_reason"] = failure_reason
            
            # Merge recovered data into existing result or create new
            final_result = db_run.get("result") or {}
            final_result.update(recovered_data)
            db_run["result"] = final_result

            db_service.save_run(run_id, db_run.get("user_id"), "failed", result=final_result, failure_reason=failure_reason)
            
            # Continue to return failed status so frontend stops polling
            
        current_result = db_run.get("result")
        
        if current_result and isinstance(current_result, dict):
            remote_assets = current_result.get("remote_assets", {})
            if remote_assets:
                # Map standardized keys if needed, or just pass through
                # Frontend expects "Hook", "Feature", etc.
                # remote_assets keys are "Hook_image", "Hook_video", etc.
                # We can map them.
                for key, url in remote_assets.items():
                    # e.g. key="Hook_image" -> assets["Hook_image"] = url
                    assets[key] = url
                    
                    # For backward compatibility / simple display in frontend which might expect "Hook" checks
                    # Frontend logic: *ngIf="sceneAssets['Hook']" (it expects the image path usually?)
                    # Let's see frontend logic: 
                    # <img [src]="getAssetUrl(sceneAssets[scene.id])" ...>
                    # scene.id is "Hook". 
                    # So we need assets["Hook"] to be the image URL.
                    if key.endswith("_image"):
                        scene_name = key.replace("_image", "")
                        assets[scene_name] = url
    
    # 2. Overlay Local Assets (if surviving/available)
    session_dir = f"tmp/{run_id}"
    if os.path.exists(session_dir):
        # We expect files like "0_Hook_image.png" or "Hook_image.png"
        for filename in os.listdir(session_dir):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                # Only add if not already present from cloud (Cloud is SSoT)
                if "Hook" in filename and "Hook" not in assets: assets["Hook"] = f"/outputs/{run_id}/{filename}"
                elif "Feature" in filename and "Feature" not in assets: assets["Feature"] = f"/outputs/{run_id}/{filename}"
                elif "Lifestyle" in filename and "Lifestyle" not in assets: assets["Lifestyle"] = f"/outputs/{run_id}/{filename}"
                elif "CTA" in filename and "CTA" not in assets: assets["CTA"] = f"/outputs/{run_id}/{filename}"

    return {
        "run_id": run_id,
        "status": current_status,
        "result": current_result,
        "assets": assets
    }

@router.get("/history")
async def get_history(user: dict = Depends(get_current_user)):
    """List past runs sorted by timestamp (newest first)."""
    history = []
    """List past runs from Firestore."""
    history = db_service.get_user_history(user['uid'])
    return history

@router.websocket("/ws/logs/{run_id}")
async def websocket_logs(websocket: WebSocket, run_id: str):
    # WebSocket authentication - extract token from query params
    # Frontend should connect with: ws://host/api/ws/logs/{run_id}?token={firebase_token}
    await websocket.accept()
    
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.send_text("Error: Authentication token required")
            await websocket.close(code=1008, reason="No token provided")
            return
        
        # Verify Firebase token manually
        from projects.backend.firebase_setup import verify_token
        try:
            user = verify_token(token)
        except Exception as auth_error:
            await websocket.send_text(f"Error: Authentication failed - {str(auth_error)}")
            await websocket.close(code=1008, reason="Invalid token")
            return
    
        # AUTHORIZATION: Verify user owns this run
        db_run = db_service.get_run(run_id)
        if not db_run:
            await websocket.send_text("Error: Run not found")
            await websocket.close(code=1008, reason="Run not found")
            return
        
        if db_run.get("user_id") != user.get("uid"):
            await websocket.send_text("Error: Unauthorized access to this run")
            await websocket.close(code=1008, reason="Unauthorized")
            logger.warning(f"Unauthorized log access attempt: User {user.get('uid')} tried to access run {run_id} owned by {db_run.get('user_id')}")
            return
        
        log_path = f"tmp/{run_id}/run.log"
        
        # Wait for file to exist
        retries = 0
        while not os.path.exists(log_path):
            if retries > 20: # 10 seconds timeout
                await websocket.close()
                return
            await asyncio.sleep(0.5)
            retries += 1
            
        with open(log_path, "r") as f:
            # Go to end of file? Or start? Start is better.
            f.seek(0, 0)
            
            while True:
                line = f.readline()
                if line:
                    await websocket.send_text(line)
                else:
                    # Check if run is done
                    # First check memory
                    status = run_status.get(run_id)
                    
                    # If not in memory or unknown, check disk (persistence recovery)
                    if not status or status == "unknown":
                         db_run = db_service.get_run(run_id)
                         if db_run:
                             status = db_run.get("status")
                    
                    if status in ["completed", "failed"]:
                        # Send remaining buffer
                        remaining = f.read()
                        if remaining:
                            await websocket.send_text(remaining)
                        break
                    await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from logs {run_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

@router.get("/download/{run_id}")
async def download_run_assets(run_id: str, user: dict = Depends(get_current_user)):
    """Zips the run directory and returns it as a downloadable file."""
    
    # AUTHORIZATION: Verify user owns this run
    db_run = db_service.get_run(run_id)
    if not db_run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if db_run.get("user_id") != user.get("uid"):
        logger.warning(f"Unauthorized download attempt: User {user.get('uid')} tried to download run {run_id} owned by {db_run.get('user_id')}")
        raise HTTPException(status_code=403, detail="Unauthorized access to this run")
    
    session_dir = f"tmp/{run_id}"
    
    if not os.path.exists(session_dir):
        # Fallback: Check DB for cloud link
        if db_run.get("result", {}).get("assets_url"):
            return RedirectResponse(url=db_run["result"]["assets_url"])
            
        raise HTTPException(status_code=404, detail="Run not found or expired")
        
    # Create zip file in tmp (parent of session_dir)
    # We use shutil.make_archive
    zip_base_name = f"tmp/{run_id}_assets"
    zip_path = f"{zip_base_name}.zip"
    
    # Check if zip already exists to save time? 
    # Maybe not, as new assets might have been generated. Re-zipping is safer.
    
    try:
        shutil.make_archive(zip_base_name, 'zip', session_dir)
    except Exception as e:
        logger.error(f"Failed to zip assets for {run_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create asset archive")

    return FileResponse(
        path=zip_path, 
        filename=f"ignite_assets_{run_id}.zip",
        media_type='application/zip'
    )
@router.post("/regenerate-scene/{run_id}/{scene_id}")
async def regenerate_scene(run_id: str, scene_id: str, request: RegenerateSceneRequest, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    user_id = user.get("uid")
    REGEN_COST = 3  # Ensures 76% margin ($1.98 revenue vs $0.94 COGS)
    
    # --- ANTI-SPAM: THROTTLING CHECKS ---
    # 1. Check user cooldown (2 minutes - same as full generation)
    user_cooldown = throttling_service.check_user_cooldown(user_id)
    if user_cooldown is not None:
        minutes = user_cooldown // 60
        seconds = user_cooldown % 60
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {minutes}m {seconds}s before regenerating. This prevents system overload."
        )
    
    # 2. Check global throttle (30 seconds)
    global_throttle = throttling_service.check_global_throttle()
    if global_throttle is not None:
        raise HTTPException(
            status_code=429,
            detail=f"System is processing another request. Please wait {global_throttle} seconds."
        )
    
    # 1. Fetch existing run
    db_run = db_service.get_run(run_id)
    if not db_run:
        raise HTTPException(status_code=404, detail="Run not found.")
        
    if db_run.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this project.")

    # 2. Credit check
    balance = db_service.get_credits(user_id)
    if balance < REGEN_COST:
        raise HTTPException(status_code=402, detail=f"Insufficient credits for regeneration. Need {REGEN_COST}.")
    
    # 3. Deduct Credits
    success = db_service.deduct_credits(user_id, REGEN_COST)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to process credits.")

    # 4. Reconstruct State for Partial Run
    previous_result = db_run.get("result", {})
    previous_request = db_run.get("request", {})
    
    # Identify scene list and paths - it might be in 'result' (as LangGraph returns full state)
    scenes_list = previous_result.get("scenes_list") or []
    existing_scene_paths = previous_result.get("scene_paths") or []
    visual_dna = previous_result.get("visual_dna") or {}
    
    # --- FIX: Handle Stringified/Nested Visual DNA ---
    if isinstance(visual_dna, str):
        try:
             import json
             # Try to parse stringified JSON
             visual_dna = json.loads(visual_dna)
        except:
             print("Wrapper: Failed to parse stringified visual_dna")
             
    # Handle the specific "content": "```json..." case user reported
    if isinstance(visual_dna, dict) and "content" in visual_dna and isinstance(visual_dna["content"], str):
        try:
            raw_content = visual_dna["content"]
            # Strip markdown code blocks if present
            clean_content = raw_content.replace("```json", "").replace("```", "").strip()
            visual_dna = json.loads(clean_content)
            print("Wrapper: Successfully parsed nested visual_dna content")
        except Exception as e:
            print(f"Wrapper: Failed to parse nested visual_dna content: {e}")

    script = previous_result.get("script")
    remote_assets = previous_result.get("remote_assets") or {}
    history = previous_result.get("history") or []

    
    # 5. Trigger Background Task
    # We create a pseudo-request object that mimics the original
    from projects.backend.schemas import GenerateRequest
    regen_request = GenerateRequest(
        prompt=previous_request.get("prompt", ""),
        product_image_path=previous_request.get("product_image_path"),
        config=previous_request.get("config", {})
    )
    # Inject the regeneration flag and existing data into the config so our workflow sees it
    if not regen_request.config: regen_request.config = {}
    regen_request.config["regenerate_scene_id"] = scene_id
    if request.prompt:
        regen_request.config["regenerate_prompt"] = request.prompt

    regen_request.config["existing_scene_paths"] = existing_scene_paths
    regen_request.config["visual_dna"] = visual_dna
    regen_request.config["script"] = script
    regen_request.config["scenes_list"] = scenes_list
    regen_request.config["remote_assets"] = remote_assets
    regen_request.config["history"] = history

    
    # --- RECORD GENERATION START (for throttling) ---
    throttling_service.record_generation(user_id)
    
    db_service.save_run(run_id, user_id, "running")


    background_tasks.add_task(run_pipeline_task, run_id, regen_request, user_id)
    
    db_service.track_event(user_id, "scene_regenerated", {"run_id": run_id, "scene_id": scene_id})

    return {"status": "started", "message": f"Regenerating {scene_id}. {REGEN_COST} credits deducted."}

@router.post("/pre-flight-check")
async def pre_flight_check_endpoint(
    input_data: str,
    image_path: str = None,
    user: dict = Depends(get_current_user)
):
    """
    Pre-flight check for person/celebrity detection in text and image.
    Returns warnings and requires_confirmation flag to show modal before generation.
    """
    try:
        from execution.person_detection import pre_flight_check
        
        print(f"\n=== PRE-FLIGHT CHECK ===" )
        print(f"User: {user.get('uid')}")
        print(f"Input data: {input_data[:100] if input_data else 'None'}...")
        print(f"Image path: {image_path}")
        
        result = pre_flight_check(input_data or "", image_path)
        
        print(f"Pre-flight result: safe={result.get('safe_to_proceed')}, requires_confirmation={result.get('requires_confirmation')}")
        print(f"Warnings: {len(result.get('warnings', []))}")
        print(f"========================\n")
        
        return result
    except Exception as e:
        logger.error(f"Pre-flight check failed: {e}")
        # Return safe result on error - don't block user
        return {
            "safe_to_proceed": True,
            "requires_confirmation": False,
            "warnings": [{
                "code": "PREFLIGHT_ERROR",
                "severity": "low",
                "message": f"Pre-flight check failed: {str(e)}",
                "recommendation": "Proceeding without pre-flight validation."
            }],
            "has_person_detected": False
        }
