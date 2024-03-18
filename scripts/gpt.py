import json
from openai import OpenAI
import os
import base64
import requests
import time

client = OpenAI()
from pathlib import Path
api_key = "your_api_key"

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}
# Set your OpenAI API key here

# Path to your annotation file
json_file_path = ''

# Output file
output_file_path = ''

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
# Read the JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Open the output file
with open(output_file_path, 'w') as output_file:
    for entry in data:
        image_path = entry['image_path']
        question = entry['question']
        question_id = entry['question_id']
        base64_image = encode_image(image_path)

        # Check if image exists
        if not Path(image_path).is_file():
            print(f"Image not found: {image_path}")
            continue

        # Prepare the prompt
        prompt = f"{question}"
        # Count the number of attempts
        attempts = 0

        while 1:
            try:
                payload = {
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
                    "max_tokens": 300
                }
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                print(response.json())
                model_output = response.json()['choices'][0]['message']['content']
                
                break  # Break the loop if request was successful
            except Exception as e:
                print(image_path)
                print(f"Error during API call: {str(e)}")
                attempts += 1
                time.sleep(30)  # Wait for 1 second before retrying. You can adjust the waiting time.


        # Write the result to the output file
        output_entry = {
            "question_id": question_id,
            "model_output": model_output,
            "prompt": question
        }
        output_file.write(json.dumps(output_entry) + '\n')

print("Processing completed.")
