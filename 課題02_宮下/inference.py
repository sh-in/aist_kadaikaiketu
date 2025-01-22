from q1_solver import Q1Solver
from q2_solver import Q2Solver
import os
import argparse

def list_questions(question):
    if question == 'q1mult':
        directory = '../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/MultiChoice/Q1/'
    elif question == 'q1yesno':
        directory = '../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/YesNo/Q1/'
    elif question == 'q2mult':
        directory = '../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/MultiChoice/Q2/'
    elif question == 'q2yesno':
        directory = '../Knowledge-Graph-Reasoning-Challenge/DataSet/QA/YesNo/Q2/'
    else:
        raise ValueError(f'Invalid question type: {question}')
    questions = []
    for filename in os.listdir(directory):
        if not filename == "q1-test.json":
            questions.append(directory + filename) 
    print(questions)
    return questions

def parse_args():
    parser = argparse.ArgumentParser(description='Solve specified questions.')
    parser.add_argument('--question', type=str, required=True, help='Specify the question to solve (q1mult, q1yesno, q2mult, q2yesno, q5)')  # Update help text
    parser.add_argument('--completedata', action='store_true', help='Use complete data')
    parser.add_argument('--use_gpt', action='store_true', help='Use GPT-4o for missing data')
    return parser.parse_args()

def main():
    args = parse_args()
    print(f"==========Question: {args.question}, CompleteData: {args.completedata}==========")
    if args.question in ['q1mult', 'q1yesno']:
        q1s = Q1Solver('mp4_files_list.txt', qtype=args.question, use_gpt=args.use_gpt, completedata=args.completedata)
    elif args.question in ['q2mult', 'q2yesno']:
        q2s = Q2Solver('mp4_files_list.txt', qtype=args.question, use_gpt=args.use_gpt, completedata=args.completedata)
    
    questions = list_questions(args.question)
    questions.sort()
    correct = 0
    total = 0

    if args.question == 'q1mult':
        for question in questions[:50]:
            print(question)
            is_correct = q1s.solve(question)
            if is_correct:
                correct += 1
            total += 1
        print(f'Accuracy: {correct}/{total} = {correct/total}')

    elif args.question == 'q1yesno':
        for question in questions[:50]:
            print(question)
            is_correct = q1s.solve(question)
            if is_correct:
                correct += 1
            total += 1
        print(f'Accuracy: {correct}/{total} = {correct/total}')
        
    elif args.question == 'q2mult':
        for question in questions[:50]:
            print(question)
            is_correct = q2s.solve(question)
            if is_correct:
                correct += 1
            total += 1
        print(f'Accuracy: {correct}/{total} = {correct/total}')
    elif args.question == 'q2yesno':
        for question in questions[:50]:
            print(question)
            is_correct = q2s.solve(question)
            if is_correct:
                correct += 1
            total += 1
        print(f'Accuracy: {correct}/{total} = {correct/total}')
    else:
        raise ValueError(f'Invalid question type: {args.question}')

if __name__ == '__main__':
    main()