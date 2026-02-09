import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import threading

try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

from openai import OpenAI
import requests

# GLOBAL LOCK: Ensures only one thread calls Veo API at a time
# This prevents race conditions where multiple threads pass rate limit check
# but then all hit the API simultaneously, causing cascading 429 errors
VEO_API_LOCK = threading.Lock()

# Factory Base Class
class MediaProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, output_path: str, config: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def generate_video(self, prompt: str, output_path: str, image_path: Optional[str], config: Dict[str, Any]) -> Tuple[str, float, str]:
        pass

# Concrete Implementations
class OpenAIMediaProvider(MediaProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt: str, output_path: str, config: Dict[str, Any]) -> str:
        print(f"--- MediaFactory: Generating Image via OpenAI (DALL-E 3) ---")
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792", 
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            img_data = requests.get(image_url).content
            with open(output_path, "wb") as f:
                f.write(img_data)
            return output_path
        except Exception as e:
            print(f"OpenAI Image Gen Failed: {e}")
            raise e

    def generate_video(self, prompt: str, output_path: str, image_path: Optional[str], config: Dict[str, Any]) -> Tuple[str, float, str]:
        print("OpenAI Sora is not yet available via public API in this context.")
        raise NotImplementedError("OpenAI Video Generation not supported yet.")

