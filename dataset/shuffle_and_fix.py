import os
from PIL import Image
import numpy as np
import random

def find_images(directory):
    """
    Find all image files in the given directory and its subdirectories.
    
    Args:
    - directory (str): The path to the directory.
    
    Returns:
    - list of str: A list of paths to the image files.
    """
    image_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_paths.append(os.path.join(root, file))
    return image_paths

def split_shuffle_and_fix_patches(image_path, output_dir,fix_num):
    """
    Split the image into 4x4 patches, randomly fix the position of 4 patches,
    shuffle the remaining patches, and save the shuffled image with fixed patches.
    
    Args:
    - image_path (str): The path to the image file.
    - output_dir (str): The directory to save the processed images.
    """
    try:
        # Load the image
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Define the size for the patches
        patch_width = img_width // 4
        patch_height = img_height // 4

        # Split the image into 4x4 patches
        patches = [img.crop((i * patch_width, j * patch_height, (i+1) * patch_width, (j+1) * patch_height)) 
                   for i in range(4) for j in range(4)]

        # Randomly fix the position of 4 patches, shuffle the remaining
        fixed_indices = set(random.sample(range(16), fix_num))
        non_fixed_patches = [patch for idx, patch in enumerate(patches) if idx not in fixed_indices]
        random.shuffle(non_fixed_patches)

        # Create a new blank image to hold the processed patches
        new_img = Image.new('RGB', (img_width, img_height))

        # Paste the fixed and shuffled patches into the new image
        non_fixed_idx = 0
        for i in range(4):
            for j in range(4):
                idx = i * 4 + j
                if idx in fixed_indices:
                    new_img.paste(patches[idx], (i * patch_width, j * patch_height))
                else:
                    new_img.paste(non_fixed_patches[non_fixed_idx], (i * patch_width, j * patch_height))
                    non_fixed_idx += 1

        # Prepare the output path
        rel_path = os.path.relpath(image_path, start=os.path.dirname(data_dir))
        output_path = os.path.join(output_dir, rel_path)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save the processed image
        new_img.save(output_path)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

fix_num_list = [4,8,12]
data_dir = 'original/data'

for fix_num in fix_num_list:
# Define the input and output directories
  # Change this to your actual data directory
    output_dir = f"Fixed_Patch_QA/fix{fix_num}"

    # Find all images in the data directory
    image_paths = find_images(data_dir)

    # Process each image
    for image_path in image_paths:
        split_shuffle_and_fix_patches(image_path, output_dir, fix_num)

print("Processing complete.")
