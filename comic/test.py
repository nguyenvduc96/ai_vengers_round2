import requests
import json
import base64
import os

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai/v1"
AI_API_KEY = os.getenv("GEMINI_API_KEY") # Thay bằng API key của bạn
IMAGE_SAVE_PATH = "generated_chat_image.png"

# --- Bước 1: Gọi API để tạo hình ảnh ---
url = f"{AI_API_BASE}/chat/completions"
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {AI_API_KEY}"
}
data = {
  "model": "gemini-2.5-flash-image-preview",
  "messages": [
      {
          "role": "user",
          "content": "A futuristic cityscape at sunset, with flying cars and neon lights. High resolution, photorealistic, 8k"
      }
  ]
}

try:
  response = requests.post(url, headers=headers, data=json.dumps(data))
  response.raise_for_status()

  result = response.json()
  # Trích xuất dữ liệu ảnh base64 từ response
  base64_string = result['choices'][0]['message']['images'][0]['image_url']['url']
  print("Image data received successfully.")

  # --- Bước 2: Giải mã và lưu hình ảnh ---
  # Loại bỏ tiền tố 'data:image/png;base64,' nếu có
  if ',' in base64_string:
      header, encoded = base64_string.split(',', 1)
  else:
      encoded = base64_string

  image_data = base64.b64decode(encoded)

  with open(IMAGE_SAVE_PATH, 'wb') as f:
      f.write(image_data)
  
  print(f"Image saved to {IMAGE_SAVE_PATH}")

except requests.exceptions.RequestException as e:
  print(f"An error occurred: {e}")
  print(f"Response body: {response.text if 'response' in locals() else 'No response'}")
except (KeyError, IndexError) as e:
  print(f"Failed to parse image data from response: {e}")
  print(f"Response body: {response.text if 'response' in locals() else 'No response'}")