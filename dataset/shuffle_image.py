import os
from PIL import Image
import numpy as np
import random

def find_images(directory):
    image_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_paths.append(os.path.join(root, file))
    return image_paths

def split_and_shuffle_image(image_path, output_dir, patch_num):
    try:
        # Load the image
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Define the size for the patches
        patch_width = img_width // patch_num
        patch_height = img_height // patch_num

        patches = [img.crop((i * patch_width, j * patch_height, (i+1) * patch_width, (j+1) * patch_height)) 
                   for i in range(patch_num) for j in range(patch_num)]

        # Shuffle the patches
        random.shuffle(patches)

        # Create a new blank image to hold the shuffled patches
        new_img = Image.new('RGB', (img_width, img_height))

        # Paste the shuffled patches into the new image
        for i in range(patch_num):
            for j in range(patch_num):
                new_img.paste(patches.pop(), (i * patch_width, j * patch_height))

        # Prepare the output path
        rel_path = os.path.relpath(image_path, start=os.path.dirname(data_dir))
        output_path = os.path.join(output_dir, rel_path)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the shuffled image
        new_img.save(output_path)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

patch_num_list = [2,4,8]
data_dir = 'original/data'

for patch_num in patch_num_list:
  # Change this to your actual data directory
    output_dir = f"Patchwise_QA/{patch_num}x{patch_num}"

    # Find all images in the data directory
    image_paths = find_images(data_dir)

    # Process each image
    for image_path in image_paths:
        split_and_shuffle_image(image_path, output_dir,patch_num)

print("Processing complete.")

