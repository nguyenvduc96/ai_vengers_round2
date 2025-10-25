#!/usr/bin/env python3
"""
Test script for image editing using Gemini 2.5 Flash Image.
Takes an input image and applies edits based on a text prompt.
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
# CONFIGURATION SECTION - Modify these for different editing tasks
# =============================================================================


# Input Image Path
INPUT_IMAGE = "/Volumes/vipman/ai_vengers_round2/generated/20251025/generated_20251025_181806_2.png"


# Editing Prompt - Describe what changes you want to make
EDIT_PROMPT = """Delete all text in the image"""


# Output Configuration
OUTPUT_PREFIX = "edited_image_delete"  # Prefix for saved image files


# Aspect Ratio - Use "original" to maintain input image aspect ratio, or specify: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
ASPECT_RATIO = "2:3"  # Set to match your image or desired output


# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
   """Main execution function."""
  
   print("=" * 80)
   print("✏️  IMAGE EDITING WITH GEMINI 2.5 FLASH IMAGE")
   print("=" * 80)
   print(f"\nInput Image: {INPUT_IMAGE}")
   print(f"Aspect Ratio: {ASPECT_RATIO}")
   print(f"Output Prefix: {OUTPUT_PREFIX}")
   print(f"\n📝 Edit Prompt:")
   print(f"   {EDIT_PROMPT}")
   print("\n" + "=" * 80)
  
   # Check if input image exists
   if not os.path.exists(INPUT_IMAGE):
       print(f"\n❌ Error: Input image not found: {INPUT_IMAGE}")
       print("Please check the file path and try again.")
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
      
       # Edit image
       print(f"\n✏️  Editing image...")
       print(f"📝 Prompt length: {len(EDIT_PROMPT)} characters")
       print("\n⏳ This may take 10-30 seconds...\n")
      
       # Create image config
       image_config = ImageConfig(
           aspect_ratio=ASPECT_RATIO,
           num_images=1
       )
      
       # Call edit_image method (which uses generate with reference)
       result = client.edit_image(
           image_path=INPUT_IMAGE,
           edit_prompt=EDIT_PROMPT,
           config=image_config
       )
      
       # Display results
       print("\n" + "=" * 80)
      
       if result.get("success"):
           print("✅ EDITING SUCCESSFUL!")
           print("=" * 80)
          
           for img in result.get("generated_images", []):
               print(f"\n📁 Edited image:")
               print(f"  📄 File: {img['file_path']}")
               print(f"  📐 Size: {img['info']['width']}x{img['info']['height']}")
               print(f"  💾 File size: {img['info']['size_mb']} MB")
               print(f"\n🔍 Compare:")
               print(f"  Original: {INPUT_IMAGE}")
               print(f"  Edited:   {img['file_path']}")
       else:
           print("❌ EDITING FAILED")
           print("=" * 80)
           print(f"\n⚠️  Error: {result.get('error', 'Unknown error')}")
      
       print("\n" + "=" * 80)
       print("💡 TIP: You can chain edits by using the output as input for next edit")
       print("=" * 80)
      
   except FileNotFoundError as e:
       print(f"\n❌ File Error: {e}")
       print("Make sure the input image exists and image_client.py is available")
       sys.exit(1)
   except Exception as e:
       print(f"\n❌ Error during editing: {e}")
       import traceback
       traceback.print_exc()
       sys.exit(1)




if __name__ == "__main__":
   main()






