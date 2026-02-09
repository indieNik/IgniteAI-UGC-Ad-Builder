"""
Community Router
Handles public video sharing, likes, and community feed
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
import time
from projects.backend.dependencies import get_current_user
from projects.backend.services.db_service import db_service
from google.cloud import firestore

router = APIRouter()

@router.post("/view/{run_id}")
async def track_view(run_id: str):
    """Increment view count"""
    try:
        ref = db_service.db.collection("executions").document(run_id)
        ref.update({"views": firestore.Increment(1)})
        return {"status": "success"}
    except Exception as e:
        # Ignore errors for views
        return {"status": "ignored"}

# ============= Models =============

class ShareVideoRequest(BaseModel):
    is_public: bool

class CommunityVideo(BaseModel):
    run_id: str
    user_id: str
    user_name: Optional[str] = None
    project_name: Optional[str] = None
    video_url: str
    thumbnail_url: Optional[str] = None
    likes: int = 0
    views: int = 0
    shared_at: float
    is_liked_by_user: bool = False

# ============= Community Feed =============

@router.get("/videos")
async def get_community_videos(
    sort_by: str = Query("recent", regex="^(recent|popular|trending|liked)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user)
):
    """Get public community videos with pagination"""
    try:
        current_user_id = user.get("uid")
        
        # Query public videos
        query = db_service.db.collection("executions").where("is_public", "==", True)
        
        # Sort based on parameter
        if sort_by == "recent":
            query = query.order_by("shared_at", direction=firestore.Query.DESCENDING)
        elif sort_by == "popular":
            query = query.order_by("likes", direction=firestore.Query.DESCENDING)
        elif sort_by == "trending":
            # Trending = high likes in last 7 days
            week_ago = time.time() - (7 * 24 * 60 * 60)
            query = query.where("shared_at", ">=", week_ago).order_by("shared_at", direction=firestore.Query.DESCENDING).order_by("likes", direction=firestore.Query.DESCENDING)
        
        elif sort_by == "liked":
            # Fetch liked video IDs
            likes_ref = db_service.db.collection("community_likes").where("user_id", "==", current_user_id)
            liked_docs = likes_ref.stream()
            liked_ids = [d.get("run_id") for d in liked_docs]
            
            if not liked_ids:
                return {"videos": [], "total": 0, "offset": offset, "limit": limit}

            # Fetch specific docs (Manual pagination for 'liked' tab needed if list is huge)
            # For now, simplistic approach: fetch all liked (up to reasonable limit), then paginate in memory
            # or Query 'in' chunks. 
            # Using getAll for efficiency
            refs = [db_service.db.collection("executions").document(rid) for rid in liked_ids]
            
            # Simple slicing for pagination on ID list first
            start = offset
            end = offset + limit
            page_refs = refs[start:end]
            
            if not page_refs:
                 docs = []
            else:
                 docs = db_service.db.get_all(page_refs)
            
            # Note: docs from getAll are snapshots
            # Filter out non-existent or private ones (if unliked implies visible?)
            # Usually we check existence.
        
        # Apply pagination (Only for non-liked queries)
        if sort_by != "liked":
            query = query.limit(limit).offset(offset)
            docs = query.stream()
        
        videos = []
        for doc in docs:
            data = doc.to_dict()
            
            # Check if current user liked this video
            like_doc = db_service.db.collection("community_likes").document(f"{current_user_id}_{data['run_id']}").get()
            is_liked = like_doc.exists
            
            # Get user info
            user_doc = db_service.db.collection("users").document(data.get("user_id")).get()
            user_name = user_doc.to_dict().get("name", "Anonymous") if user_doc.exists else "Anonymous"
            
            # Extract video info
            result = data.get("result", {})
            
            videos.append({
                "run_id": data.get("run_id"),
                "user_id": data.get("user_id"),
                "user_name": user_name,
                "project_name": result.get("config", {}).get("project_title", "Untitled"),
                "video_url": result.get("video_url", ""),
                "thumbnail_url": result.get("remote_assets", {}).get("Hook_image", ""),
                "likes": data.get("likes", 0),
                "views": data.get("views", 0),
                "shared_at": data.get("shared_at", 0),
                "is_liked_by_user": is_liked
            })
        
        return {
            "videos": videos,
            "total": len(videos),
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video/{run_id}")
async def get_community_video(run_id: str, user: dict = Depends(get_current_user)):
    """Get single community video details"""
    try:
        current_user_id = user.get("uid")
        
        # Get video
        doc = db_service.db.collection("executions").document(run_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Video not found")
        
        data = doc.to_dict()
        
        # Check if public
        if not data.get("is_public", False):
            raise HTTPException(status_code=403, detail="Video is not public")
        
        # Increment view count
        db_service.db.collection("executions").document(run_id).update({
            "views": firestore.Increment(1)
        })
        
        # Check if liked by current user
        like_doc = db_service.db.collection("community_likes").document(f"{current_user_id}_{run_id}").get()
        is_liked = like_doc.exists
        
        # Get user info
        user_doc = db_service.db.collection("users").document(data.get("user_id")).get()
        user_name = user_doc.to_dict().get("name", "Anonymous") if user_doc.exists else "Anonymous"
        
        result = data.get("result", {})
        
        return {
            "run_id": data.get("run_id"),
            "user_id": data.get("user_id"),
            "user_name": user_name,
            "project_name": result.get("config", {}).get("project_title", "Untitled"),
            "video_url": result.get("video_url", ""),
            "thumbnail_url": result.get("remote_assets", {}).get("Hook_image", ""),
            "likes": data.get("likes", 0) + 1,  # Include the increment
            "views": data.get("views", 0) + 1,
            "shared_at": data.get("shared_at", 0),
            "is_liked_by_user": is_liked
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= Share/Unshare =============

@router.post("/share/{run_id}")
async def share_video(run_id: str, user: dict = Depends(get_current_user)):
    """Share video to community"""
    try:
        user_id = user.get("uid")
        
        # Get video
        doc = db_service.db.collection("executions").document(run_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Video not found")
        
        data = doc.to_dict()
        
        # Check ownership
        if data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You can only share your own videos")
        
        # Check if video is completed
        if data.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Only completed videos can be shared")
        
        # Update video to public
        db_service.db.collection("executions").document(run_id).update({
            "is_public": True,
            "shared_at": time.time(),
            "likes": 0,
            "views": 0
        })
        
        # Track event
        db_service.track_event(user_id, "video_shared_to_community", {"run_id": run_id})
        
        return {"message": "Video shared to community successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/share/{run_id}")
async def unshare_video(run_id: str, user: dict = Depends(get_current_user)):
    """Remove video from community"""
    try:
        user_id = user.get("uid")
        
        # Get video
        doc = db_service.db.collection("executions").document(run_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Video not found")
        
        data = doc.to_dict()
        
        # Check ownership
        if data.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="You can only unshare your own videos")
        
        # Update video to private
        db_service.db.collection("executions").document(run_id).update({
            "is_public": False,
            "shared_at": firestore.DELETE_FIELD
        })
        
        # Track event
        db_service.track_event(user_id, "video_unshared_from_community", {"run_id": run_id})
        
        return {"message": "Video removed from community"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= Likes =============

@router.post("/like/{run_id}")
async def like_video(run_id: str, user: dict = Depends(get_current_user)):
    """Like a community video"""
    try:
        user_id = user.get("uid")
        
        # Get video
        doc = db_service.db.collection("executions").document(run_id).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Video not found")
        
        data = doc.to_dict()
        
        # Check if public
        if not data.get("is_public", False):
            raise HTTPException(status_code=403, detail="Can only like public videos")
        
        # Check if already liked
        like_id = f"{user_id}_{run_id}"
        like_doc = db_service.db.collection("community_likes").document(like_id).get()
        
        if like_doc.exists:
            return {"message": "Already liked"}
        
        # Create like record
        db_service.db.collection("community_likes").document(like_id).set({
            "user_id": user_id,
            "run_id": run_id,
            "created_at": time.time()
        })
        
        # Increment like count
        db_service.db.collection("executions").document(run_id).update({
            "likes": firestore.Increment(1)
        })
        
        # Track event
        db_service.track_event(user_id, "video_liked", {"run_id": run_id})
        
        return {"message": "Video liked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/like/{run_id}")
async def unlike_video(run_id: str, user: dict = Depends(get_current_user)):
    """Unlike a community video"""
    try:
        user_id = user.get("uid")
        
        # Check if liked
        like_id = f"{user_id}_{run_id}"
        like_doc = db_service.db.collection("community_likes").document(like_id).get()
        
        if not like_doc.exists:
            return {"message": "Not liked"}
        
        # Delete like record
        db_service.db.collection("community_likes").document(like_id).delete()
        
        # Decrement like count
        db_service.db.collection("executions").document(run_id).update({
            "likes": firestore.Increment(-1)
        })
        
        # Track event
        db_service.track_event(user_id, "video_unliked", {"run_id": run_id})
        
        return {"message": "Video unliked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
