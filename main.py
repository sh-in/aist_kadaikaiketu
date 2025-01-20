import argparse
import os
from pathlib import Path
import json
import re
from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib

import query
import q3, q4
import pandas as pd

# activityと動画の対応リスト取得
def read_file_list(file_list):
    # read file list and contain as an associative array
    file_dict = {}
    with open(file_list, 'r') as f:
        for line in f:
            file_name, file_path = line.strip().split(', ')
            scene = file_path.split("/")[4]
            file_dict[file_name+"_"+scene] = file_path
    return file_dict

def get_question_info(question_json: dict):
    for answer_json in  question_json["answers"]:
        if answer_json["correct"] == True:
            answer = answer_json["answer"]
    senario = question_json["senario"]
    question = question_json["question"]
    return senario, question, answer

# QAファイル関連の前処理
def pre_process_question(question_file: Path, regex: re.Pattern):
    # QAファイルの読み込み
    with open(question_file, "r") as f:
        question_json = json.load(f)
    # QA内のsenario, question, answerの取得
    senario, question, answer = get_question_info(question_json)
    # senario, questionから必要な情報の取得
    scene,day = senario.split("_")
    place = re.search(regex, question).group(1)
    # 正解の回数の取得 (Q1, 2用)
    # answer_number = re.search(rf"{place} (.+?) times", question).group(1)
    # try:
    #     answer_number = re.search(rf"number=(.+?)\).number", answer_number).group(1)
    # except:
    #     answer_number = answer_number
    # senarioからepisodeを読み込み、activitiesを取得
    with open(PROJECT_PATH / Path(f"DataSet/PartiallyMissingData/Episodes/222/{senario}.json"), 'r') as f:
        episode_json=json.load(f)
        activities = episode_json["data"]["activities"]
    
    return senario, question, answer, activities, place, scene, day
    return senario, question, answer, activities, place, scene, day, ansqwer_number

def main(args, PROJECT_PATH):
    qa_type = args.qa_type
    qa_num = args.qa_num
    # QAファイルのパス指定
    if qa_num != "Caption":
        question_path = PROJECT_PATH / Path(f"DataSet/QA/{qa_type}/Q{qa_num}")
    else:
        question_path = PROJECT_PATH / Path(f"DataSet/QA/{qa_type}/{qa_num}")
    
    # activityと動画の対応リスト取得
    file_dict = read_file_list(PROJECT_PATH / Path("methods/mp4_files_list.txt"))
    # actionのリスト取得
    action_list = pd.read_csv(PROJECT_PATH / Path("methods/action_list.csv"), header=None)
    action_list = action_list[0].tolist()

    accuracy = 0
    total = 0
    predictions = []
    answers = []
    questions = []
    video_paths = []
    for question_file in question_path.iterdir():
        questions.append(question_file)
        total += 1
        print("-"*20)
        print(question_file)
        # 正規表現のコンパイル
        # QAの種類によって変更する必要あり
        if qa_num == "3":
            if qa_type == "MultiChoice":
                regex = re.compile(r"What did he do after he first entered the ([a-z]+)")
            elif qa_type == "YesNo":
                regex = re.compile(r"Did he ([a-zA-Z]+)")
        elif qa_num == "4":
            regex = re.compile(r"What did he do just before he first entered the ([a-z]+)")
        # 前処理
        senario, question, answer, activities, target_place, scene, day = pre_process_question(question_file, regex)
        # senario, question, answer, activities, place, scene, day, answer_number = pre_process_question(question_file)
        if qa_num == "3":
            if qa_type == "MultiChoice":
                # Q3: kitchenに入った直後に何をしたか
                action_label, video_path, accuracy = q3.q3(PROJECT_PATH, activities, answer, target_place, scene, accuracy, file_dict, action_list)
                print("accuracy:", accuracy/total)
                predictions.append(action_label)
                answers.append(answer)
                video_paths.append(video_path)
                # 20回の試行で、GPTによる補完なしで60%の精度を達成
                # 20回の試行で、GPTによる補完あり(place)で55%の精度を達成
                # 20回の試行で、GPTによる補完あり(place, action)で50%の精度を達成
                # 20回の試行で、GPTによる補完有(place, action)でfirst, last placeを取得、55%の精度を達成
            elif qa_type == "YesNo":
                action = target_place
                target_place = "kitchen"
                action_label, video_path, _ = q3.q3(PROJECT_PATH, activities, action, target_place, scene, accuracy, file_dict, action_list)
                if action == action_label.upper() and answer == "Yes":
                    accuracy += 1
                elif action != action_label.upper() and answer == "No":
                    accuracy += 1

                print("accuracy:", accuracy/total)
                predictions.append(action_label)
                answers.append(answer)
                video_paths.append(video_path)
                # %の精度を達成
        elif qa_num == "4":
            # Q4: kitchenに入る直前に何をしたか
            action_label, video_path, accuracy = q4.q4(PROJECT_PATH, activities, answer, target_place, scene, accuracy, file_dict, action_list, qa_num)
            print("accuracy:", accuracy/total)
            predictions.append(action_label)
            answers.append(answer)
            video_paths.append(video_path)
            # 10回の試行で、GPTによる補完なしで30%の精度を達成
            # 20回の試行で、GPTによる補完なしで65%の精度を達成
            # 20回の試行で、GPTによる補完あり(place, action)で65%の精度を達成
            # 20回の試行で、GPTによる補完有(place, action)last placeを取得、65%の精度を達成
        elif qa_num == "5":
            # Q5: ある時間帯で何をしたか
            pass
        if total == 20:
            break
    print("Final Accuracy:", accuracy/total)
    ouptut_df = pd.DataFrame({"questions": questions, "video path": video_paths, "answers": answers, "predictions": predictions})
    ouptut_df.to_csv(PROJECT_PATH / Path(f"methods/outputs/{qa_type}_Q{qa_num}_output.csv"), index=False)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--qa_type", type=str, default="MultiChoice")
    arg_parser.add_argument("--qa_num", type=str, default="1")
    args = arg_parser.parse_args()
    PROJECT_PATH = "/home/suzuki.shin/workspace/aist_kadai/"
    main(args, PROJECT_PATH)