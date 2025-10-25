# Configuration
from openai import OpenAI

client = OpenAI(
  api_key="sk-hj_b8UR4iNeuFX62E5gj1g",
  base_url="https://api.thucchien.ai"
)

with open("prompt_v2.txt", "r", encoding="utf-8") as f:
    prompt_content = f.read()

# Execute
response = client.chat.completions.create(
  model="gemini-2.5-pro",
  messages=[
      {
          "role": "system",
          "content": "You are an expert comic book writer and character designer. I need you to create a complete comic book plan with cover and full story script. You must generate the prompt in all pages"
      },
      {
          "role": "user",
          "content": prompt_content
      }
  ]
)

with open("output_script_v2.txt", "w", encoding="utf-8") as f:
    f.write(response.choices[0].message.content)

print("Output written to output_script.txt")