from q1_solver import Q1Solver
import os

def list_questions():
    questions = []
    directory = '../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/MultiChoice/Q1'
    for filename in os.listdir(directory):
        if not filename == "q1-test.json":
            scene_id = filename.split('_')[2][-1]
            if scene_id in ['1', '2']:
                questions.append(filename) 
    print(questions)
    return questions

q1s = Q1Solver('mp4_files_list.txt', completedata=True)

questions = list_questions()
questions.sort()
correct = 0
total = 0
for question in questions:
    print(question)
    pred, gt = q1s.solve(f'../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/MultiChoice/Q1/{question}')
    if pred == gt:
        correct += 1
    total += 1

print(f'Accuracy: {correct}/{total} = {correct/total}')
# q1s.solve('../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/MultiChoice/Q1/q1_answer_scene1_Day1_bathroom.json')
# q1s.solve('../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/YesNo/Q1/q1_answer_scene2_Day1_bedroom.json')
