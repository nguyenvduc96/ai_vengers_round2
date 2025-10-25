import json
from typing import Literal
from openai import OpenAI
from pydantic import BaseModel, Field
import base64
import os
import requests


IMAGE_PROMPT_REQUIREMENTS = """
  ##### IMAGE REQUIREMENTS:
  Here are some tips for generating image prompt:
  - Core Components: Always define the Subject, the surrounding Context/Background, and the overall Style (e.g., photograph, painting, 3D render).
  - Descriptive Modifiers: Enhance the prompt with specific details about lighting, camera angle, color palette, or artistic medium.
  - Technical Specifications: If necessary, include technical parameters like image quality.
   **NOTICES**
  If you need to generate image for Vietnamese map or Vietnamese flag, you need to use the following descriptions:
  - The Vietnamese Map: "A minimalist map of Vietnam with its distinctive S-shape, entirely colored in red with a yellow star in the northern region, mirroring the Vietnamese flag. To the east of the main map, there are two smaller island clusters, also colored red."

  - The Vietnamese Flag: "a powerful shot of the Vietnamese flag, its vibrant red background billowing gracefully, with the golden star at its center shining brightly."
"""




class Panel(BaseModel):
    panel_number: int = Field(description="The number of the panel. It should be the order of the panel in the page")
    image_prompt: str = Field(description="The prompt to generate the image of the panel. It should be a detailed description of the image to generate. What is the background, what is the characters, what is the action, what is the emotion, what is the dialogue, what is the narration, etc. Have to be consistent in style. And all description have to be in English.")
    image_ratio: Literal["1:1","3:4", "4:3", "16:9", "9:16"] = Field(description="The ratio of the image. It should be the ratio of the image to generate.")
    dialogue: str = Field(description="The dialogue of the panel. It should be the dialogue of the characters in the panel. If there is no dialogue, leave it blank.")




class Page(BaseModel):
    page_number: int = Field(description="The number of the page")
    panels: list[Panel] = Field(description="The list of panels in the page")
class Character(BaseModel):
    name: str = Field(description="The name of the character")
    description: str = Field(description="The description of the character. It should be a detailed description of the character. What is the character's appearance, age, gender, personality, etc. Have to be consistent in style. And all description have to be in English.")  
   
class Story(BaseModel):
    thinking: str = Field(description="The reason that why you create this story")
    title: str = Field(description="The title of the story")
    content: str = Field(description="The content of the story")
    style: str = Field(description= "Style of the pictures in the comic. For example: Vietnamese modern comic, manga, popart,...")
    characters: list[Character] = Field(description="The list of characters in the story")
    pages: list[Page] = Field(description="The list of pages in the story")
  
def generate_content_with_structured_output(
    model: str,
    messages: list[dict[str, str]],
    response_schema: BaseModel,
    temperature: float = 0.8):
    client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://api.thucchien.ai")
    response = client.chat.completions.parse(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format=response_schema
    )
    return response.choices[0].message.parsed

def create_story(requirements: str):
    prompt = f"""
    You are an expert Vietnamese storyboard artist. Your mission is to create a storyboard for a comic book based on the user's requirements provided below.
    ## YOUR TASK:
    You will deliver your response in these steps:
    ### 1. Define the story title and the content of the story
    - Define the story title. The title should be a catchy and memorable title that is related to the content of the story.
    - Define the content of the story. The content should be a detailed description of the story. What is the story about, what is the main characters, what is the main events, what is the main conflicts, etc.
    ### 2. Define the characters of the story
    - Define the characters of the story. The characters should be a detailed description of the characters. What is the character's appearance, age, gender, personality, etc. It'll be used to create the character reference image.
    ### 3. Separate the story into pages
    - You need to create the content for each page of the comic book. How many panels per page?
    - The first page have only 1 panel and have to be the cover of the comic. 
    - You have to describe the image in the panel in detail. Make sure there is no text in the image except inside dialogue/text/narration.
    - You have to think about the layout of the page and decide the ratio of the image in the panel.
    {IMAGE_PROMPT_REQUIREMENTS}
    ## IMPORTANT:
    - Make sure the style of the story is consistent.
    """
    story = generate_content_with_structured_output(
        model="gemini-2.5-pro",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Here is the requirements for the story: {requirements}"}
        ],
        response_schema=Story
    )
    with open("story.json", "w", encoding="utf-8") as f:
        json.dump(story.model_dump(), f, indent=4, ensure_ascii=False)
    return story




