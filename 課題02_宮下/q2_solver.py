import json
import pdb
import rdflib
import csv
from dijkstra import count_teleport
from datetime import datetime
from gpt_inference import query_gpt
from act_movie_mapper import construct_full_path

class Q2Solver:
    def __init__(self, mp4_file_list_path, qtype, use_gpt, completedata=False):
        self.file_dict_ = {}
        complete_text = 'CompleteData' if completedata else 'PartiallyMissingData'
        self.use_gpt = use_gpt
        if use_gpt and not completedata:
            gpt_text = 'GPT'
        else:
            gpt_text = 'NoGPT'
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.out_file_name = f'./outputs/{qtype}_{complete_text}_{gpt_text}_{current_time}.csv'
        with open(mp4_file_list_path, 'r') as f:
            for line in f:
                file_name, file_path = line.strip().split(',')
                self.file_dict_[file_name] = file_path
        self.completedata = completedata
        if completedata:
            self.episode_prefix_ = "../Knowledge-Graph-Reasoning-Challenge/DataSet/CompleteData/Episodes/" # + scene1_Day1.json
            self.rdf_prefix_ = "../Knowledge-Graph-Reasoning-Challenge/DataSet/CompleteData/RDF/" # + Admire_art1_scene1.ttl
        else:
            self.episode_prefix_ = "../Knowledge-Graph-Reasoning-Challenge/DataSet/PartiallyMissingData/Episodes/222/"
            self.rdf_prefix_ = "../Knowledge-Graph-Reasoning-Challenge/DataSet/PartiallyMissingData/RDF/222/" 
        with open('./action_list.txt', 'r') as file:
            self.action_list_ = [line.strip() for line in file.readlines()]
        
    def solve(self, filename): # filename (../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/MultiChoice/Q1/q1_answer_scene1_Day1_bathroom.json)
        """
        This function solve the question 2
        input: filename
        output: is_correct (bool)
        """
        print("====================================================")
        # JSONファイルを読み込む
        with open(filename, 'r') as file:
            data = json.load(file)
        
        # question部分にアクセス
        question_type = data.get('questionType', '')
        if question_type == 'multipleChoice':
            question = data.get('question', '') # 第二引数はデフォルト値
            question_words = question.split() # "How many times did he {verb}?"
            target = question_words[-1].rstrip('?')
            print(f'Question: {question}, Target: {target}')
        elif question_type == 'Yes/No':
            question = data.get('question', '')
            target = question.split()[2] # 例: Did he wipe 2 times? => wipe
            target_count = int(question.split()[-2]) # 例: Did he wipe 2 times? => 2
            print(f'Question: {question}, Target: {target}, Target count: {target_count}')
        else:
            raise ValueError(f'Invalid question type: {question_type}')

        # scenarioにアクセス
        scenario = data.get('senario', '')
        with open(self.episode_prefix_ + scenario + ".json", 'r') as file:
            scenario_data = json.load(file)
        activities = scenario_data['data']['activities']
        scene = scenario_data['data']['scene']
        count = 0 # Target actionの実行回数

        # csvファイルに書き込むデータを定義
        activity_list_csv = [] # activity名 + scene番号
        count_list_csv = [] # 各activityでのaction count
        action_list_csv = [] # 各activityでのaction_list
        cumsum_time_list_csv = [] # 各activityでの累積時間
        replace_flags_csv = [] # 各activityでのGPTによる置換フラグ

        # 各activityについて、Actionの回数の計測
        for activity in activities:
            count_activity = count # 現在のactivityでのTarget actionの実行回数(差分を計算)
            print(activity)
            activity_list_csv.append(activity + "_scene" + str(scene))
            if self.completedata:
                with open(self.rdf_prefix_ + activity + "_scene" + str(scene) + ".ttl", 'r') as file:
                    g = rdflib.Graph()
                    g.parse(file, format='turtle')
                with open (self.rdf_prefix_ + "add_places.ttl", 'r') as file:
                    g.parse(file, format='turtle')
            else:
                with open(self.rdf_prefix_ + activity + "_scene" + str(scene) + "-222.ttl", 'r') as file:
                    g = rdflib.Graph()
                    g.parse(file, format='turtle')
            
            query = """
            PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
            PREFIX vh2kg: <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
            SELECT *
            WHERE {
                ?event a ?eventType .
                ?event vh2kg:eventNumber ?n .
                ?event vh2kg:action ?action .
                ?event vh2kg:time ?time .
                ?time time:numericDuration ?sec
            } order by ?n limit 100
            """
            result = g.query(query)
            action_list = []
            time_list = []
            for row in result:
                # print(f"{row.event} {row.action} {row.n} {row.sec}sec")
                action_list.append(str(row.action).split('/')[-1].lower())
                time_list.append(float(row.sec))
            cumsum_time_list = [sum(time_list[:i+1]) for i in range(len(time_list))]
            cumsum_time_list_csv.append(cumsum_time_list)
            
            print(action_list)
            replace_flags = []
            for i, action in enumerate(action_list):
                if "xxx" in action: # actionxxx0など
                    if self.use_gpt:
                        if i == 0:
                            time = (0, cumsum_time_list[i])
                        else:
                            time = (cumsum_time_list[i-1], cumsum_time_list[i])
                        prefix = self.file_dict_[activity]
                        movie_full_path = construct_full_path(prefix, scene, activity, viewpoint=0)
                        pred_action = query_gpt(movie_full_path, self.action_list_, time, i, mode="action")
                        action_list[i] = pred_action
                        replace_flags.append(True)
                        action = pred_action
                else:
                    replace_flags.append(False)
                if action == target:
                    count += 1
            replace_flags_csv.append(replace_flags)
            action_list_csv.append(action_list) # TODO GPTを使用する場合、置換後のaction listを保存し、欠損フラグを別で用意
            print(count)
            count_list_csv.append(count - count_activity)
        
        print(f'Target action "{target}" executed {count} times.')
            
        # answersの各要素にアクセス
        answers = data.get('answers', [])
        if question_type == 'multipleChoice':
            for answer in answers:
                answer_id = answer.get('id')
                answer_text = answer.get('answer')
                correct = answer.get('correct')
                if correct:
                    gt = answer_text
                print(f'Answer ID: {answer_id}, Answer: {answer_text}, Correct: {correct}')

            with open(self.out_file_name, 'a', newline='') as csvfile:
                fieldnames = ['filename', 'target_action', 'prediction', 'ground_truth', 'correct', 'activity', 'count', 'action_list', 'event_time_list', 'replace_flags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()
                
                for activity, count_csv, action_list, cumsum_time_list, replace_flags in zip(activity_list_csv, count_list_csv, action_list_csv, cumsum_time_list_csv, replace_flags_csv):
                    writer.writerow({
                        'filename': filename,
                        'target_action': target,
                        'prediction': count,
                        'ground_truth': gt,
                        'correct': count == gt,
                        'activity': activity,
                        'count': count_csv,
                        'action_list': action_list,
                        'event_time_list': cumsum_time_list,
                        'replace_flags': replace_flags
                    })

            return count == gt 
        
        elif question_type == 'Yes/No':
            for answer in answers:
                answer_id = answer.get('id')
                answer_text = answer.get('answer')
                correct = answer.get('correct')
                if correct:
                    gt = True if answer_text.lower() == 'yes' else False
                print(f'Answer ID: {answer_id}, Answer: {answer_text}, Correct: {correct}')
            pred = count == target_count # True: Yes, False: No
            print(f'Pred count: {count}, Target Count: {target_count}, Prediction: {pred}, Ground Truth: {gt}')

            with open(self.out_file_name, 'a', newline='') as csvfile:
                fieldnames = ['filename', 'target_action', 'target_count', 'predict_count', 'prediction', 'ground_truth', 'correct', 'activity', 'count', 'action_list', 'event_time_list', 'replace_flags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()
                
                for activity, count_csv, action_list, cumsum_time_list, replace_flags in zip(activity_list_csv, count_list_csv, action_list_csv, cumsum_time_list_csv, replace_flags_csv):
                    writer.writerow({
                        'filename': filename,
                        'target_action': target,
                        'target_count': target_count,
                        'predict_count': count,
                        'prediction': pred,
                        'ground_truth': gt,
                        'correct': pred == gt,
                        'activity': activity,
                        'count': count_csv,
                        'action_list': action_list,
                        'event_time_list': cumsum_time_list,
                        'replace_flags': replace_flags
                    })

            return pred == gt # Yes/Noが一致しているなら正解
        
        else:
            raise ValueError(f'Invalid question type: {question_type}')