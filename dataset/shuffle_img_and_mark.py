import os
import base64
import json
import requests
import time
import itertools
import random
from PIL import Image, ImageDraw, ImageFont

api_key = "your_api_key"  # Replace with your actual API key
def split_shuffle_mark_image(image_path):
    img = Image.open(image_path)
    img_width, img_height = img.size
    # Define the size for the patches
    patch_width = img_width // 2
    patch_height = img_height // 2

    patches = [(img.crop((i * patch_width, j * patch_height, (i+1) * patch_width, (j+1) * patch_height)), j * 2 + i) 
                for j in range(2) for i in range(2)]
    random.shuffle(patches)
    new_img = Image.new('RGB', (img_width, img_height))
    
    # Draw object to mark numbers on patches
    draw = ImageDraw.Draw(new_img)
    font = ImageFont.truetype("arial.ttf", size=min(patch_width, patch_height)//5)  # Adjust font size to patch size

    idx_orig_pos_dict = {}

    for idx, (patch, orig_pos) in enumerate(patches):
        x, y = (idx % 2 * patch_width, idx // 2 * patch_height)
        new_img.paste(patch, (x, y))
        draw.text((x + 10, y + 10), str(idx), fill=(255, 0, 0), font=font)
        idx_orig_pos_dict[idx] = orig_pos

    # Sort the dictionary by orig_pos and print idx sequence
    sorted_idx_orig_pos = sorted(idx_orig_pos_dict.items(), key=lambda x: x[1])
    sorted_idxs = [item[0] for item in sorted_idx_orig_pos]
    print(image_path)
    parts = image_path.split('/')
    last_two_parts = '/'.join(parts[-2:])
    new_path = f"Reconstruction/rebuild_img/data/{last_two_parts}"
    directory = os.path.dirname(new_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    new_img.save(new_path)
    return new_path, sorted_idxs

# Define the function to encode the image to base64 format
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Specify the directory to look for images
directory = 'original/data'

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
                shuffled_image_path, original_positions = split_shuffle_mark_image(image_path)
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

                        all_permutations = list(itertools.permutations([0, 1, 2, 3]))
                        all_permutations.remove(tuple(original_positions))

                        incorrect_answers = random.sample(all_permutations, 3)

                        correct_option_index = random.randint(0, 3)
                        options = ['A', 'B', 'C', 'D']
                        text = f"This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. *{model_output}*is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:"
                        # Construct the options text without brackets
                        for i, option in enumerate(options):
                            answer_str = ','.join(map(str, incorrect_answers.pop() if i != correct_option_index else original_positions))
                            text += f'\n{option}) {answer_str}'
                        
                        subdir_responses.append({
                            "question_id": question_id,
                            "image": shuffled_image_path,
                            "text": text,
                            "category": f"rebuild_img",
                            "answer": options[correct_option_index]
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
        subdir_json_path = os.path.join('Reconstruction/rebuild_img/annotations', last_dir) + '.jsonl'
        directory = os.path.dirname(subdir_json_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
        with open(subdir_json_path, 'w') as outfile:
            json.dump(subdir_responses, outfile)
        
        print(f"Responses for {subdir} are saved in {subdir_json_path}")
