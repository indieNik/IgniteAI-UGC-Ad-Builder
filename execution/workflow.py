from __future__ import annotations
import os
import json
import time
from typing import TypedDict, Optional, List, Dict, Any
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END

# Imports from execution modules
from execution.visual_dna import extract_visual_dna
from execution.script_generation import generate_script_and_shots
from execution.scene_generation import generate_scene, generate_end_card, generate_character
from execution.voice_generation import generate_voice
from execution.assembly import assemble_video

# Dynamic DB Import Helper
def get_db_service():
    try:
        # Check if projects is in path (it is when running from backend)
        from projects.backend.services.db_service import db_service
        return db_service
    except (ImportError, ValueError) as e:
        # ValueError happens when Firebase is not initialized (standalone mode)
        # ImportError happens when projects module doesn't exist
        print(f"ℹ️  DB Service unavailable (standalone mode): {type(e).__name__}")
        return None

def handle_pipeline_failure(exception, state: AgentState):
    """
    Centralized handler for pipeline failures.
    Triggers credit refund, marks run as failed, and logs the error.
    """
    from execution.exceptions import PipelineFailureException
    
    # Check if this is our custom exception
    if not isinstance(exception, PipelineFailureException):
        # Wrap generic exceptions
        exception = PipelineFailureException(
            stage="unknown",
            reason=str(exception),
            user_message="❌ Video generation failed. Your credits have been refunded.",
            requires_refund=True
        )
    
    print(f"\n{'='*60}")
    print(f"⚠️  PIPELINE FAILURE DETECTED")
    print(f"{'='*60}")
    print(f"Stage: {exception.stage}")
    print(f"Reason: {exception.reason}")
    print(f"User Message: {exception.user_message}")
    print(f"Requires Refund: {exception.requires_refund}")
    print(f"{'='*60}\n")
    
    # Get DB service and user info
    db = get_db_service()
    user_id = state.get("user_id")
    run_id = state.get("run_id")
    
    if not db or not user_id or not run_id:
        print("⚠️  Cannot process refund - missing DB service or user info")
        return
    
    # Process refund if required
    if exception.requires_refund:
        # Determine credits to refund (this should come from the initial charge)
        # For now, we'll need to track this in state or retrieve from run document
        credits_charged = state.get("credits_charged", 0)
        
        if credits_charged > 0:
            print(f"Initiating refund of {credits_charged} credits...")
            refund_success = db.refund_credits(
                user_id=user_id,
                amount=credits_charged,
                reason=f"{exception.stage}: {exception.reason}",
                run_id=run_id
            )
            
            if refund_success:
                print(f"✅ Refund processed successfully")
            else:
                print(f"⚠️  Refund was not processed (may have already been refunded)")
        else:
            print("ℹ️  No credits to refund (credits_charged = 0)")
    
    # Mark run as failed in Firestore
    try:
        db.save_run(
            run_id=run_id,
            user_id=user_id,
            status="failed",
            result={
                "failure_stage": exception.stage,
                "failure_reason": exception.reason,
                "user_message": exception.user_message,
                "refunded": exception.requires_refund,
                "timestamp": time.time()
            }
        )
        print(f"✅ Run marked as failed in database")
    except Exception as e:
        print(f"⚠️  Failed to update run status: {e}")
    
    # TODO: Send WebSocket notification to frontend
    # This would require WebSocket service integration
    # For now, just log that it should happen
    print(f"TODO: Send WebSocket notification to user")

# Load environment variables
load_dotenv()

# Define the State
class AgentState(TypedDict):
    input_data: str
    user_id: Optional[str] # Added for DB updates
    product_image_path: Optional[str]
    character_image_path: Optional[str] # [NEW] Anchor Character
    visual_dna: Optional[dict]
    script: Optional[str]
    scenes_list: Optional[List[dict]]
    scene_paths: Optional[List[str]]
    audio_path: Optional[str]
    end_card_path: Optional[str]
    end_card_url: Optional[str] # Remote URL
    remote_assets: Optional[Dict[str, str]] # Map of asset_id -> cloud_url
    result: Optional[str]
    run_id: str
    session_output_dir: str
    config: Dict[str, Any]
    cost_usd: float # Total accumulated cost
    usage_details: Dict[str, Any] # Breakdown
    regenerate_scene_id: Optional[str] # If set, only this scene is processed
    history: List[Dict[str, Any]] # Version tracking for edits