class GoogleMediaProvider(MediaProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found.")
        self.client = genai.Client(api_key=self.api_key)

    def generate_image(self, prompt: str, output_path: str, config: Dict[str, Any]) -> str:
        model_name = config.get("image_model", "imagen-4.0-generate-001")
        print(f"--- MediaFactory: Generating Image via Google ({model_name}) ---")
        
        try:
            response = self.client.models.generate_images(
                model=model_name,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="9:16",
                    output_mime_type="image/png"
                )
            )
            if response.generated_images:
                image_bytes = response.generated_images[0].image.image_bytes
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                return output_path
            else:
                raise ValueError("No images returned from Google Imagen.")
        except Exception as e:
            print(f"Google Image Gen Failed: {e}")
            raise e

    def generate_video(self, prompt: str, output_path: str, image_path: Optional[str], config: Dict[str, Any]) -> Tuple[str, float, str]:
        model_name = config.get("video_model", "veo-3.1-fast-generate-preview")
        duration = float(config.get("duration", 6.0))
        
        print(f"--- MediaFactory: Generating Video via Google Veo ({model_name}) ---")
        
        # SMART RATE LIMITING: Use Token Bucket algorithm
        # Only waits when quota is actually full (not on every request)
        
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES + 1):
            try:
                # CRITICAL SECTION: Acquire global lock to serialize Veo calls
                # This ensures that rate limiter check + API call happen atomically
                # Only one thread can execute this block at a time
                with VEO_API_LOCK:
                    print(f"🔒 Acquired Veo API lock (Thread {threading.current_thread().name})")
                    
                    # 1. Check Rate Limiter (Throttling)
                    try:
                        from projects.backend.services.rate_limiter import rate_limiter
                        from execution.exceptions import QuotaExceededException
                        rate_limiter.check_and_wait(model_name)
                    except ImportError:
                        print("⚠️ Rate limiter not available, proceeding without throttle")
                    except QuotaExceededException as qe:
                        # Daily quota exhausted - Fail immediately, no retry
                        print(f"❌ Daily Quota Exhausted: {qe}")
                        print("⚡ Skipping retries. Falling back to Ken Burns effect.")
                        raise  # Propagate to trigger fallback in scene_generation.py
                
                    # 2. Construct Config
                    vid_config = types.GenerateVideosConfig(
                        number_of_videos=1,
                        aspect_ratio=config.get("aspect_ratio", "9:16"),
                        duration_seconds=duration
                    )

                    if image_path:
                        with open(image_path, "rb") as f:
                            img_bytes = f.read()
                        veo_image = types.Image(image_bytes=img_bytes, mime_type="image/png")
                        source = types.GenerateVideosSource(prompt=prompt, image=veo_image)
                    else:
                        source = types.GenerateVideosSource(prompt=prompt)

                    # 3. Call API (INSIDE LOCK)
                    print(f"calling Veo (Attempt {attempt+1}/{MAX_RETRIES+1})...")
                    response = self.client.models.generate_videos(
                        model=model_name,
                        source=source,
                        config=vid_config
                    )
                    
                    # Lock is released here, but request is already sent to Google
                    # Polling can happen outside the lock
                    
                print(f"🔓 Released Veo API lock (request sent)")
                print(f"Veo Operation Started: {response.name}. Polling...")
                
                # 4. Poll for completion (OUTSIDE LOCK - doesn't consume quota)
                while not response.done:
                    time.sleep(10)
                    response = self.client.operations.get(response)
                    
                if response.response and response.response.generated_videos:
                    vid_content = self.client.files.download(file=response.response.generated_videos[0].video)
                    with open(output_path, "wb") as f:
                        f.write(vid_content)
                    return output_path, duration, model_name
                else:
                    error_msg = str(response.error) if response.error else "Unknown error"
                    # If this is a quota error wrapped in the response object
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "quota" in error_msg.lower():
                        raise RuntimeError(f"Veo Quota Error: {error_msg}")
                        
                    # ENHANCED DEBUGGING FOR "Unknown error"
                    print(f"❌ Veo Response Details: Status={response.state if hasattr(response, 'state') else 'N/A'}")
                    try:
                        # Attempt to log more attributes if available
                        if hasattr(response, 'metadata'): print(f"Metadata: {response.metadata}")
                        if hasattr(response, 'result'): print(f"Result: {response.result}")
                    except:
                        pass
                        
                    raise ValueError(f"Veo Generation Failed: {error_msg} (See logs for object dump)")

            except Exception as e:
                error_str = str(e)
                is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower()
                
                if is_rate_limit and attempt < MAX_RETRIES:
                    wait_time = (attempt + 1) * 30 # 30s, 60s, 90s
                    print(f"⚠️ Veo Rate Limit Hit (Attempt {attempt+1}): {e}")
                    print(f"⏳ Sleeping for {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue # Retry
                else:
                    # Final failure or non-retryable error
                    if is_rate_limit:
                         print(f"❌ PEAK RPM LIMIT HIT after {MAX_RETRIES} retries: {e}")
                    else:
                         print(f"Google Video Gen Failed: {e}")
                    raise e

class MediaFactory:
    @staticmethod
    def get_provider(provider_name: str) -> MediaProvider:
        provider_name = provider_name.lower()
        if "openai" in provider_name:
            return OpenAIMediaProvider()
        elif "google" in provider_name or "gemini" in provider_name or "veo" in provider_name:
            return GoogleMediaProvider()
        else:
            raise ValueError(f"Unknown Media Provider: {provider_name}")

    @staticmethod
    def generate_image(prompt: str, output_path: str, config: Dict[str, Any]) -> str:
        provider_name = config.get("image_provider", os.getenv("IMAGE_PROVIDER", "google"))
        provider = MediaFactory.get_provider(provider_name)
        return provider.generate_image(prompt, output_path, config)

    @staticmethod
    def generate_video(prompt: str, output_path: str, image_path: Optional[str], config: Dict[str, Any]) -> Tuple[str, float, str]:
        provider_name = config.get("video_provider", "google") # Video defaults to Google usually as OpenAI has no Sora API
        # Intelligent fallback logic if user selects OpenAI for video but it's not supported?
        # For now, simplistic.
        if "openai" in provider_name:
             print("Warning: OpenAI Video not supported. Fallback to Google Veo.")
             provider_name = "google"
             
        provider = MediaFactory.get_provider(provider_name)
        return provider.generate_video(prompt, output_path, image_path, config)
