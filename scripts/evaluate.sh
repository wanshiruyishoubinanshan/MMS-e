#!/bin/bash

WORKSPACE_PATH="/data1/leijiayi/LLaMA2-Accessory/accessory/eval_mm/MMS-e" # Please put your absolute workspace path here. It will be used as root folder for all the following folders.
GROUND_TRUTH_FOLDER="lab3/stable12/annotations" # The input folder of the ground truth answers.
MODEL_PREDICT_FOLDER="lab3/stable12/results/adapter_results" # The input folder of your model predict answers.
RESULT_OUTPUT_FOLDER="lab3/stable12/evaluate_results/adapter_evaluate_results" # The output folder of the gpt evaluate results. Python script will generate results here.
OPENAI_API_KEY="your_api_key" # Please put your openai key here

# Function to get the prefix of a file path (everything except the last component)
function get_path_prefix() {
    local file_path="$1"
    
    # Remove the last component from the path
    echo "${file_path%/*}"
}

function evaluate() {
    local prediction_file="$1"
    local script="$2"
    local ground_truth_file="$3"
    local output_file="$4"
    
    export OPENAI_API_KEY="$OPENAI_API_KEY"
    python "$WORKSPACE_PATH/$script" \
        --prediction_jsonl_path "$MODEL_PREDICT_FOLDER/$prediction_file" \
        --ground_truth_jsonl_path "$GROUND_TRUTH_FOLDER/$ground_truth_file" \
        --output_jsonl_path "$RESULT_OUTPUT_FOLDER/$output_file" \
        --gpt_model "gpt-3.5-turbo"
    
    python "$WORKSPACE_PATH/avg_score.py" "$RESULT_OUTPUT_FOLDER/$output_file"
}
function get_ground_truth_file() {
    local prediction_file="$1"
    
    case "$prediction_file" in
        *action_recognition*) echo "action_recognition.jsonl" ;;
        *artwork_recognition*) echo "artwork_recognition.jsonl" ;;
        *celebrity_recognition*) echo "celebrity_recognition.jsonl" ;;
        *commonsense_reasoning*) echo "commonsense_reasoning.jsonl" ;;
        *future_prediction*) echo "future_prediction.jsonl" ;;
        *image_scene*) echo "image_scene.jsonl" ;;
        *image_topic*) echo "image_topic.jsonl" ;;
        *instances_attributes*) echo "instances_attributes.jsonl" ;;
        *instances_counting*) echo "instances_counting.jsonl" ;;
        *object_localization*) echo "object_localization.jsonl" ;;
        *text_recognition*) echo "text_recognition.jsonl" ;;
        *visual_reasoning*) echo "visual_reasoning.jsonl" ;;
        *) echo "unknown" ;;
    esac
}


# Function to determine the appropriate evaluation script based on file name
function get_evaluation_script() {
    local file_name="$1"
    
    if [[ "$file_name" == *"action_recognition"* || "$file_name" == *"future_prediction"* || "$file_name" == *"image_scene"* || "$file_name" == *"image_topic"* || "$file_name" == *"instances_attributes"* || "$file_name" == *"instances_counting"* || "$file_name" == *"object_localization"* || "$file_name" == *"text_recognition"* || "$file_name" == *"visual_reasoning"* ]]; then
        echo "gpt_evaluation_script_multichoice.py"
    elif [[ "$file_name" == *"artwork_recognition"* || "$file_name" == *"celebrity_recognition"* || "$file_name" == *"commonsense_reasoning"* ]]; then
        echo "gpt_evaluation_script_judge.py"
    fi
    #echo "gpt_evaluation_rebuild_img.py"
    

}

# Main loop for file processing
echo "========================================"
echo "Starting evaluation of prediction files..."
echo "========================================"

find "$MODEL_PREDICT_FOLDER" -name "*.jsonl" | while read file; do
    # 获取完整的文件名和文件所在的目录
    base_name=$(basename "$file")
    dir_name=$(dirname "$file")
   
    relative_path=${file#"$MODEL_PREDICT_FOLDER/"}
    
    ground_truth_file=$(get_ground_truth_file "$relative_path")
    if [ "$ground_truth_file" != "unknown" ]; then
        script_name=$(get_evaluation_script "$relative_path")
        path_prefix=$(get_path_prefix "$relative_path")
        output_file="${base_name%.jsonl}_evaluate.json"

        evaluate "$relative_path" "$script_name" "$ground_truth_file" "$output_file"
    else
        echo "No matching ground truth file for $relative_path"
    fi
done



echo "========================================"
echo "Evaluation process complete."
echo "========================================"
