"""
Image Generation Client for Gemini 2.5 Flash Image
Supports text-to-image, image-to-image, multi-image fusion, and sessions
"""


import os
import requests
import base64
from typing import List, Optional, Dict, Any


from config import (
   API_BASE_URL,
   DEFAULT_MODEL,
   DEFAULT_IMAGES_DIR,
   ImageConfig
)
from utils import (
   encode_image_to_base64,
   decode_base64_to_image,
   validate_reference_images,
   generate_filename,
   organize_output_path,
   get_image_info
)
from session_manager import Session, SessionManager, SessionConfig




class ImageGenerationClient:
   """
   Client for Gemini 2.5 Flash Image generation
  
   Features:
   - Text-to-Image generation
   - Image-to-Image editing
   - Multi-image fusion (up to 3 reference images)
   - Session management for character consistency
   - 10 aspect ratios supported
   """
  
   def __init__(
       self,
       api_key: str,
       base_url: str = API_BASE_URL,
       model: str = DEFAULT_MODEL,
       default_config: Optional[ImageConfig] = None
   ):
       """
       Initialize image generation client
      
       Args:
           api_key: Google API key
           base_url: API base URL
           model: Model name (default: gemini-2.5-flash-image-preview)
           default_config: Default image generation configuration
       """
       self.api_key = api_key
       self.base_url = base_url.rstrip('/')
       self.model = model
       self.default_config = default_config or ImageConfig()
       self.session_manager = SessionManager()
  
   def generate(
       self,
       prompt: str,
       config: Optional[ImageConfig] = None,
       reference_images: Optional[List[str]] = None,
       save_to: Optional[str] = None
   ) -> Dict[str, Any]:
       """
       Generate image(s) from text prompt
      
       Args:
           prompt: Text description of the image to generate
           config: Image generation configuration (uses default if None)
           reference_images: Optional list of reference image paths (max 3)
           save_to: Optional output path (auto-generated if None)
          
       Returns:
           Dict with generation results
       """
       config = config or self.default_config
      
       # If num_images > 1, make multiple API calls
       if config.num_images > 1:
           print(f"📊 Generating {config.num_images} images (making {config.num_images} API calls)...")
           all_generated = []
          
           for img_num in range(config.num_images):
               print(f"  • Generating image {img_num + 1}/{config.num_images}...", end=" ", flush=True)
              
               # Determine save path for this image
               current_save_to = None
               if save_to:
                   base, ext = os.path.splitext(save_to)
                   current_save_to = f"{base}_{img_num + 1}{ext}"
              
               # Make single API call
               single_result = self._generate_single(
                   prompt=prompt,
                   config=config,
                   reference_images=reference_images,
                   save_to=current_save_to
               )
              
               if single_result.get("success"):
                   all_generated.extend(single_result.get("generated_images", []))
                   print("✅")
               else:
                   print(f"❌ {single_result.get('error')}")
          
           if all_generated:
               return {
                   "success": True,
                   "prompt": prompt,
                   "config": {
                       "aspect_ratio": config.aspect_ratio,
                       "num_images": config.num_images
                   },
                   "reference_images": reference_images or [],
                   "generated_images": all_generated
               }
           else:
               return {
                   "success": False,
                   "error": "Failed to generate any images"
               }
       else:
           # Single image generation
           return self._generate_single(prompt, config, reference_images, save_to)
  
   def _generate_single(
       self,
       prompt: str,
       config: ImageConfig,
       reference_images: Optional[List[str]] = None,
       save_to: Optional[str] = None
   ) -> Dict[str, Any]:
       """
       Internal method to generate a single image
       """
       try:
           # Build request payload for Gemini API
           contents = []
          
           # Add reference images if provided
           if reference_images:
               # Validate reference images
               validation = validate_reference_images(reference_images)
               if not validation["valid"]:
                   return {
                       "success": False,
                       "error": f"Invalid reference images: {validation['errors']}"
                   }
              
               # Build parts with images
               parts = []
              
               # Add reference images as inline_data
               for image_path in validation["valid_images"]:
                   base64_data, mime_type = encode_image_to_base64(image_path)
                   parts.append({
                       "inline_data": {
                           "mime_type": mime_type,
                           "data": base64_data
                       }
                   })
              
               # Add text prompt
               parts.append({"text": prompt})
              
               contents.append({"parts": parts})
           else:
               # Text-only prompt
               contents.append({
                   "parts": [{"text": prompt}]
               })
          
           # Build generation config with aspect ratio
           generation_config = {
               "imageConfig": {
                   "aspectRatio": config.aspect_ratio
               }
           }
          
           # Build full request payload
           payload = {
               "contents": contents,
               "generationConfig": generation_config
           }
          
           # Make API request
           url = f"{self.base_url}/models/{self.model}:generateContent"
           headers = {
               "x-goog-api-key": self.api_key,
               "Content-Type": "application/json"
           }
          
           response = requests.post(url, json=payload, headers=headers)
           response.raise_for_status()
           response_data = response.json()
          
           # Extract generated images from response
           generated_files = []
          
           if "candidates" in response_data and len(response_data["candidates"]) > 0:
               candidate = response_data["candidates"][0]
               if "content" in candidate and "parts" in candidate["content"]:
                   for i, part in enumerate(candidate["content"]["parts"]):
                       # Check for both camelCase and snake_case
                       if "inlineData" in part or "inline_data" in part:
                           # Get base64 data (try both naming conventions)
                           inline_data = part.get("inlineData") or part.get("inline_data")
                           base64_string = inline_data.get("data")
                          
                           # Generate output path
                           if save_to:
                               # Make sure save_to is an absolute path or in the output directory
                               if os.path.isabs(save_to):
                                   output_path = save_to
                               else:
                                   # Relative path - put it in the default output directory
                                   output_dir = config.output_dir
                                   if config.organize_by_date:
                                       from datetime import datetime
                                       date_folder = datetime.now().strftime("%Y%m%d")
                                       output_dir = os.path.join(output_dir, date_folder)
                                   os.makedirs(output_dir, exist_ok=True)
                                   output_path = os.path.join(output_dir, save_to)
                              
                               # Handle multiple images
                               parts_with_images = [p for p in candidate["content"]["parts"] if "inlineData" in p or "inline_data" in p]
                               if len(parts_with_images) > 1:
                                   base, ext = os.path.splitext(output_path)
                                   output_path = f"{base}_{i+1}{ext}"
                           else:
                               filename = generate_filename(
                                   prefix="generated",
                                   suffix=f"{i+1}" if len(candidate["content"]["parts"]) > 1 else "",
                                   extension=config.output_format
                               )
                               output_path = organize_output_path(
                                   config.output_dir,
                                   filename,
                                   config.organize_by_date
                               )
                          
                           # Decode and save
                           saved_path = decode_base64_to_image(base64_string, output_path)
                          
                           # Get image info
                           info = get_image_info(saved_path)
                          
                           generated_files.append({
                               "file_path": saved_path,
                               "info": info
                           })
          
           if not generated_files:
               return {
                   "success": False,
                   "error": "No images generated in response"
               }
          
           return {
               "success": True,
               "prompt": prompt,
               "config": {
                   "aspect_ratio": config.aspect_ratio,
                   "num_images": config.num_images
               },
               "reference_images": reference_images or [],
               "generated_images": generated_files,
               "response": response_data
           }
          
       except requests.exceptions.RequestException as e:
           return {
               "success": False,
               "error": f"API request failed: {str(e)}",
               "prompt": prompt
           }
       except Exception as e:
           return {
               "success": False,
               "error": str(e),
               "prompt": prompt
           }
  
   def generate_with_reference(
       self,
       prompt: str,
       reference_images: List[str],
       config: Optional[ImageConfig] = None
   ) -> Dict[str, Any]:
       """
       Generate image with reference images (editing, fusion, consistency)
      
       Args:
           prompt: Text description or editing instruction
           reference_images: List of reference image paths (1-3 images)
           config: Image generation configuration
          
       Returns:
           Dict with generation results
       """
       return self.generate(
           prompt=prompt,
           config=config,
           reference_images=reference_images
       )
  
   def edit_image(
       self,
       image_path: str,
       edit_prompt: str,
       config: Optional[ImageConfig] = None
   ) -> Dict[str, Any]:
       """
       Edit an existing image with natural language instructions
      
       Args:
           image_path: Path to image to edit
           edit_prompt: Natural language editing instruction
           config: Image generation configuration
          
       Returns:
           Dict with generation results
       """
       return self.generate_with_reference(
           prompt=edit_prompt,
           reference_images=[image_path],
           config=config
       )
  
   def fuse_images(
       self,
       image_paths: List[str],
       fusion_prompt: str,
       config: Optional[ImageConfig] = None
   ) -> Dict[str, Any]:
       """
       Fuse multiple images together (max 3)
      
       Args:
           image_paths: List of image paths to fuse (2-3 images)
           fusion_prompt: Description of how to fuse the images
           config: Image generation configuration
          
       Returns:
           Dict with generation results
       """
       if len(image_paths) < 2:
           return {
               "success": False,
               "error": "Need at least 2 images to fuse"
           }
      
       return self.generate_with_reference(
           prompt=fusion_prompt,
           reference_images=image_paths,
           config=config
       )
  
   # ========================================================================
   # Session-based generation for character consistency
   # ========================================================================
  
   def create_session(self, config: Optional[SessionConfig] = None) -> Session:
       """
       Create new session for maintaining context
      
       Args:
           config: Session configuration
          
       Returns:
           New Session object
       """
       return self.session_manager.create_session(config=config)
  
   def load_session(self, session_id: str) -> Session:
       """
       Load existing session
      
       Args:
           session_id: Session identifier
          
       Returns:
           Loaded Session object
       """
       return self.session_manager.load_session(session_id)
  
   def generate_with_session(
       self,
       session: Session,
       prompt: str,
       config: Optional[ImageConfig] = None,
       reference_images: Optional[List[str]] = None,
       use_session_history: bool = True
   ) -> Dict[str, Any]:
       """
       Generate image within a session to maintain context
      
       Args:
           session: Session object
           prompt: Text prompt
           config: Image generation configuration
           reference_images: Optional reference images
           use_session_history: Whether to include session history in API call
          
       Returns:
           Dict with generation results
       """
       config = config or self.default_config
      
       # Add user message to session
       session.add_message("user", prompt)
      
       # Build messages for API
       if use_session_history and len(session.messages) > 1:
           # Use session history for context
           api_messages = session.get_messages_for_api()
       else:
           # Just current prompt
           api_messages = [{"role": "user", "content": prompt}]
      
       try:
           # Build Gemini API request
           contents = []
          
           # Add reference images if provided
           if reference_images:
               validation = validate_reference_images(reference_images)
               if not validation["valid"]:
                   return {
                       "success": False,
                       "error": f"Invalid reference images: {validation['errors']}"
                   }
              
               # Add references to session
               for image_path in validation["valid_images"]:
                   session.add_reference_image(image_path)
              
               # Build parts with images
               parts = []
               for image_path in validation["valid_images"]:
                   base64_data, mime_type = encode_image_to_base64(image_path)
                   parts.append({
                       "inline_data": {
                           "mime_type": mime_type,
                           "data": base64_data
                       }
                   })
              
               parts.append({"text": prompt})
               contents.append({"parts": parts})
           else:
               contents.append({
                   "parts": [{"text": prompt}]
               })
          
           # Build generation config
           generation_config = {
               "imageConfig": {
                   "aspectRatio": config.aspect_ratio
               }
           }
          
           payload = {
               "contents": contents,
               "generationConfig": generation_config
           }
          
           # Make API request
           url = f"{self.base_url}/models/{self.model}:generateContent"
           headers = {
               "x-goog-api-key": self.api_key,
               "Content-Type": "application/json"
           }
          
           response = requests.post(url, json=payload, headers=headers)
           response.raise_for_status()
           response_data = response.json()
          
           # Extract and save images
           generated_files = []
          
           if "candidates" in response_data and len(response_data["candidates"]) > 0:
               candidate = response_data["candidates"][0]
               if "content" in candidate and "parts" in candidate["content"]:
                   for i, part in enumerate(candidate["content"]["parts"]):
                       # Check for both camelCase and snake_case
                       if "inlineData" in part or "inline_data" in part:
                           inline_data = part.get("inlineData") or part.get("inline_data")
                           base64_string = inline_data.get("data")
                          
                           # Generate filename in session folder
                           filename = generate_filename(
                               prefix=f"gen_{session.metadata['generation_count']+1}",
                               suffix=f"{i+1}" if len(candidate["content"]["parts"]) > 1 else "",
                               extension=config.output_format
                           )
                          
                           # Save to session images folder
                           output_path = os.path.join(session.session_path, "images", filename)
                           os.makedirs(os.path.dirname(output_path), exist_ok=True)
                          
                           saved_path = decode_base64_to_image(base64_string, output_path)
                          
                           # Add to session
                           session.add_generated_image(saved_path, copy_to_session=False)
                          
                           info = get_image_info(saved_path)
                           generated_files.append({
                               "file_path": saved_path,
                               "info": info
                           })
              
               # Add assistant message to session
               session.add_message("assistant", f"Generated {len(generated_files)} image(s)")
               session.increment_generation_count()
               session.save()
              
               return {
                   "success": True,
                   "session_id": session.session_id,
                   "prompt": prompt,
                   "config": {
                       "aspect_ratio": config.aspect_ratio,
                       "num_images": config.num_images
                   },
                   "reference_images": reference_images or [],
                   "generated_images": generated_files,
                   "session_summary": session.get_summary(),
                   "response": response
               }
           else:
               return {
                   "success": False,
                   "error": "No images generated in response",
                   "session_id": session.session_id
               }
              
       except Exception as e:
           return {
               "success": False,
               "error": str(e),
               "session_id": session.session_id,
               "prompt": prompt
           }
  
   def list_sessions(self) -> List[Dict[str, Any]]:
       """List all available sessions"""
       return self.session_manager.list_sessions()
  
   def delete_session(self, session_id: str):
       """Delete a session"""
       self.session_manager.delete_session(session_id)
  
   def cleanup_old_sessions(self, hours: int = 24) -> int:
       """
       Clean up sessions older than specified hours
      
       Returns:
           Number of sessions deleted
       """
       return self.session_manager.cleanup_old_sessions(hours)






