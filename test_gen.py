# Configuration
from openai import OpenAI

client = OpenAI(
  api_key="sk-hj_b8UR4iNeuFX62E5gj1g",
  base_url="https://api.thucchien.ai"
)

with open("prompt.txt", "r", encoding="utf-8") as f:
    prompt_content = f.read()



# Execute
response = client.chat.completions.create(
  model="gemini-2.5-pro",
  messages=[
      {
          "role": "system",
          "content": "You are an expert comic book writer and character designer."
      },
      {
          "role": "user",
          "content": prompt_content
      },
  ],
      temperature=0.7
)

with open("output_script_p1.txt", "w", encoding="utf-8") as f:
    f.write(response.choices[0].message.content)

print("Output written to output_script.txt")