# Define nodes
def extract_dna_node(state: AgentState):
    """Extract Visual DNA with graceful failure handling"""
    # Idempotency check for regeneration
    if state.get("visual_dna"):
        print("--- Using Persisted Visual DNA ---")
        return {"visual_dna": state["visual_dna"]}
    
    try:
        config = state.get("config", {})
        dna = extract_visual_dna(state["input_data"], image_path=state.get("product_image_path"), config=config)
        return {"visual_dna": dna}
    except Exception as e:
        # Handle graceful failure
        from execution.exceptions import PipelineFailureException
        handle_pipeline_failure(e, state)
        raise  # Re-raise to stop workflow


def generate_script_node(state: AgentState):
    """Generate script with graceful failure handling"""
    # Idempotency check for regeneration
    if state.get("scenes_list") and state.get("script"):
        print("--- Using Persisted Script & Shotlist ---")
        return {"script": state["script"], "scenes_list": state["scenes_list"]}

    try:
        print("--- Generating Script & Shotlist ---")
        config = state.get("config", {})
        data = generate_script_and_shots(state["input_data"], state["visual_dna"], config=config)

        # Calculate LLM Cost (Script Gen)
        from projects.backend.services.pricing_service import PricingService
        meta = data.get("usage_metadata", {}).get("usage", {})
        in_tokens = meta.get("input_tokens", 0)
        out_tokens = meta.get("output_tokens", 0)
        
        llm_cost = PricingService.calculate_llm_cost("gemini", in_tokens, out_tokens)
        
        # Update State Usage
        usage = state.get("usage_details", {})
        usage["llm_tokens_in"] = usage.get("llm_tokens_in", 0) + in_tokens
        usage["llm_tokens_out"] = usage.get("llm_tokens_out", 0) + out_tokens
        
        state["cost_usd"] = state.get("cost_usd", 0.0) + llm_cost
        state["usage_details"] = usage
        
        return {"script": data["script"], "scenes_list": data["scenes"], "cost_usd": state["cost_usd"], "usage_details": usage}
    except Exception as e:
        # Handle graceful failure
        from execution.exceptions import PipelineFailureException
        handle_pipeline_failure(e, state)
        raise  # Re-raise to stop workflow

def generate_character_node(state: AgentState):
    """
    Generates the Anchor Character.
    Skipped if we are only regenerating a specific scene (unless that scene needs character context update, but usually anchor is static).
    """
    # Idempotency / Skip if regenerating a specific scene (anchor should persist)
    if state.get("regenerate_scene_id") and state.get("character_image_path"):
         print("--- Skipping Character Gen (Regeneration Mode) ---")
         return {} # Keep existing
         
    if state.get("character_image_path"):
        print("--- Using Persisted Character Anchor ---")
        return {}

    print("--- Generating Character Anchor ---")
    config = state.get("config", {})
    visual_dna = state.get("visual_dna", {})
    output_dir = state.get("session_output_dir", "tmp")
    product_image = state.get("product_image_path")
    
    char_path, char_url = generate_character(visual_dna, config, output_dir, product_image)
    
    # Cost (Image Gen)
    from projects.backend.services.pricing_service import PricingService
    cost = PricingService.calculate_image_cost(config.get("image_model", "dall-e-3"), 1)
    
    # Remote Assets
    assets = state.get("remote_assets", {}) or {}
    assets["character_anchor"] = char_url
    
    return {
        "character_image_path": char_path,
        "remote_assets": assets,
        "cost_usd": state.get("cost_usd", 0.0) + cost
    }

