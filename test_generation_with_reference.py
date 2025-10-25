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
   "/Volumes/vipman/ai_vengers_round2/generated/20251025/character_sheet_Mai.png",
#    "/Volumes/vipman/ai_vengers_round2/generated/20251025/character_sheet_Mai.png",
]


# Generation Prompt
# PROMPT = """Create a single, highly dramatic comic book panel in a Modern Manga style with a Vietnamese cultural context.\n\nPANEL SPECIFICATIONS:\n- Aspect ratio: 2:3\n- Cultural setting: Modern Vietnam\n\nCAMERA:\n- Angle: Medium close-up\n- Perspective: Slightly high angle, looking down to emphasize vulnerability.\n\nSCENE: The entire story is told in this one moment of devastating realization. A teenage girl, Mai, sits frozen in her dark bedroom, illuminated only by the cold, blue-white light of her laptop screen. The screen itself prominently displays a stark \"404 Not Found\" error message.\n\nCHARACTER:\nMai (Vietnamese):\n- Use the uploaded character reference.\n- Action/Pose: She is sitting rigidly, staring blankly at the screen. Her body language is defeated. One hand is limp, having just dropped her smartphone onto the bed beside her.\n- Expression: A look of utter shock, disbelief, and dawning horror. Her eyes are wide, and a single tear is beginning to form.\n- Position: Centered, but slightly off-balance to create unease.\n\nSETTING/BACKGROUND:\n- Her bedroom is dark and filled with shadows. K-pop posters on the wall are visible but obscured, adding to the sense of isolation.\n- Visual effect: Faint, glitchy, holographic images of the K-pop lightstick she dreamed of buying are dissolving into pixels around her, symbolizing her shattered hopes.\n\nLIGHTING AND MOOD:\n- Light source: The harsh, unforgiving glow from the laptop screen is the only light.\n- Color palette: Dominated by deep blues, blacks, and greys, with the stark white of the screen cutting through the darkness.\n- Atmosphere: Crushing disappointment, silence, and solitude.\n- Overall feeling: The heartbreaking moment of a harsh lesson learned.\n\nTEXT ELEMENTS (in Vietnamese):\n- Internal Monologue (at the bottom, in a shaky, faint font):\n\"Mình... bị lừa rồi sao...?\"\n\nCRITICAL REQUIREMENTS:\n- Use the uploaded character reference for Mai for consistency.\n- The character must appear authentically Vietnamese.\n- The panel must convey a powerful sense of shock and emotional devastation in a single image.\n- All text must be in Vietnamese. ONLY BLACK and WHITE color"""
# PROMPT = """Create a single, highly dramatic comic book panel in a Modern Manga style with a Vietnamese cultural context.\n\nPANEL SPECIFICATIONS:\n- Aspect ratio: 2:3\n- Cultural setting: Modern Vietnam\n\nCAMERA:\n- Angle: Medium close-up\n- Perspective: Slightly high angle, looking down to emphasize vulnerability.\n\nSCENE: The entire story is told in this one moment of devastating realization. A teenage girl, Mai, sits frozen in her dark bedroom, illuminated only by the cold, blue-white light of her laptop screen. The screen itself prominently displays a stark \"404 Not Found\" error message.\n\nCHARACTER:\nMai (Vietnamese):\n- Use the uploaded character reference.\n- Action/Pose: She is sitting rigidly, staring blankly at the screen. Her body language is defeated. One hand is limp, having just dropped her smartphone onto the bed beside her.\n- Expression: A look of utter shock, disbelief, and dawning horror. Her eyes are wide, and a single tear is beginning to form.\n- Position: Centered, but slightly off-balance to create unease.\n\nSETTING/BACKGROUND:\n- Her bedroom is dark and filled with shadows. K-pop posters on the wall are visible but obscured, adding to the sense of isolation.\n- Visual effect: Faint, glitchy, holographic images of the K-pop lightstick she dreamed of buying are dissolving into pixels around her, symbolizing her shattered hopes.\n\nLIGHTING AND MOOD:\n- Light source: The harsh, unforgiving glow from the laptop screen is the only light.\n- Color palette: Dominated by deep blues, blacks, and greys, with the stark white of the screen cutting through the darkness.\n- Atmosphere: Crushing disappointment, silence, and solitude.\n- Overall feeling: The heartbreaking moment of a harsh lesson learned.\n\nTEXT ELEMENTS (in Vietnamese):\n- Internal Monologue (at the bottom, in a shaky, faint font):\n\"Mình... bị lừa rồi sao...?\"\n\nCRITICAL REQUIREMENTS:\n- Use the uploaded character reference for Mai for consistency.\n- The character must appear authentically Vietnamese.\n- The panel must convey a powerful sense of shock and emotional devastation in a single image.\n- All text must be in Vietnamese. ONLY BLACK and WHITE color"""
PROMPT="Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot, eye-level.\n\nSCENE: A cozy, slightly messy Vietnamese kitchen in the evening. Mai is pleading with her mom, who is busy cooking.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. She is clasping her hands together, making a cute begging face.\n- Mai's Mom (Vietnamese, around 45 years old, gentle face but looks busy): She is chopping vegetables at the counter, looking over her shoulder at Mai with a mix of exasperation and affection.\n\nSETTING/BACKGROUND: A warm kitchen with common Vietnamese cooking ingredients on the counter. The atmosphere is homey.\n\nLIGHTING AND MOOD: Warm light from the kitchen overhead lamp. The mood is a typical, warm family interaction.\n\nTEXT ELEMENTS (in Vietnamese):\n- Speech Balloon 1 (near Mai): \"Mẹ ơi, cho con mua cái này nhé? Đang giảm giá lớn lắm ạ! Bạn con ai cũng có rồi...\"\n- Speech Balloon 2 (near Mom): \"Lại đồ thần tượng gì chứ... Thôi được rồi, nhưng chỉ lần này thôi đấy nhé!\"\n\nCRITICAL REQUIREMENTS: Use uploaded reference for Mai. The setting should feel like an authentic Vietnamese home. All text in Vietnamese."
PROMPT= "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: High-angle close-up, looking down at Mai and her phone.\n\nSCENE: Mai is sitting on her bed in her bedroom, which has K-pop posters on the wall. She is intensely focused on her phone, entering payment information.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. Her expression is concentrated and a little anxious as she types on her phone.\n\nSETTING/BACKGROUND: Her bedroom decorated with K-pop merchandise. The focus is on the action of entering details into the phone.\n\nLIGHTING AND MOOD: The room is lit by a desk lamp, with the phone's screen casting a glow on her face. The mood is one of suspense and anticipation.\n\nTEXT ELEMENTS (in Vietnamese):\n- Caption Box (bottom, internal thought style): \"Chỉ cần vài cú nhấp chuột...\"\n- Sound Effect (near her fingers): \"*click* *click*\"\n\nCRITICAL REQUIREMENTS: Use uploaded character reference for Mai. Her room should reflect her personality. All text in Vietnamese."

