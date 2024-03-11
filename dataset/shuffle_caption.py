import os
import base64
import json
import requests
import time
import random

api_key = "your_api_key"  # Replace with your actual API key

# Define the function to encode the image to base64 format
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Specify the directory to look for images
directory = 'original/data1'

# Define the supported image formats
image_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

# Your API key and other headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

prompt = "Briefly describe this picture in one sentence, less than 20 words."

# Walk through the directory
for subdir, dirs, files in os.walk(directory):
    # Initialize variable for storing the responses for the current subdir
    subdir_responses = []
    question_id = 1
    for file in files:
        # Check if the file is an image
        if file.lower().endswith(image_formats):
            image_path = os.path.join(subdir, file)
            try:
                # Encode the image
                base64_image = encode_image(image_path)

                # Define the payload for API request
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

                # Initialize variable to track attempt count
                attempts = 0

                # Try to send request and process response
                while attempts<5:
                    try:
                        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                        response_json = response.json()
                        print(response_json)  # Print response for debugging
                        model_output = response_json['choices'][0]['message']['content']
                      
                        words = model_output.split()
                        random.shuffle(words)  
                        shuffled_caption = ' '.join(words)  
                        # Store the response with the image path
                        subdir_responses.append({
                            "question_id": question_id,
                            "image": image_path,
                            "text": f"*{shuffled_caption}*This is a brief description of the image, scrambled; restore the correct order of expression based on the content in the image.",
                            "category": f"rebuild_caption",
                            "answer": model_output
                        })
                        question_id +=1
                        break  # If request is successful, break the loop
                    except Exception as e:
                        print(f"Error during API call: {str(e)}")
                        attempts += 1
                        time.sleep(30)  # If there's an error, wait for a while before retrying

            except Exception as e:
                print(f"Error encoding file {image_path}: {str(e)}")


    # Save the responses to a JSON file in the corresponding subdir
    if subdir_responses:  # Only save if there are responses
        last_dir = os.path.basename(subdir)
        subdir_json_path = os.path.join('Reconstruction/rebuild_caption/annotations', last_dir) + '.jsonl'
    
        with open(subdir_json_path, 'w') as outfile:
            json.dump(subdir_responses, outfile)
        
        print(f"Responses for {subdir} are saved in {subdir_json_path}")