def generate_scenes_node(state: AgentState):
    print("--- Generating Scenes (Parallel) ---")
    dna = state.get("visual_dna", {})
    scenes_to_process = state.get("scenes_list", [])
    output_dir = state.get("session_output_dir", "tmp")
    regen_id = state.get("regenerate_scene_id")
    
    # Fallback if script generation failed
    if not scenes_to_process:
        print("Warning: No scenes list found. Using fallback.")
        scenes_to_process = [
            {"id": "Hook", "description": "Hero shot of the product"},
            {"id": "Feature", "description": "Lifestyle shot of usage"},
            {"id": "Lifestyle", "description": "Close up product details"},
            {"id": "CTA", "description": "Call to action text overlay"}
        ]
    
    # Anchor Character logic
    character_anchor = state.get("character_image_path")
    if not character_anchor and not regen_id:
        print("Warning: No Character Anchor found. Scenes might lack consistency.")
        
    config = state.get("config", {})
    product_image = state.get("product_image_path")
    run_id = state.get("run_id", "unknown")
    user_id = state.get("user_id")
    db = get_db_service()

    # Shared State Accumulators
    accumulated_remote_assets = state.get("remote_assets", {}) or {}
    total_cost = state.get("cost_usd", 0.0)
    usage = state.get("usage_details", {}) or {}
    history = state.get("history", []) or []
    
    # Prepare result container (Pre-filled with None to maintain order)
    generated_videos_result = [None] * len(scenes_to_process)
    
    # Existing paths (for regeneration partial updates)
    existing_paths = state.get("scene_paths", [])
    if existing_paths and len(existing_paths) == len(scenes_to_process):
         generated_videos_result = list(existing_paths)

    # Helper function for parallel execution
    def process_single_scene(index, scene):
        scene_id = scene.get("id")
        
        # SKIP LOGIC (Regeneration)
        if regen_id and scene_id != regen_id:
            # If we already have a path for this index, keep it
            if index < len(existing_paths):
                return {
                    "index": index,
                    "skipped": True,
                    "video_path": existing_paths[index],
                    "remote_assets": {} # No new assets
                }
            return {"index": index, "skipped": True, "video_path": None}

        print(f"🚀 Launching Parallel Scene: {scene_id}")
        print(f"   📝 Scene Description: {scene.get('description', 'N/A')[:200]}...")
        print(f"   🎬 Scene Script: {scene.get('scene_script', 'N/A')[:200]}...")
        
        # Version History (only if actively generating)
        if regen_id and index < len(existing_paths):
             old_path = existing_paths[index]
             old_remote = accumulated_remote_assets.get(f"{scene_id}_image")
             old_video_remote = accumulated_remote_assets.get(f"{scene_id}_video")
             
             history_entry = {
                 "timestamp": time.time(),
                 "scene_id": scene_id,
                 "previous_local_path": old_path,
                 "previous_image_url": old_remote,
                 "previous_video_url": old_video_remote,
                 "reason": "user_regeneration"
             }
             history.append(history_entry)

        scene["run_id_ref"] = run_id
        
        # PERSIST REGENERATION INSTRUCTIONS
        # If this is the target scene and we have a new prompt, save it to 'modifications'
        if regen_id and scene_id == regen_id:
            new_prompt = config.get("regenerate_prompt")
            if new_prompt:
                mods = scene.get("modifications", [])
                # Avoid exact duplicates
                if not mods or mods[-1] != new_prompt:
                    mods.append(new_prompt)
                    scene["modifications"] = mods
                    print(f"   🔄 Persisted Modification for {scene_id}: {new_prompt}")

        print(f"   🔍 DEBUG: Full scene data keys: {list(scene.keys())}")
        
        # EXECUTION
        # Note: We pass 'character_anchor' as 'previous_scene_image' to enforce consistency
        # Optimization: If regenerating, we skip image gen if we want to keep the same shot? 
        # Actually for now, let's assume full regen of that scene.
        
        # Cost Tracking (Local to thread)
        local_cost = 0.0
        local_usage = {}
        
        try:
            video_path, image_path, scene_assets, stats = generate_scene(
                scene, 
                dna, 
                config=config, 
                output_dir=output_dir, 
                product_image_path=product_image,
                previous_scene_image=character_anchor, # STAR TOPOLOGY LINK
                skip_image_generation=False # Always generate fresh unless specifically optimized
            )
            
            # Calculate Cost
            from projects.backend.services.pricing_service import PricingService
            if stats.get("image_model"):
                img_cost = PricingService.calculate_image_cost(stats["image_model"], 1, config.get("aspect_ratio", "9:16"))
                local_cost += img_cost
                local_usage["images"] = 1
            
            if stats.get("video_duration", 0) > 0:
                vid_model = stats.get("video_model", "veo-3.1-fast-generate-preview")
                actual_dur = stats.get("video_duration", 0)
                vid_cost = PricingService.calculate_video_cost(vid_model, actual_dur)
                local_cost += vid_cost
                local_usage["video_seconds"] = actual_dur
                
            return {
                "index": index,
                "video_path": video_path,
                "remote_assets": scene_assets,
                "cost": local_cost,
                "usage": local_usage,
                "skipped": False
            }
            
        except Exception as e:
            print(f"❌ Scene {scene_id} Failed: {e}")
            return {"index": index, "error": str(e)}

    # PARALLEL EXECUTION LOOP
    futures = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i, scene in enumerate(scenes_to_process):
            futures.append(executor.submit(process_single_scene, i, scene))
            
        for future in as_completed(futures):
            res = future.result()
            
            if "error" in res:
                print(f"Parallel Task Error: {res['error']}")
                continue
                
            idx = res["index"]
            
            if res.get("skipped"):
                print(f"Skipped Scene {idx} (Regeneration Mode)")
                if res.get("video_path"):
                     generated_videos_result[idx] = res["video_path"]
                continue
                
            # Success Handling
            generated_videos_result[idx] = res["video_path"]
            
            # Aggregate Assets & Costs
            if res.get("remote_assets"):
                accumulated_remote_assets.update(res["remote_assets"])
            
            total_cost += res.get("cost", 0.0)
            u = res.get("usage", {})
            usage["images"] = usage.get("images", 0) + u.get("images", 0)
            usage["video_seconds"] = usage.get("video_seconds", 0) + u.get("video_seconds", 0)
            
            # Real-time DB Update (Incremental)
            if db and user_id:
                try:
                    # We can't update 'scene_paths' fully yet as it might have Nones
                    # But we can update assets
                    db.save_run(run_id, user_id, "running", result={
                        "remote_assets": accumulated_remote_assets,
                        "cost_usd": round(total_cost, 4)
                    })
                except:
                    pass

    # Clean up Nones (if any failure occurred)
    final_paths = [p for p in generated_videos_result if p is not None]
    
    # Update State
    state["cost_usd"] = total_cost
    state["usage_details"] = usage
        
    # Generate End Card (Can also be parallel, but fast enough to keep here or move to separate thread if needed)
    # Keeping sequential for simplicity as it relies on final product shots potentially
    end_card_path = state.get("end_card_path")
    end_card_url = state.get("end_card_url")

    if not regen_id or regen_id == 'CTA':
        print("--- Checking/Generating End Card ---")
        ec_local = os.path.join(output_dir, f"end_card_{run_id}.png")
        cta = config.get("cta_text", "Shop Now. Link in Bio!")
        website = config.get("website_url", "www.teatee.store") 
        try:
            if product_image:
                end_card_url = generate_end_card(product_image, cta, website, ec_local, visual_dna=dna, config=config)
                if end_card_url:
                    end_card_path = ec_local
                    accumulated_remote_assets["end_card"] = end_card_url
        except Exception as e:
            print(f"End Card Gen Error: {e}")
        
    return {
        "scene_paths": final_paths, 
        "end_card_path": end_card_path, 
        "end_card_url": end_card_url,
        "remote_assets": accumulated_remote_assets,
        "cost_usd": total_cost,
        "usage_details": usage,
        "visual_dna": dna, # Pass through
        "history": history,
        "scenes_list": scenes_to_process # Persist updates (e.g. modifications)
    }




