
"""
Configuration settings for Gemini 2.5 Flash Image generation
"""


import os
from typing import List


# API Configuration
# API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/"
API_BASE_URL= "https://api.thucchien.ai/gemini/v1beta"

DEFAULT_MODEL = "gemini-2.5-flash-image-preview"


# Image Generation Settings
SUPPORTED_ASPECT_RATIOS: List[str] = [
   "1:1",   # Square
   "3:2",   # Photo landscape
   "2:3",   # Photo portrait
   "3:4",   # Standard portrait
   "4:3",   # Standard landscape
   "4:5",   # Near square tall (Instagram)
   "5:4",   # Near square wide
   "9:16",  # Tall portrait (Mobile/TikTok/Stories)
   "16:9",  # Wide landscape (Videos/Banners)
   "21:9"   # Ultra wide (Cinematic)
]


# Technical Limits (from Google documentation)
MAX_INPUT_TOKENS = 32768
MAX_OUTPUT_TOKENS = 32768
MAX_INPUT_IMAGES = 3        # Maximum reference images per prompt
MAX_IMAGE_SIZE_MB = 7       # Maximum size per image
MAX_OUTPUT_IMAGES = 10      # Maximum images to generate per prompt
MAX_TOTAL_INPUT_SIZE_MB = 500


# Supported image formats
SUPPORTED_IMAGE_FORMATS = ["image/png", "image/jpeg", "image/webp"]
SUPPORTED_FILE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]


# Output Settings
DEFAULT_OUTPUT_DIR = "generated"
DEFAULT_IMAGES_DIR = "generated/images"
DEFAULT_SESSIONS_DIR = "generated/sessions"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_NUM_IMAGES = 1


# Session Settings
MAX_SESSION_HISTORY = 10     # Maximum messages to keep in session history
SESSION_TIMEOUT_HOURS = 24   # Auto-cleanup sessions older than this
AUTO_SAVE_REFERENCES = True  # Save reference images in session folder


# File naming
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
SESSION_ID_LENGTH = 8


# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"




class ImageConfig:
   """Configuration for image generation"""
  
   def __init__(
       self,
       aspect_ratio: str = DEFAULT_ASPECT_RATIO,
       num_images: int = DEFAULT_NUM_IMAGES,
       output_dir: str = DEFAULT_OUTPUT_DIR,
       save_references: bool = AUTO_SAVE_REFERENCES,
       organize_by_date: bool = True,
       output_format: str = "png"
   ):
       """
       Initialize image generation configuration
      
       Args:
           aspect_ratio: Image aspect ratio (e.g., "16:9")
           num_images: Number of images to generate (1-10)
           output_dir: Base directory for outputs
           save_references: Whether to save reference images
           organize_by_date: Organize output by date folders
           output_format: Output image format (png, jpeg, webp)
       """
       if aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
           raise ValueError(f"Aspect ratio must be one of {SUPPORTED_ASPECT_RATIOS}")
      
       if not 1 <= num_images <= MAX_OUTPUT_IMAGES:
           raise ValueError(f"num_images must be between 1 and {MAX_OUTPUT_IMAGES}")
      
       if output_format not in ["png", "jpeg", "jpg", "webp"]:
           raise ValueError("output_format must be png, jpeg, or webp")
      
       self.aspect_ratio = aspect_ratio
       self.num_images = num_images
       self.output_dir = output_dir
       self.save_references = save_references
       self.organize_by_date = organize_by_date
       self.output_format = "jpeg" if output_format == "jpg" else output_format




class SessionConfig:
   """Configuration for session management"""
  
   def __init__(
       self,
       max_history: int = MAX_SESSION_HISTORY,
       save_references: bool = AUTO_SAVE_REFERENCES,
       auto_cleanup: bool = False,
       timeout_hours: int = SESSION_TIMEOUT_HOURS
   ):
       """
       Initialize session configuration
      
       Args:
           max_history: Maximum messages to keep in history
           save_references: Save reference images with session
           auto_cleanup: Automatically clean up old sessions
           timeout_hours: Hours before session is considered stale
       """
       self.max_history = max_history
       self.save_references = save_references
       self.auto_cleanup = auto_cleanup
       self.timeout_hours = timeout_hours




# Aspect ratio information for users
ASPECT_RATIO_INFO = {
   "1:1": {"name": "Square", "use_case": "Social media posts, avatars"},
   "3:2": {"name": "Photo landscape", "use_case": "Standard photos"},
   "2:3": {"name": "Photo portrait", "use_case": "Portrait photography"},
   "3:4": {"name": "Standard portrait", "use_case": "Print materials"},
   "4:3": {"name": "Standard landscape", "use_case": "Presentations"},
   "4:5": {"name": "Near square tall", "use_case": "Instagram posts"},
   "5:4": {"name": "Near square wide", "use_case": "Computer displays"},
   "9:16": {"name": "Tall portrait", "use_case": "Mobile/TikTok/Stories"},
   "16:9": {"name": "Wide landscape", "use_case": "Videos, banners"},
   "21:9": {"name": "Ultra wide", "use_case": "Cinematic, panoramas"}
}




def get_aspect_ratio_description(ratio: str) -> str:
   """Get human-readable description of aspect ratio"""
   info = ASPECT_RATIO_INFO.get(ratio, {})
   name = info.get("name", "Unknown")
   use_case = info.get("use_case", "General use")
   return f"{ratio} - {name} ({use_case})"




def validate_image_file(file_path: str) -> bool:
   """Check if file is a valid image file"""
   import os
   if not os.path.exists(file_path):
       return False
  
   ext = os.path.splitext(file_path)[1].lower()
   return ext in SUPPORTED_FILE_EXTENSIONS




def get_image_size_mb(file_path: str) -> float:
   """Get image file size in MB"""
   import os
   size_bytes = os.path.getsize(file_path)
   return size_bytes / (1024 * 1024)






