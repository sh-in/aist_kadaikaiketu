import json
import pdb
import rdflib
from dijkstra import count_teleport

class Q1Solver:
    def __init__(self, mp4_file_list_path, completedata=False):
        self.file_dict_ = {}
        with open(mp4_file_list_path, 'r') as f:
            for line in f:
                file_name, file_path = line.strip().split(',')
                self.file_dict_[file_name] = file_path
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
        output: prediction, ground truth
        """
        print("====================================================")
        # JSONファイルを読み込む
        with open(filename, 'r') as file:
            data = json.load(file)
        
        # "livingroom"を含むquestion部分にアクセス
        question = data.get('question', '') # 第二引数はデフォルト値
        question_words = question.split()
        target = question_words[-1].rstrip('?')
        print(f'Question: {question}, Target: {target}')

        # scenarioにアクセス
        scenario = data.get('senario', '')
        with open(self.episode_prefix_ + scenario + ".json", 'r') as file:
            scenario_data = json.load(file)
        activities = scenario_data['data']['activities']
        scene = scenario_data['data']['scene']
        count = 0 # 部屋の入室回数のカウント
        before_teleport = target # テレポート前の部屋にいたかどうか

        # 各activityについて、部屋の入室回数の計測
        for activity in activities:
            print(activity)
            with open(self.rdf_prefix_ + activity + "_scene" + str(scene) + ".ttl", 'r') as file:
                g = rdflib.Graph()
                g.parse(file, format='turtle')
            with open (self.rdf_prefix_ + "add_places.ttl", 'r') as file:
                g.parse(file, format='turtle')
            
            query = """
            PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
            PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
            SELECT *
            WHERE {
                ?e :from ?from_room .
                ?e :to ?to_room .
                ?e :eventNumber ?n .
            } order by ?n limit 100"""

            result = g.query(query)
            room_list = []
            for row in result:
                # print(f"{row.e} {row.room} {row.n}")
                room_list.append((str(row.from_room).split('/')[-1].lower(),str(row.to_room).split('/')[-1].lower()))
            if room_list == []: # 普通はfrom_toで取ればよいが、動かない場合はplaceのみ取得
                query = """
                        PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
                        PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
                        SELECT *
                        WHERE {
                            ?e :place ?room .
                            ?e :eventNumber ?n .
                        } order by ?n limit 100"""
                result = g.query(query)
                for row in result:
                    res_text = str(row.room).split('/')[-1].lower(),str(row.room).split('/')[-1].lower()
                room_list.append((res_text, res_text)) # from と toを同じとして扱う
            print(room_list)
            # Action間のテレポート処理
            count += count_teleport(before_teleport, room_list[0][0], scene, target)
            
            previous_room = target # 最初にtargetにいてもカウントしない
            for from_room, to_room in room_list:
                if from_room != previous_room:
                    count += count_teleport(from_room, to_room, scene, target)
                    previous_room = from_room
            
            before_teleport = room_list[-1][1]
            print(count)
        
        print(f'Target room "{target}" entered {count} times.')
            
        gt = 0
        # answersの各要素にアクセス
        answers = data.get('answers', [])
        for answer in answers:
            answer_id = answer.get('id')
            answer_text = answer.get('answer')
            correct = answer.get('correct')
            if correct:
                gt = answer_text
            print(f'Answer ID: {answer_id}, Answer: {answer_text}, Correct: {correct}')
        return count, gt # 選択式だが、選択肢に予測がない場合の対処が難しい(ニブイチ回答すると、accuracyがかさ増しされてしまう)