PROMPT="Create a Modern Manga style comic panel. Aspect ratio: 2:3.\n\nCAMERA: Extreme close-up of a smartphone screen.\n\nSCENE: The entire panel is the phone screen. It displays a brightly colored, celebratory message.\n\nSETTING/BACKGROUND: The screen shows a confirmation page with confetti and star graphics around the central text.\n\nLIGHTING AND MOOD: Bright and cheerful light emitting from the screen. The mood is successful and happy.\n\nTEXT ELEMENTS (in Vietnamese):\n- Text on screen (center, large, bold, celebratory font): \"ĐẶT HÀNG THÀNH CÔNG!\"\n\nCRITICAL REQUIREMENTS: The text must be in Vietnamese and be the sole focus of the panel. The design should look like a generic success message from an e-commerce site."
PROMPT = "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot, eye-level.\n\nSCENE: Mai is on her bed, celebrating joyfully but quietly. Small, dreamy bubbles around her show the glowing K-pop lightstick she just ordered.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. She has her arms raised in a victory pose, a huge, happy smile on her face, with her eyes closed in bliss.\n\nSETTING/BACKGROUND: Her bedroom is softly lit. The focus is on her pure joy.\n\nLIGHTING AND MOOD: Soft, dreamy lighting. The color palette incorporates pastel pinks and purples to enhance the dreamy, happy mood.\n\nTEXT ELEMENTS:\n- Thought Bubble (near Mai, excited script font): \"Yesss!\"\n\nCRITICAL REQUIREMENTS: Use uploaded character reference for Mai. The emotion of pure happiness should be the central focus. The text should be presented as an internal thought."
PROMPT =  "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Montage of small, overlapping frames showing the passage of time.\n\nSCENE: Show Mai in various daily activities (at school, eating dinner, watching TV). In each small frame, she is shown glancing at her phone expectantly. Her expression shifts from hopeful to impatient across the montage.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. Her actions are routine, but her focus is always on her phone.\n\nSETTING/BACKGROUND: Various settings of her daily life.\n\nLIGHTING AND MOOD: The color palette should gradually become more muted and greyish to reflect her growing anxiety.\n\nTEXT ELEMENTS (in Vietnamese):\n- Caption Box (top of panel): \"Một tuần sau...\"\n\nCRITICAL REQUIREMENTS: Use uploaded character reference for Mai. The panel must effectively convey the passage of time and Mai's increasing impatience."
PROMPT =  "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot from the side.\n\nSCENE: Mai is sitting at her desk in her bedroom, anxiously typing on her laptop. The room feels tense.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. Her expression is worried and focused on the laptop screen.\n\nSETTING/BACKGROUND: Her bedroom, but the atmosphere is heavy.\n\nLIGHTING AND MOOD: The main light is the cold glow from the laptop screen, casting shadows in the room. The color palette is cool with blues and greys. The mood is ominous.\n\nTEXT ELEMENTS (in Vietnamese):\n- Thought Bubble (top): \"Tại sao vẫn chưa có thông tin giao hàng nhỉ? Để mình kiểm tra lại trang web...\"\n- Sound Effect (near keyboard): \"*tap* *tap* *tap*\"\n\nCRITICAL REQUIREMENTS: Use uploaded character reference. The sense of foreboding and anxiety should be clear. All text in Vietnamese."
PROMPT= "Create a Modern Manga style comic panel. Aspect ratio: 2:3.\n\nCAMERA: Extreme close-up of a laptop screen.\n\nSCENE: The entire panel is the laptop screen, displaying a clear browser error message.\n\nSETTING/BACKGROUND: A standard \"404 Not Found\" or \"This site can't be reached\" page. The design should be stark and impersonal.\n\nLIGHTING AND MOOD: The cold, flat light of a computer screen. The mood is empty and disappointing.\n\nTEXT ELEMENTS:\n- Text on screen (center, standard browser font): \"404 Not Found\"\n\nCRITICAL REQUIREMENTS: The error message must be the sole focus. The feeling should be one of finality and disappointment."
PROMPT = "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot from a slightly high angle.\n\nSCENE: Mai is frozen in front of her laptop, which still shows the error screen. Her face is pale with shock. Her phone is depicted mid-air, having just slipped from her grasp and is about to land on her bed.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. Her expression is one of utter shock and dawning horror. Her body language is limp and defeated.\n\nSETTING/BACKGROUND: Her bedroom now feels cold and empty.\n\nLIGHTING AND MOOD: The cold light from the laptop screen is the only significant light source, illuminating her stunned face. The color palette is desaturated blue and grey. The mood is one of devastation.\n\nTEXT ELEMENTS (in Vietnamese):\n- Thought Bubble (bottom of panel, in a shaky, thin font): \"Mình... bị lừa rồi sao...?\"\n\nCRITICAL REQUIREMENTS: Use uploaded character reference. The panel must capture the precise moment of heartbreaking realization. All text in Vietnamese."
PROMPT = "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot, eye-level.\n\nSCENE: Mai is crying into a pillow on her bed. Her mom sits beside her, gently patting her back in a comforting gesture.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. Her face is hidden, but her shoulders are shaking from crying.\n- Mai's Mom: Sits next to Mai, with a gentle, loving, and empathetic expression.\n\nSETTING/BACKGROUND: Mai's bedroom, lit by soft daylight from the window.\n\nLIGHTING AND MOOD: Soft, natural lighting. The mood is somber but warm and supportive.\n\nTEXT ELEMENTS (in Vietnamese):\n- Speech Balloon (near Mom): \"Không sao đâu con gái. Coi như đây là một bài học. Tiền mất có thể kiếm lại được, quan trọng là con đã nhận ra.\"\n\nCRITICAL REQUIREMENTS: Use uploaded character reference for Mai. The scene must convey a strong sense of motherly comfort and support. All text in Vietnamese."
PROMPT = "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot, straight-on.\n\nSCENE: Mai, An, and Mai's mom are gathered around a laptop at Mai's desk. They are looking at an article or video about identifying online scams.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. In the middle. She has stopped crying and is now paying close attention to the screen.\n- An (Vietnamese): Use uploaded reference. On the left. She is pointing at the screen, explaining something with a knowledgeable expression.\n- Mai's Mom: On the right. She is listening intently with a thoughtful look.\n\nSETTING/BACKGROUND: The laptop screen shows a list of red flags for online scams.\n\nLIGHTING AND MOOD: Neutral, realistic lighting. The mood is serious and educational but supportive.\n\nTEXT ELEMENTS (in Vietnamese):\n- Speech Balloon (near An): \"Đây này, những trang web lừa đảo thường có tên miền lạ, không có thông tin liên lạc rõ ràng, và luôn thúc giục mình thanh toán thật nhanh.\"\n\nCRITICAL REQUIREMENTS: Use uploaded references. The focus is on the collaborative and supportive learning process. All text in Vietnamese."
PROMPT = "Create a Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot from a slightly high angle.\n\nSCENE: Mai and An are working together at a table in the school library, brainstorming ideas in a notebook.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. On the right. She looks determined and energetic, actively writing and drawing in the notebook.\n- An (Vietnamese): Use uploaded reference. On the left. She is looking at the notebook, nodding in agreement and offering suggestions.\n\nSETTING/BACKGROUND: A bright, well-lit school library with bookshelves in the background.\n\nLIGHTING AND MOOD: Bright, natural light from large library windows. The color palette is bright and optimistic. The mood is creative and empowered.\n\nTEXT ELEMENTS (in Vietnamese):\n- Speech Balloon 1 (near Mai): \"Tớ không muốn có bạn nào khác bị lừa như tớ nữa. Chúng mình phải làm gì đó!\"\n- Speech Balloon 2 (near An): \"Ý hay đó! Chúng ta có thể làm một bài đăng tổng hợp các dấu hiệu lừa đảo cho trang của trường.\"\n\nCRITICAL REQUIREMENTS: Use uploaded references. The panel should feel positive and proactive. All text in Vietnamese."
PROMPT =  "Create a Modern Manga style comic panel. Aspect ratio: 2:3.\n\nCAMERA: Close-up on a smartphone screen.\n\nSCENE: The screen shows a well-designed social media post (like an Instagram carousel). The main image has the title \"CÁCH NHẬN BIẾT LỪA ĐẢO ONLINE\" (How to Spot an Online Scam).\n\nSETTING/BACKGROUND: The post graphic is eye-catching and easy to read, with bullet points visible like \"URL Lạ\", \"Giá Quá Rẻ\", \"Thúc Giục Chuyển Khoản\".\n\nLIGHTING AND MOOD: Bright and clear, like a phone screen. The mood is informative and helpful.\n\nTEXT ELEMENTS (in Vietnamese):\n- Text on graphic: Title \"CÁCH NHẬN BIẾT LỪA ĐẢO ONLINE\" and other keywords.\n- Caption on post: \"LƯỚT TRÁI ĐỂ XEM CÁC DẤU HIỆU NHẬN BIẾT!\"\n\nCRITICAL REQUIREMENTS: The social media post must look authentic and be the focus. All text in Vietnamese."
PROMPT =           "Create a final Modern Manga style comic panel. Aspect ratio: 2:3. Cultural setting: Vietnam.\n\nCAMERA: Medium shot from a slightly low angle to make the characters look heroic.\n\nSCENE: Mai and An stand together in the schoolyard, looking confidently at the viewer. Behind them, a large, translucent version of their successful social media post is visible, with 'like' and 'comment' icons floating around it.\n\nCHARACTERS:\n- Mai (Vietnamese): Use uploaded reference. On the left. She holds her phone and has a confident, empowered smile.\n- An (Vietnamese): Use uploaded reference. On the right. She has an arm around Mai's shoulder, smiling proudly.\n\nSETTING/BACKGROUND: The schoolyard is bright and sunny. The background is filled with the visual representation of their positive impact online.\n\nLIGHTING AND MOOD: Bright, warm sunlight. The color palette is vibrant and hopeful. The overall feeling is empowering and triumphant.\n\nTEXT ELEMENTS (in Vietnamese):\n- Caption Box (bottom of panel, inspiring font): \"Hãy là người dùng thông thái trên không gian mạng!\"\n\nCRITICAL REQUIREMENTS: Use uploaded references. The final panel must convey a strong, positive message of empowerment. All text in Vietnamese."

# Output Configuration              "prompt": "Create a Modern Manga style comic panel. Aspect ratio: 2:3.\n\nCAMERA: Close-up on a smartphone screen.\n\nSCENE: The screen shows a well-designed social media post (like an Instagram carousel). The main image has the title \"CÁCH NHẬN BIẾT LỪA ĐẢO ONLINE\" (How to Spot an Online Scam).\n\nSETTING/BACKGROUND: The post graphic is eye-catching and easy to read, with bullet points visible like \"URL Lạ\", \"Giá Quá Rẻ\", \"Thúc Giục Chuyển Khoản\".\n\nLIGHTING AND MOOD: Bright and clear, like a phone screen. The mood is informative and helpful.\n\nTEXT ELEMENTS (in Vietnamese):\n- Text on graphic: Title \"CÁCH NHẬN BIẾT LỪA ĐẢO ONLINE\" and other keywords.\n- Caption on post: \"LƯỚT TRÁI ĐỂ XEM CÁC DẤU HIỆU NHẬN BIẾT!\"\n\nCRITICAL REQUIREMENTS: The social media post must look authentic and be the focus. All text in Vietnamese."

OUTPUT_PREFIX = "p1_p1"  # Prefix for saved image files


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