def generate_image(
    page:Page,style:str):
    try:
        client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://api.thucchien.ai")
        messages=[]
        for panel in page.panels:
            output_file = f"./output/image_{page.page_number}_{panel.panel_number}.png"
            if len(messages) > 6:
                input_message = messages[-4]
            else:
                input_message = messages
                
            # response = client.chat.completions.create(
            #             model="gemini-2.5-flash-image-preview",
            #             messages= input_message,
            #             modalities=["image"]
            # )
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {os.getenv("GEMINI_API_KEY")}',
            }
            json_data = {
                'model': 'gemini-2.5-flash-image-preview',
                'messages': messages,
                'modalities': [
                    'image',
                ],
            }
            response = requests.post('https://api.thucchien.ai/v1/chat/completions', headers=headers, json=json.dumps(json_data))
            response.raise_for_status()
            
            result = response.json()
            base64_string = result['choices'][0]['message']['images'][0]['image_url']['url']
            messages.append(
                {
                    "role": "assistant",
                    "content": base64_string
                }
            )
            if ',' in base64_string:
                _, encoded = base64_string.split(',', 1)
            else:
                encoded = base64_string
            image_data = base64.b64decode(encoded)
            with open(output_file, "wb") as f:
                f.write(image_data)
            print("Image saved to generated_chat_image.png")

    except Exception as e:
        print(f"Error generating image: {e}")
        return None
    

if __name__ == "__main__":
  story = create_story(
      requirements="""
      Sáng tạo truyện tranh 9 trang (1 bìa màu, 9 trang nội dung) về chủ đề cảnh báo lừa đảo trực tuyến, hướng đến đối tượng học sinh THCS & THPT.

        Yêu cầu:
        - Cốt truyện: Xoay quanh hai nhân vật chính là học sinh, đối mặt và xử lý các tình huống lừa đảo online phổ biến (ví dụ: lừa nạp thẻ game, giả mạo người thân, đánh cắp thông tin cá nhân).
        - Nội dung: Phản ánh các hình thức lừa đảo thực tế, gần gũi với học sinh. Lồng ghép các kỹ năng nhận biết và phòng tránh một cách tự nhiên, dễ hiểu. Truyền tải thông điệp về việc sử dụng Internet an toàn và có trách nhiệm.
        - Nhân vật: Tạo hình nhân vật học sinh (một nam, một nữ) với phong cách năng động, thông minh và hiện đại.
        - Phong cách vẽ: Nét vẽ theo phong cách Vietnam comic trẻ trung, hiện đại. Bố cục các khung truyện sáng tạo, dễ theo dõi.
        - Trang bìa (đen trắng): Cần nổi bật, thể hiện được chủ đề chính, có tên truyện hấp dẫn và hình ảnh nhân vật chính tự tin trong môi trường số.
        - Các trang nội dung (trắng đen): Kể câu chuyện qua các tình huống cụ thể, cách giải quyết vấn đề và kết thúc bằng một trang tổng kết các bài học hoặc mẹo an toàn chính.
        - Ngôn ngữ: Sử dụng tiếng Việt với lời thoại tự nhiên, dí dỏm, phù hợp với lứa tuổi học sinh.
      """
  )
  print(story)
  for page in story.pages:
      generate_image(page=page, style=story.style)







