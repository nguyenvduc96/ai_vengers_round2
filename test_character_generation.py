#!/usr/bin/env python3
"""
Test script for character reference sheet generation using Gemini 2.5 Flash Image.
This script can be adapted for different character prompts.
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
# CONFIGURATION SECTION - Modify these for different prompts
# =============================================================================

# key: sk-hj_b8UR4iNeuFX62E5gj1g 
# Output Configuration
OUTPUT_PREFIX = "character_sheet_Mai"  # Prefix for saved image files


# Aspect Ratio Options: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
ASPECT_RATIO = "2:3"  # Portrait format for character sheet


# Number of variations to generate (1-10)
NUM_IMAGES = 1


# =============================================================================
# PROMPT SECTION - Modify this for different characters
# =============================================================================


PROMPT = """Create a detailed character reference sheet for \"Mai\" of Vietnamese ethnicity for comic book use.\n\nCHARACTER IDENTITY:\n- Name: Mai\n- Role: Protagonist\n- Nationality/Ethnicity: Vietnamese\n\nMAIN VIEW - Full body standing neutral pose:\n- Height/Build: 160cm, slim build\n- Skin tone: Light-medium warm tone\n- Hair: Natural black, shoulder-length, straight\n- Eyes: Dark brown, large and expressive\n- Expression: Neutral/friendly\n\nClothing:\n- Casual homewear: simple t-shirt and shorts.\n\nADDITIONAL VIEWS:\n- Expression samples: Shocked, Horrified, Disappointed, Sad.\n\nSTYLE:\n- Art style: Modern Manga\n- Color: Full color with shading\n- Background: White\n\nCRITICAL REQUIREMENTS:\n- Character must appear authentically as Vietnamese\n- Physical features accurate to ethnicity."""

          

# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main():
   """Main execution function."""
  
   print("=" * 80)
   print("🎨 CHARACTER REFERENCE SHEET GENERATION TEST")
   print("=" * 80)
   print(f"\nAspect Ratio: {ASPECT_RATIO}")
   print(f"Number of Images: {NUM_IMAGES}")
   print(f"Output Prefix: {OUTPUT_PREFIX}")
   print("\n" + "=" * 80)
  
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
      
       # Generate image
       print(f"\n🎨 Generating character reference sheet...")
       print(f"📝 Prompt length: {len(PROMPT)} characters")
       print("\n⏳ This may take 10-30 seconds...\n")
      
       # Create image config
       image_config = ImageConfig(
           aspect_ratio=ASPECT_RATIO,
           num_images=NUM_IMAGES
       )
      
       result = client.generate(
           prompt=PROMPT,
           config=image_config,
           save_to=f"{OUTPUT_PREFIX}.png"
       )
      
       # Display results
       print("\n" + "=" * 80)
      
       if result.get("success"):
           print("✅ GENERATION SUCCESSFUL!")
           print("=" * 80)
          
           for img in result.get("generated_images", []):
               print(f"\n📁 Generated image:")
               print(f"  📄 File: {img['file_path']}")
               print(f"  📐 Size: {img['info']['width']}x{img['info']['height']}")
               print(f"  💾 File size: {img['info']['size_mb']} MB")
       else:
           print("❌ GENERATION FAILED")
           print("=" * 80)
           print(f"\n⚠️  Error: {result.get('error', 'Unknown error')}")
      
       print("\n" + "=" * 80)
       print("💡 TIP: Use generated images as references for panel generation")
       print("=" * 80)
      
   except FileNotFoundError as e:
       print(f"\n❌ File Error: {e}")
       print("Make sure all required files are in the image_gen folder")
       sys.exit(1)
   except Exception as e:
       print(f"\n❌ Error during generation: {e}")
       import traceback
       traceback.print_exc()
       sys.exit(1)




if __name__ == "__main__":
   main()



