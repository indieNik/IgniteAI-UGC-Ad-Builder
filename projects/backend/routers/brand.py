from fastapi import APIRouter, Depends, HTTPException
from projects.backend.dependencies import get_current_user
from projects.backend.services.db_service import db_service
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class BrandConfig(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    colors: Optional[List[str]] = None
    character_prompt: Optional[str] = None
    music_style: Optional[str] = None
    font_family: Optional[str] = None

@router.get("")
async def get_brand(user: dict = Depends(get_current_user)):
    user_id = user["uid"]
    brand = db_service.get_brand(user_id)
    if not brand:
        return {"status": "not_found", "brand": None}
    return {"status": "success", "brand": brand}

@router.post("")
async def update_brand(config: BrandConfig, user: dict = Depends(get_current_user)):
    user_id = user["uid"]
    brand_data = config.dict(exclude_unset=True)
    updated_brand = db_service.upsert_brand(user_id, brand_data)
    return {"status": "success", "brand": updated_brand}
