from pydantic import BaseModel
from typing import Optional, Dict, Any

class GenerateRequest(BaseModel):
    prompt: str
    product_image_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}

class GenerateResponse(BaseModel):
    run_id: str
    status: str
    message: str

class RegenerateSceneRequest(BaseModel):
    prompt: Optional[str] = None
