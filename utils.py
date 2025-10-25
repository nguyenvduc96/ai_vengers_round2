"""
Utility functions for image generation
"""


import os
import base64
from datetime import datetime
from typing import List, Optional, Dict, Any
from PIL import Image
import io


from config import (
   TIMESTAMP_FORMAT,
   SUPPORTED_FILE_EXTENSIONS,
   MAX_IMAGE_SIZE_MB,
   get_image_size_mb
)




def encode_image_to_base64(image_path: str) -> tuple[str, str]:
   """
   Encode image file to base64 string
  
   Args:
       image_path: Path to image file
      
   Returns:
       Tuple of (base64_string, mime_type)
   """
   # Determine MIME type from extension
   ext = os.path.splitext(image_path)[1].lower()
   mime_type_map = {
       '.png': 'image/png',
       '.jpg': 'image/jpeg',
       '.jpeg': 'image/jpeg',
       '.webp': 'image/webp'
   }
   mime_type = mime_type_map.get(ext, 'image/jpeg')
  
   # Read and encode
   with open(image_path, 'rb') as f:
       image_data = f.read()
  
   base64_string = base64.b64encode(image_data).decode('utf-8')
   return base64_string, mime_type




def decode_base64_to_image(base64_string: str, output_path: str) -> str:
   """
   Decode base64 string to image file
  
   Args:
       base64_string: Base64 encoded image data
       output_path: Path to save decoded image
      
   Returns:
       Path to saved image file
   """
   # Handle data URL format (data:image/png;base64,...)
   if ',' in base64_string:
       header, encoded = base64_string.split(',', 1)
   else:
       encoded = base64_string
  
   # Decode and save
   image_data = base64.b64decode(encoded)
  
   # Ensure directory exists
   os.makedirs(os.path.dirname(output_path), exist_ok=True)
  
   with open(output_path, 'wb') as f:
       f.write(image_data)
  
   return output_path




def validate_reference_images(image_paths: List[str]) -> Dict[str, Any]:
   """
   Validate reference images before sending to API
  
   Args:
       image_paths: List of image file paths
      
   Returns:
       Dict with validation results
   """
   from config import MAX_INPUT_IMAGES
  
   errors = []
   warnings = []
   valid_images = []
  
   # Check count
   if len(image_paths) > MAX_INPUT_IMAGES:
       errors.append(f"Too many images: {len(image_paths)} (max: {MAX_INPUT_IMAGES})")
       return {"valid": False, "errors": errors, "valid_images": []}
  
   # Check each image
   for image_path in image_paths:
       # Check existence
       if not os.path.exists(image_path):
           errors.append(f"File not found: {image_path}")
           continue
      
       # Check extension
       ext = os.path.splitext(image_path)[1].lower()
       if ext not in SUPPORTED_FILE_EXTENSIONS:
           errors.append(f"Unsupported format: {image_path} (must be PNG, JPEG, or WebP)")
           continue
      
       # Check size
       size_mb = get_image_size_mb(image_path)
       if size_mb > MAX_IMAGE_SIZE_MB:
           errors.append(f"Image too large: {image_path} ({size_mb:.2f}MB, max: {MAX_IMAGE_SIZE_MB}MB)")
           continue
       elif size_mb > MAX_IMAGE_SIZE_MB * 0.8:
           warnings.append(f"Image near size limit: {image_path} ({size_mb:.2f}MB)")
      
       valid_images.append(image_path)
  
   return {
       "valid": len(errors) == 0,
       "errors": errors,
       "warnings": warnings,
       "valid_images": valid_images
   }




def generate_filename(
   prefix: str = "generated",
   suffix: str = "",
   extension: str = "png",
   add_timestamp: bool = True
) -> str:
   """
   Generate filename with optional timestamp
  
   Args:
       prefix: Filename prefix
       suffix: Filename suffix
       extension: File extension (without dot)
       add_timestamp: Whether to add timestamp
      
   Returns:
       Generated filename
   """
   parts = [prefix]
  
   if add_timestamp:
       timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
       parts.append(timestamp)
  
   if suffix:
       parts.append(suffix)
  
   filename = "_".join(parts) + f".{extension}"
   return filename




def organize_output_path(
   base_dir: str,
   filename: str,
   organize_by_date: bool = True
) -> str:
   """
   Generate organized output path
  
   Args:
       base_dir: Base output directory
       filename: Image filename
       organize_by_date: Whether to organize by date
      
   Returns:
       Full output path
   """
   if organize_by_date:
       date_folder = datetime.now().strftime("%Y%m%d")
       output_path = os.path.join(base_dir, date_folder, filename)
   else:
       output_path = os.path.join(base_dir, filename)
  
   # Ensure directory exists
   os.makedirs(os.path.dirname(output_path), exist_ok=True)
  
   return output_path




