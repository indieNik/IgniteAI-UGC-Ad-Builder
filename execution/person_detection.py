"""
Person detection utility for pre-flight warnings.
Detects if an image contains people or if user text mentions people/celebrities.
"""
import re
from typing import Dict, List

def detect_person_in_text(text: str) -> Dict[str, any]:
    """
    Detect mentions of people, celebrities, or human-related keywords in text.
    
    Args:
        text: User-provided text (product description, input data)
    
    Returns:
        {
            "has_person_mention": bool,
            "warnings": [{"message": str, "severity": str}]
        }
    """
    warnings = []
    
    # Keywords that indicate human presence
    person_keywords = [
        r'\bperson\b', r'\bpeople\b', r'\bman\b', r'\bwoman\b', r'\bchild\b',
        r'\bface\b', r'\bportrait\b', r'\bselfie\b', r'\bmodel\b',
        r'\bcelebrity\b', r'\bactor\b', r'\bactress\b', r'\binfluencer\b',
        r'\bhuman\b', r'\bme\b', r'\bmyself\b', r'\bi\b', r'\bmy face\b'
    ]
    
    text_lower = text.lower()
    detected_keywords = []
    
    for keyword_pattern in person_keywords:
        if re.search(keyword_pattern, text_lower):
            detected_keywords.append(keyword_pattern.strip(r'\b'))
    
    if detected_keywords:
        warnings.append({
            "code": "PERSON_MENTIONED_IN_TEXT",
            "severity": "medium",
            "message": f"Your description mentions: {', '.join(detected_keywords[:3])}. Videos with people may be rejected by Veo.",
            "recommendation": "Use product-only images and descriptions for best results."
        })
    
    return {
        "has_person_mention": len(detected_keywords) > 0,
        "detected_keywords": detected_keywords,
        "warnings": warnings
    }

def detect_person_in_image(image_path: str) -> Dict[str, any]:
    """
    Detect faces/people in an image using OpenCV (optional - lightweight check).
    Falls back gracefully if OpenCV is not available.
    
    Args:
        image_path: Path to image file
    
    Returns:
        {
            "has_faces": bool,
            "face_count": int,
            "warnings": [{"message": str, "severity": str}]
        }
    """
    warnings = []
    
    try:
        import cv2
        import numpy as np
    except ImportError:
        # OpenCV not available - return warning but don't fail
        warnings.append({
            "code": "OPENCV_NOT_AVAILABLE",
            "severity": "low",
            "message": "Face detection unavailable (OpenCV not installed). Proceeding without pre-flight check.",
            "recommendation": "Install opencv-python for face detection warnings."
        })
        return {
            "has_faces": False,
            "face_count": 0,
            "warnings": warnings,
            "detection_skipped": True
        }
    
    try:
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            warnings.append({
                "code": "IMAGE_LOAD_FAILED",
                "severity": "low",
                "message": "Could not load image for face detection.",
                "recommendation": "Ensure image path is correct."
            })
            return {"has_faces": False, "face_count": 0, "warnings": warnings}
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load Haar Cascade (built-in with OpenCV)
        # Using frontal face cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        face_count = len(faces)
        
        if face_count > 0:
            warnings.append({
                "code": "FACES_DETECTED",
                "severity": "high",
                "message": f"⚠️ {face_count} face(s) detected in your image. Veo may reject this video.",
                "recommendation": "Use a product-only image without people for best results. Click 'Proceed Anyway' to continue at your own risk."
            })
        
        return {
            "has_faces": face_count > 0,
            "face_count": face_count,
            "warnings": warnings
        }
        
    except Exception as e:
        warnings.append({
            "code": "DETECTION_ERROR",
            "severity": "low",
            "message": f"Face detection failed: {str(e)}",
            "recommendation": "Proceeding without face detection."
        })
        return {
            "has_faces": False,
            "face_count": 0,
            "warnings": warnings,
            "detection_error": True
        }

def pre_flight_check(input_data: str, image_path: str = None) -> Dict[str, any]:
    """
    Combined pre-flight check for person detection in text and image.
    
    Args:
        input_data: User text input
        image_path: Optional path to product image
    
    Returns:
        {
            "safe_to_proceed": bool,  # False if high-severity warnings
            "warnings": [{"code": str, "severity": str, "message": str, "recommendation": str}],
            "requires_confirmation": bool  # True if user should confirm before proceeding
        }
    """
    all_warnings = []
    
    # Check text
    text_result = detect_person_in_text(input_data)
    all_warnings.extend(text_result.get("warnings", []))
    
    # Check image if provided
    if image_path:
        image_result = detect_person_in_image(image_path)
        all_warnings.extend(image_result.get("warnings", []))
    
    # Determine if confirmation is required
    high_severity_warnings = [w for w in all_warnings if w["severity"] == "high"]
    requires_confirmation = len(high_severity_warnings) > 0
    
    # Safe to proceed if no high-severity warnings (or if user has confirmed)
    safe_to_proceed = not requires_confirmation
    
    return {
        "safe_to_proceed": safe_to_proceed,
        "requires_confirmation": requires_confirmation,
        "warnings": all_warnings,
        "has_person_detected": len(all_warnings) > 0
    }

if __name__ == "__main__":
    # Test cases
    print("=== Person Detection Tests ===\n")
    
    # Test 1: Text with person mention
    print("Test 1: Text with person mention")
    result = detect_person_in_text("This is me using the product in my daily routine")
    print(f"Result: {result}\n")
    
    # Test 2: Product-only text
    print("Test 2: Product-only text")
    result = detect_person_in_text("Premium organic tea from the Himalayas")
    print(f"Result: {result}\n")
    
    # Test 3: Pre-flight check (no image)
    print("Test 3: Pre-flight check without image")
    result = pre_flight_check("Amazing skincare product with vitamin C")
    print(f"Result: {result}\n")