def generate_voice_node(state: AgentState):
    print("--- Generating Voiceover ---")
    config = state.get("config", {})
    if config.get("voiceover_required") is False or config.get("voice_required") is False:
        print("Voiceover disabled in configuration. Skipping.")
        return {"audio_path": ""}
        
    script_text = state.get("script", "Experience the diverse flavors of life.")
    scene_paths = state.get("scene_paths", [])
    visual_dna = state.get("visual_dna", {})
    output_dir = state.get("session_output_dir", "tmp")
    
    # Pass scenes and DNA to voice generator for context-aware generation
    audio_path, duration = generate_voice(script_text, scene_paths=scene_paths, visual_dna=visual_dna, output_dir=output_dir)
    
    # Cost
    # Simple estimation: 1 word ~ 5 chars. Or load file? script_text len is safer
    char_count = len(script_text)
    from projects.backend.services.pricing_service import PricingService
    voice_cost = PricingService.calculate_audio_cost(char_count=char_count)
    
    state["cost_usd"] = state.get("cost_usd", 0.0) + voice_cost
    usage = state.get("usage_details", {})
    usage["voice_chars"] = usage.get("voice_chars", 0) + char_count
    state["usage_details"] = usage
    
    return {"audio_path": audio_path}

def generate_bgm_node(state: AgentState):
    """
    Generate/select BGM in parallel with voice generation.
    Performance optimization: runs concurrently to reduce idle time.
    """
    config = state.get("config", {})
    if not config.get("bgm_required", True):
        print("BGM disabled in configuration. Skipping.")
        return {"bgm_path": None}
    
    from execution.music_selection import select_bgm_track
    output_dir = state.get("session_output_dir", "output")
    visual_dna = state.get("visual_dna", {})
    bgm_path = select_bgm_track(visual_dna, output_dir=output_dir, config=config)
    return {"bgm_path": bgm_path}