def get_image_info(image_path: str) -> Dict[str, Any]:
   """
   Get information about an image file
  
   Args:
       image_path: Path to image file
      
   Returns:
       Dict with image information
   """
   if not os.path.exists(image_path):
       return {"error": "File not found"}
  
   try:
       # Get file info
       size_bytes = os.path.getsize(image_path)
       size_mb = size_bytes / (1024 * 1024)
      
       # Get image dimensions
       with Image.open(image_path) as img:
           width, height = img.size
           format_name = img.format
           mode = img.mode
      
       # Calculate aspect ratio
       from math import gcd
       divisor = gcd(width, height)
       aspect_ratio = f"{width//divisor}:{height//divisor}"
      
       return {
           "path": image_path,
           "size_bytes": size_bytes,
           "size_mb": round(size_mb, 2),
           "width": width,
           "height": height,
           "aspect_ratio": aspect_ratio,
           "format": format_name,
           "mode": mode
       }
   except Exception as e:
       return {"error": str(e)}




def resize_image_if_needed(
   image_path: str,
   max_size_mb: float = MAX_IMAGE_SIZE_MB,
   quality: int = 85
) -> Optional[str]:
   """
   Resize image if it exceeds size limit
  
   Args:
       image_path: Path to image file
       max_size_mb: Maximum size in MB
       quality: JPEG quality (1-100)
      
   Returns:
       Path to resized image (or None if no resize needed)
   """
   size_mb = get_image_size_mb(image_path)
  
   if size_mb <= max_size_mb:
       return None  # No resize needed
  
   # Open image
   with Image.open(image_path) as img:
       # Calculate scale factor
       scale = (max_size_mb / size_mb) ** 0.5
       new_width = int(img.width * scale)
       new_height = int(img.height * scale)
      
       # Resize
       resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
      
       # Generate output path
       base, ext = os.path.splitext(image_path)
       output_path = f"{base}_resized{ext}"
      
       # Save with compression
       if ext.lower() in ['.jpg', '.jpeg']:
           resized.save(output_path, 'JPEG', quality=quality, optimize=True)
       elif ext.lower() == '.png':
           resized.save(output_path, 'PNG', optimize=True)
       else:
           resized.save(output_path, quality=quality, optimize=True)
      
       return output_path




def create_thumbnail(
   image_path: str,
   thumbnail_size: tuple = (256, 256),
   output_path: Optional[str] = None
) -> str:
   """
   Create thumbnail of image
  
   Args:
       image_path: Path to source image
       thumbnail_size: Thumbnail size (width, height)
       output_path: Optional output path
      
   Returns:
       Path to thumbnail
   """
   with Image.open(image_path) as img:
       img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
      
       if output_path is None:
           base, ext = os.path.splitext(image_path)
           output_path = f"{base}_thumb{ext}"
      
       img.save(output_path)
  
   return output_path




def batch_validate_images(image_paths: List[str]) -> List[Dict[str, Any]]:
   """
   Validate multiple images and return detailed results
  
   Args:
       image_paths: List of image paths
      
   Returns:
       List of validation results for each image
   """
   results = []
  
   for image_path in image_paths:
       result = {
           "path": image_path,
           "valid": False,
           "errors": [],
           "warnings": [],
           "info": None
       }
      
       # Check existence
       if not os.path.exists(image_path):
           result["errors"].append("File not found")
           results.append(result)
           continue
      
       # Check format
       ext = os.path.splitext(image_path)[1].lower()
       if ext not in SUPPORTED_FILE_EXTENSIONS:
           result["errors"].append(f"Unsupported format: {ext}")
           results.append(result)
           continue
      
       # Check size
       size_mb = get_image_size_mb(image_path)
       if size_mb > MAX_IMAGE_SIZE_MB:
           result["errors"].append(f"File too large: {size_mb:.2f}MB (max: {MAX_IMAGE_SIZE_MB}MB)")
       elif size_mb > MAX_IMAGE_SIZE_MB * 0.8:
           result["warnings"].append(f"File near size limit: {size_mb:.2f}MB")
      
       # Get info
       info = get_image_info(image_path)
       result["info"] = info
      
       # Mark as valid if no errors
       result["valid"] = len(result["errors"]) == 0
       results.append(result)
  
   return results




def format_file_size(size_bytes: int) -> str:
   """
   Format file size in human-readable format
  
   Args:
       size_bytes: Size in bytes
      
   Returns:
       Formatted string (e.g., "2.5 MB")
   """
   for unit in ['B', 'KB', 'MB', 'GB']:
       if size_bytes < 1024.0:
           return f"{size_bytes:.2f} {unit}"
       size_bytes /= 1024.0
   return f"{size_bytes:.2f} TB"



