#!/bin/bash

# Define the paths for the answers folder, jsonl files, and base image folder
ANSWERS_FOLDER="results/gpt_results"   
JSONL_FILE_PATH="original/annotations"
IMAGE_FOLDER_base="original/data"
gpt_path="scripts/gpt.py" 

# Iterate over all .jsonl files in the jsonl folder
for JSONL_FILE in "$JSONL_FILE_PATH"/*.jsonl; do
    # Extract the filename without path and extension
    FILENAME=$(basename -- "$JSONL_FILE")
    FILENAME="${FILENAME%.*}"

    # Determine the image-folder based on the filename
    IMAGE_FOLDER_SUFFIX=""
    case $FILENAME in
        action_recognition)
            IMAGE_FOLDER_SUFFIX="action_recognition";;
        artwork_recognition)
            IMAGE_FOLDER_SUFFIX="artwork_recognition";;
        celebrity_recognition)
            IMAGE_FOLDER_SUFFIX="celebrity_recognition";;
        commonsense_reasoning)
            IMAGE_FOLDER_SUFFIX="commonsense_reasoning";;
        future_prediction)
            IMAGE_FOLDER_SUFFIX="future_prediction";;
        image_scene)
            IMAGE_FOLDER_SUFFIX="image_scene";;
        image_topic)
            IMAGE_FOLDER_SUFFIX="image_topic";;
        instances_attributes)
            IMAGE_FOLDER_SUFFIX="instances_attributes";;
        instances_counting)
            IMAGE_FOLDER_SUFFIX="instances_counting";;
        object_localization)
            IMAGE_FOLDER_SUFFIX="object_localization";;
        text_recognition)
            IMAGE_FOLDER_SUFFIX="text_recognition";;
        visual_reasoning)
            IMAGE_FOLDER_SUFFIX="visual_reasoning";;
        Function)
            IMAGE_FOLDER_SUFFIX="Function";;
        geo3k)
            IMAGE_FOLDER_SUFFIX="geo3k";;
        geo3D)
            IMAGE_FOLDER_SUFFIX="geo3D";;
        *)
            # Print a message and skip if no matching image folder is found
            echo "No matching image folder for $FILENAME. Skipping."
            continue;;
    esac

    # For each resolution, define the image folder and execute the model_vqa.py script for non-recover benchmarks
    
    IMAGE_FOLDER="$IMAGE_FOLDER_base/$IMAGE_FOLDER_SUFFIX"
    ANSWER_FILE="$ANSWERS_FOLDER/answers_${FILENAME}.jsonl"

        # Execute the model_vqa.py script
    python $gpt_path \
        --question-file "$JSONL_FILE" \
        --image-folder "$IMAGE_FOLDER" \
        --answers-file "$ANSWER_FILE"
done