def assembly_node(state: AgentState):
    scenes = state.get("scene_paths", [])
    audio = state.get("audio_path", "")
    visual_dna = state.get("visual_dna", {})
    bgm_path = state.get("bgm_path")  # Now retrieved from state instead of generated here
    output_dir = state.get("session_output_dir", "output")
    config = state.get("config", {})
    
    # Pass remote_assets for assembly fallback
    asm_config = config.copy()
    asm_config["remote_assets"] = state.get("remote_assets", {})
    
    end_card_path = state.get("end_card_path")
    final_video = assemble_video(scenes, audio, bgm_path=bgm_path, output_dir=output_dir, config=asm_config, end_card_path=end_card_path)
    
    # 4K Upscaling (Premium)
    if config.get("quality") == "4k" or config.get("premium", False):
        try:
            from execution.upscale import upscale_video_4k
            print("--- Premium: Upscaling to 4K ---")
            upscaled = upscale_video_4k(final_video)
            if upscaled:
                final_video = upscaled
        except Exception as e:
            print(f"Upscaling failed: {e}")

    return {"result": f"Final Video Available: {final_video}"}

# Define the graph
def build_graph():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("extract_dna", extract_dna_node)
    workflow.add_node("generate_script", generate_script_node)
    workflow.add_node("generate_character", generate_character_node)
    workflow.add_node("generate_scenes", generate_scenes_node)
    workflow.add_node("generate_voice", generate_voice_node)
    workflow.add_node("generate_bgm", generate_bgm_node)  # Performance: parallel with voice
    workflow.add_node("assembly", assembly_node)

    # Set entry point
    workflow.set_entry_point("extract_dna")

    # Add edges - Voice and BGM run in parallel after scenes
    workflow.add_edge("extract_dna", "generate_script")
    workflow.add_edge("generate_script", "generate_character")
    workflow.add_edge("generate_character", "generate_scenes")
    
    # PARALLEL EXECUTION: Voice and BGM both start after scenes
    workflow.add_edge("generate_scenes", "generate_voice")
    workflow.add_edge("generate_scenes", "generate_bgm")  # Runs concurrently with voice
    
    # Assembly waits for both voice and BGM to complete
    workflow.add_edge("generate_voice", "assembly")
    workflow.add_edge("generate_bgm", "assembly")
    workflow.add_edge("assembly", END)

    # Compile
    app = workflow.compile()
    return app

if __name__ == "__main__":
    print("Starting Workflow Test...")
    app = build_graph()
    
    # Run the graph
    import time
    run_id = f"run_{int(time.time())}"
    # Force Absolute Path for clarity and avoidance of relative path confusion
    session_dir = os.path.abspath(os.path.join(os.getcwd(), "tmp", run_id))
    
    try:
        os.makedirs(session_dir, exist_ok=True)
        if not os.path.exists(session_dir):
            raise OSError(f"Failed to create session directory: {session_dir}")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not create output directory {session_dir}: {e}")
        sys.exit(1)
        
    print(f"--- Output Directory for this Session (Absolute): {session_dir} ---")

    # Load Configuration
    config_path = "brand/configuration.json"
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            print(f"--- Loaded Configuration from {config_path} ---")
        except Exception as e:
            print(f"Warning: Failed to load configuration: {e}")
            
    # CLI OVERRIDE: Environment Variables take precedence over Config File
    # This ensures that if the user selects a mode in the launcher, it is respected.
    if os.getenv("IMAGE_PROVIDER"):
        print(f"CLI Override: Setting image_provider to {os.getenv('IMAGE_PROVIDER')}")
        config["image_provider"] = os.getenv("IMAGE_PROVIDER")
        
    if os.getenv("LLM_PROVIDER"):
        config["llm_provider"] = os.getenv("LLM_PROVIDER")
    
    # Also override models if specific env vars are set (optional, but good for consistency)
    if os.getenv("IMAGE_MODEL"):
        config["image_model"] = os.getenv("IMAGE_MODEL")

    initial_state = {
        "input_data": os.getenv("PRODUCT_DESCRIPTION", "Generic Product Ad for Meta/Instagram/Google Ads"),
        "product_image_path": os.getenv("PRODUCT_IMAGE_PATH"),
        "run_id": run_id,
        "session_output_dir": session_dir,
        "config": config
    }
    result = app.invoke(initial_state)
    
    print("Workflow Result:", result)
