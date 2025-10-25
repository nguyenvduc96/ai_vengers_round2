#!/usr/bin/env python3
"""
Test script for image generation with reference images using Gemini 2.5 Flash Image.
Generate new images based on text prompt + 1-3 reference images for style/content consistency.
"""


import os
import sys
from pathlib import Path
from datetime import datetime


# Add parent directory to path to import image_client
sys.path.insert(0, str(Path(__file__).parent))


from image_client import ImageGenerationClient
from config import ImageConfig




# =============================================================================
# CONFIGURATION SECTION - Modify these for different generation tasks
# =============================================================================


# Reference Images (1-3 images)
REFERENCE_IMAGES = [
   "/Users/ngoan.pham/Ngoan/ai_vengers/image_gen/data/566640714_1495921688128454_257114238580902529_n.png",
   "/Users/ngoan.pham/Ngoan/ai_vengers/image_gen/generated/20251024/generated_20251024_220200.png"
]


# Generation Prompt
PROMPT = """Merge the text into the image, the text as the subtitle below the title AI VENGERS with the size as the subtitle and not hide everything, keeping its original font, and style.




"""


# Output Configuration
OUTPUT_PREFIX = "comic_cover_vietnam_national_day"  # Prefix for saved image files


# Aspect Ratio Options: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
ASPECT_RATIO = "2:3"  # Portrait format


# Number of variations to generate (1-10)
NUM_IMAGES = 1  # Generate 1 image


# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
   """Main execution function."""
  
   print("=" * 80)
   print("🎨 IMAGE GENERATION WITH REFERENCE IMAGES")
   print("=" * 80)
   print(f"\nReference Images ({len(REFERENCE_IMAGES)}):")
   for i, ref in enumerate(REFERENCE_IMAGES, 1):
       print(f"  {i}. {ref}")
   print(f"\nAspect Ratio: {ASPECT_RATIO}")
   print(f"Number of Images: {NUM_IMAGES}")
   print(f"Output Prefix: {OUTPUT_PREFIX}")
   print(f"\n📝 Prompt:")
   print(f"   {PROMPT}")
   print("\n" + "=" * 80)
  
   # Validate reference images
   missing_images = []
   for ref in REFERENCE_IMAGES:
       if not os.path.exists(ref):
           missing_images.append(ref)
  
   if missing_images:
       print(f"\n❌ Error: Reference image(s) not found:")
       for img in missing_images:
           print(f"   - {img}")
       print("\nPlease check the file paths and try again.")
       sys.exit(1)
  
   if len(REFERENCE_IMAGES) > 3:
       print(f"\n❌ Error: Maximum 3 reference images allowed, you provided {len(REFERENCE_IMAGES)}")
       sys.exit(1)
  
   if len(REFERENCE_IMAGES) == 0:
       print(f"\n❌ Error: At least 1 reference image is required")
       sys.exit(1)
  
   # Get API key from environment
   api_key = os.environ.get("GEMINI_API_KEY")
  
   if not api_key:
       print("\n⚠️  GEMINI_API_KEY environment variable not set")
       api_key = input("Enter your Google API key: ").strip()
      
       if not api_key:
           print("❌ Error: API key is required")
           sys.exit(1)
  
   try:
       # Initialize client
       print("\n🔧 Initializing Image Generation Client...")
       client = ImageGenerationClient(api_key=api_key)
       print("✅ Client initialized successfully")
      
       # Generate image with references
       print(f"\n🎨 Generating image with {len(REFERENCE_IMAGES)} reference(s)...")
       print(f"📝 Prompt length: {len(PROMPT)} characters")
       print("\n⏳ This may take 10-30 seconds...\n")
      
       # Create image config
       image_config = ImageConfig(
           aspect_ratio=ASPECT_RATIO,
           num_images=NUM_IMAGES
       )
      
       # Generate with references
       result = client.generate_with_reference(
           prompt=PROMPT,
           reference_images=REFERENCE_IMAGES,
           config=image_config
       )
      
       # Display results
       print("\n" + "=" * 80)
      
       if result.get("success"):
           print("✅ GENERATION SUCCESSFUL!")
           print("=" * 80)
          
           for idx, img in enumerate(result.get("generated_images", []), 1):
               print(f"\n📁 Generated image #{idx}:")
               print(f"  📄 File: {img['file_path']}")
               print(f"  📐 Size: {img['info']['width']}x{img['info']['height']}")
               print(f"  💾 File size: {img['info']['size_mb']} MB")
          
           print(f"\n🔍 Reference images used:")
           for i, ref in enumerate(REFERENCE_IMAGES, 1):
               print(f"  {i}. {os.path.basename(ref)}")
       else:
           print("❌ GENERATION FAILED")
           print("=" * 80)
           print(f"\n⚠️  Error: {result.get('error', 'Unknown error')}")
      
       print("\n" + "=" * 80)
       print("💡 TIPS:")
       print("  • Use 1 reference for style/character consistency")
       print("  • Use 2-3 references to combine elements or styles")
       print("  • Be specific about what to take from each reference")
       print("  • Try different prompts to explore variations")
       print("=" * 80)
      
   except FileNotFoundError as e:
       print(f"\n❌ File Error: {e}")
       print("Make sure all reference images exist and image_client.py is available")
       sys.exit(1)
   except Exception as e:
       print(f"\n❌ Error during generation: {e}")
       import traceback
       traceback.print_exc()
       sys.exit(1)




if __name__ == "__main__":
   main()



