import re
import json
import openai  # Assuming openai is installed and properly set up
import time
from tqdm import tqdm

import argparse
from openai import OpenAI
client = OpenAI()
def load_jsonl(file_path):
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

def get_gpt_scores(prediction_jsonl_path, ground_truth_jsonl_path, output_jsonl_path, gpt_model):
    # Load the ground truths
    ground_truths = load_jsonl(ground_truth_jsonl_path)
    
    # Create a dictionary for easy access to ground truths
    gt_dict = {item['question_id']: item for item in ground_truths}
    #print(gt_dict)
    # Process each prediction
    predictions = load_jsonl(prediction_jsonl_path)
        
    with open(output_jsonl_path, 'w') as out_file:
        for item in tqdm(predictions,desc='Evaluating, If stuck, please Ctrl + C .', dynamic_ncols=True):
            question_id = item['question_id']
            prediction_text = item.get('model_output',"")
            #print(gt_dict)
            gt_item = gt_dict.get(question_id, {})
            #print(gt_item)
            gt_answer = gt_item.get('answer',"")
            #print("gt:",gt_answer)
            prediction_text=str(prediction_text)
            gt_answer=str(gt_answer)
            
            
            gt_question = gt_item.get('prompt')
            #print("prediction:",prediction_text,"gt:",gt_answer)
            print(f"question_id: {question_id}, prediction_text: {prediction_text}, gt_answer: {gt_answer}")
            # if not prediction_text or not gt_answer:
            #     print(f"Skipping question_id {question_id} due to empty prediction_text or gt_answer.")
            #     continue
            
            retries = 0
            max_retries = 3
            while True:
            # Create a question for the GPT model and other processing here...
                question = f"""Compare the ground truth and prediction from AI models, to give a correctness score for the prediction.  The correctness score is 0.0 (totally wrong), 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, or 1.0 (totally right). 
                Compare the options of the ground truth and the prediction to determine if they match. If they match, assign a score of 1.0; if they do not match, assign a score of 0.0.
                If prediction is empty, assign a score of 0.0.
                Example:
                Question | Ground truth | Prediction | Correctness
                --- | --- | --- | ---
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"An empty school cafeteria with rows of folded tables and circular red stools.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,1,2,0\nB) 2,1,0,3\nC) 0,1,3,2\nD) 1,2,0,3 | A | B | 0.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"An empty school cafeteria with rows of folded tables and circular red stools.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,1,2,0\nB) 2,1,0,3\nC) 0,1,3,2\nD) 1,2,0,3 | A | A | 1.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"A close-up of a woman with curly hair, appearing concerned or focused, framed by a red border.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,0,1,2\nB) 0,1,3,2\nC) 2,0,3,1\nD) 1,0,2,3 | B | C | 0.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"A close-up of a woman with curly hair, appearing concerned or focused, framed by a red border.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,0,1,2\nB) 0,1,3,2\nC) 2,0,3,1\nD) 1,0,2,3 | B | B | 1.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"A close-up of a woman with curly hair, appearing concerned or focused, framed by a red border.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,0,1,2\nB) 0,1,3,2\nC) 2,0,3,1\nD) 1,0,2,3 | B | B) 0,1,3,2 | 1.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"A close-up of a woman with curly hair, appearing concerned or focused, framed by a red border.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,0,1,2\nB) 0,1,3,2\nC) 2,0,3,1\nD) 1,0,2,3 | B | 0,1,3,2 | 1.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"A close-up of a woman with curly hair, appearing concerned or focused, framed by a red border.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,0,1,2\nB) 0,1,3,2\nC) 2,0,3,1\nD) 1,0,2,3 | B | 2,0,3,1 | 1.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"A truck is tipping over on a road while other vehicles are nearby.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,0,2,1\nB) 1,2,0,3\nC) 2,3,1,0\nD) 0,1,2,3 | B | D | 0.0
                This is an image divided into 4 patches and randomly shuffled, with each patch labeled in red. \"A truck is tipping over on a road while other vehicles are nearby.\" is a brief description of the image. Based on the content described in this sentence, restore the correct order of the patches as top-left, top-right, bottom-left, and bottom-right. Choose from the following four options:\nA) 3,0,2,1\nB) 1,2,0,3\nC) 2,3,1,0\nD) 0,1,2,3 | B | B | 1.0
                

                Here is the QA you need to compare and score 
                Question: {gt_question} 
                Ground Truth: {gt_answer}
                Prediction: {prediction_text} 
                Score :
                
                Provide only the numerical correctness score as the output. 
                """

                try: 
                    response = client.chat.completions.create(
                    model=gpt_model,
                    max_tokens=64,
                    messages=[{"role": "user", "content": question}],
                    timeout = 10,
                )
                    # print("response: ",response)
                except:
                    print("sleep 30s")
                    time.sleep(30)

            # Example of how you might write results to the output file
                
                else:
                    # Example of how you might write results to the output file
                    model_response = response.choices[0].message.content
                    print(f"model_response: {model_response}")
                    try:
                        score_matches = re.findall(r"(\d+(\.\d+)?)", model_response)
                        if score_matches:
                            if len(score_matches) > 1:
                                raise ValueError(f"Multiple numbers detected: {model_response}")
                            
                            score = float(score_matches[0][0])
                            # print(f"model_response: {model_response}")
                            print(f"score: {score}")
                            if 0 <= score <= 1:
                                result = {
                                    'question_id': question_id,
                                    'image': gt_item.get('image', ''),
                                    'gt_answers':gt_answer,
                                    'model_answer':prediction_text,
                                    'score': score
                                }
                                out_file.write(json.dumps(result) + '\n')
                                break
                        else: 
                            raise ValueError(f"Invalid response format: {model_response}")
                    except ValueError:
                        pass
            
            
                retries += 1
                if retries == max_retries:
                    print(f"Failed to get a valid score after {max_retries} attempts for question_id {question_id}.")

def main():
    parser = argparse.ArgumentParser(description='Evaluate predictions using GPT.')
    parser.add_argument('--prediction_jsonl_path', type=str, required=True,help='Path to the prediction JSONL file.')
    parser.add_argument('--ground_truth_jsonl_path', type=str, required=True,help='Path to the ground truth JSONL file.')
    parser.add_argument('--output_jsonl_path', type=str, required=True,help='Path to save the output JSONL file.')
    parser.add_argument('--gpt_model', type=str, required=True, help='GPT model to use for evaluation.')
    
    args = parser.parse_args()
    get_gpt_scores(args.prediction_jsonl_path, args.ground_truth_jsonl_path, args.output_jsonl_path, args.gpt_model)

if __name__ == '__main__':
    main()
