import json
import pdb
import rdflib
from dijkstra import count_teleport
from datetime import datetime
import csv
from gpt_inference import query_gpt
from act_movie_mapper import construct_full_path

class Q1Solver:
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
        
    def solve(self, filename): # filename (../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/MultiChoice/Q1/q1_answer_scene1_Day1_bathroom.json)
        """
        This function solve the question 1
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
            question_words = question.split()
            target = question_words[-1].rstrip('?')
            print(f'Question: {question}, Target: {target}')
        elif question_type == 'Yes/No':
            question = data.get('question', '')
            target_str = question.split()[-2]
            
            if ')' in target_str: # 例: number=2).number
                target_count = int(target_str.split('=')[-1].split(')')[0])
            else: # 例: 2
                target_count = int(target_str)
            target = question.split()[4] # 例: Did he enter the bedroom 3 times? => bedroom
            print(f'Question: {question}, Target: {target}, Target count: {target_count}')
        else:
            raise ValueError(f'Invalid question type: {question_type}')

        # scenarioにアクセス
        scenario = data.get('senario', '')
        with open(self.episode_prefix_ + scenario + ".json", 'r') as file:
            scenario_data = json.load(file)
        activities = scenario_data['data']['activities']
        scene = scenario_data['data']['scene']
        count = 0 # 部屋の入室回数のカウント
        before_teleport = None # テレポート前の部屋にいたかどうか

        # csvファイルに書き込むデータを定義
        activity_list_csv = [] # activity名 + scene番号
        count_list_csv = [] # 各activityでのcount
        room_list_csv = [] # 各activityでのroom_list
        cumsum_time_list_csv = [] # 各eventの終了時間
        replace_flags_csv = [] # GPTの置換フラグ

        # 各activityについて、部屋の入室回数の計測
        for activity in activities:
            count_csv = count # 現在のactivityでの部屋の入室回数のカウント(差分を計算)
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
            PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
            PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
            SELECT *
            WHERE {
                ?e :eventNumber ?n .
                OPTIONAL { ?e :from ?from_room . }
                OPTIONAL { ?e :to ?to_room . }
                OPTIONAL { ?e :place ?place . }
                ?e :time ?time .
                ?time time:numericDuration ?sec
            } order by ?n limit 100"""

            result = g.query(query)
            room_list = []
            time_list = []
            for row in result:
                # print(f"{row.e} {row.n} {row.from_room} {row.to_room} {row.place}")
                if row.from_room is not None and row.to_room is not None:
                    room_list.append((str(row.from_room).split('/')[-1].lower(),str(row.to_room).split('/')[-1].lower()))
                elif row.place is not None:
                    room_list.append((str(row.place).split('/')[-1].lower(),str(row.place).split('/')[-1].lower()))
                else:
                    room_list.append((None, None))
                time_list.append(float(row.sec))
            print(room_list)
            cumsum_time_list = [sum(time_list[:i+1]) for i in range(len(time_list))]
            cumsum_time_list_csv.append(cumsum_time_list)
            replace_flags = []
            previous_room = target # 最初にtargetにいてもカウントしない
            for i, (from_room, to_room) in enumerate(room_list):
                if from_room is None or to_room is None:
                    continue
                if 'xxx' in from_room or 'xxx' in to_room:
                    if self.use_gpt:
                        if i == 0:
                            time = (0, cumsum_time_list[i])
                        else:
                            time = (cumsum_time_list[i-1], cumsum_time_list[i])
                        prefix = self.file_dict_[activity]
                        movie_full_path = construct_full_path(prefix, scene, activity, viewpoint=4)
                        pred_rooms = query_gpt(movie_full_path, None, time, i, mode="room")
                        room_list[i] = pred_rooms
                        from_room, to_room = pred_rooms
                        replace_flags.append(True)
                    else:
                        replace_flags.append(False)
                        continue # roomxxxへのpathは計算できないのでスキップ
                count += count_teleport(from_room, to_room, scene, target)
                # if from_room != previous_room:
                #     count += count_teleport(from_room, to_room, scene, target)
                #     previous_room = from_room


            # Action間のテレポート処理(placexxxを置換後に行う)
            start_room = [room for room in room_list if room != (None, None) and 'xxx' not in room[0] and 'xxx' not in room[1]][0][0]
            count += count_teleport(before_teleport, start_room, scene, target)

            replace_flags_csv.append(replace_flags)
            room_list_csv.append(room_list.copy())
            before_teleport = [room for room in room_list if room != (None, None) and 'xxx' not in room[0] and 'xxx' not in room[1]][-1][1]
            print(count)
            count_list_csv.append(count - count_csv)
        
        print(f'Target room "{target}" entered {count} times.')
            
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
                fieldnames = ['filename', 'target_room', 'prediction', 'ground_truth', 'correct', 'activity', 'count', 'room_list', 'event_time_list', 'replace_flags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()
                
                for activity, count_csv, room_list, cumsum_time_list, replace_flags in zip(activity_list_csv, count_list_csv, room_list_csv, cumsum_time_list_csv, replace_flags_csv):
                    writer.writerow({
                        'filename': filename,
                        'target_room': target,
                        'prediction': count,
                        'ground_truth': gt,
                        'correct': count == gt,
                        'activity': activity,
                        'count': count_csv,
                        'room_list': room_list,
                        'event_time_list': cumsum_time_list,
                        'replace_flags': replace_flags
                    })

            return count == gt # 選択式だが、評価が難しいため、回数の一致で判定
        
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
                fieldnames = ['filename', 'target_room', 'target_count', 'predict_count', 'prediction', 'ground_truth', 'correct', 'activity', 'count', 'room_list', 'event_time_list', 'replace_flags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()
                
                for activity, count_csv, room_list, cumsum_time_list, replace_flags in zip(activity_list_csv, count_list_csv, room_list_csv, cumsum_time_list_csv, replace_flags_csv):
                    writer.writerow({
                        'filename': filename,
                        'target_room': target,
                        'target_count': target_count,
                        'predict_count': count,
                        'prediction': pred,
                        'ground_truth': gt,
                        'correct': pred == gt,
                        'activity': activity,
                        'count': count_csv,
                        'room_list': room_list,
                        'event_time_list': cumsum_time_list,
                        'replace_flags': replace_flags
                    })

            return pred == gt # Yes/Noが一致しているなら正解
        
        else:
            raise ValueError(f'Invalid question type: {question_type}')