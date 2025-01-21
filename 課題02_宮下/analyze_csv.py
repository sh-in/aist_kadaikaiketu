import csv
from collections import defaultdict
import argparse
from datetime import datetime

def evaluate(input_file):
    print(f"evaluate {input_file}")
    previous_filename = None

    total = 0
    count = 0

    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            filename = row['filename']
            if filename == previous_filename:
                continue
            correct = row['correct'] == 'True'
            total += correct
            count += 1
            previous_filename = filename
    print(input_file)
    print(f'Correct: {total}/{count}')
    print(f'Accuracy: {total / count:.2%}')

def get_action_list(input_file):
    print(f"get action list from {input_file}")
    action_set = set()
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            actions = row['action_list'].strip('][').split(', ')
            for action in actions:
                action_set.add(action.strip("'"))
    with open('action_list.txt', 'w') as outfile:
        for action in sorted(action_set):
            outfile.write(f'{action}\n')
    
def compare(input_files):
    results = defaultdict(lambda: {'correct': 0, 'total': 0, 'mae_sum': 0, 'predictions': {}})
    previous_filename = None
    metrics = defaultdict(lambda: {'correct': 0, 'total': 0, 'mae_sum': 0})
    
    for input_file in input_files:
        count=0
        with open(input_file, 'r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row['filename'] == previous_filename:
                    continue
                previous_filename = row['filename']
                filename = row['filename']
                correct = row['correct'] == 'True'
                prediction = float(row['prediction'])
                ground_truth = float(row['ground_truth'])
                mae = abs(prediction - ground_truth)
                metrics[input_file]['correct'] += correct
                metrics[input_file]['total'] += 1
                metrics[input_file]['mae_sum'] += mae
                results[filename]['predictions'][input_file] = prediction
                results[filename]['ground_truth'] = ground_truth
                count += 1
                if count >= 50:
                    break
                
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_filename = f'comparison_results_{timestamp}.csv'
    
    with open(output_filename, 'w', newline='') as outfile:
        fieldnames = ['filename'] + input_files + ['ground_truth']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for filename, data in results.items():
            row = {'filename': filename, 'ground_truth': data['ground_truth']}
            for input_file in input_files:
                row[input_file] = data['predictions'].get(input_file, 'N/A')
            writer.writerow(row)
    
    print('Results:')
    for input_file, data in metrics.items():
        print(input_file)
        print(f'Correct: {data["correct"]}/{data["total"]}')
        print(f'Accuracy: {data["correct"] / data["total"]:.2%}')
        print(f'MAE: {data["mae_sum"] / data["total"]:.2f}')

def main():    
    # 入力ファイルと出力ファイルのパス
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Process CSV file to calculate average correct values.')
    parser.add_argument('--input_files', type=str, help='Path to the input CSV file', nargs='+')
    parser.add_argument('--mode', type=str, required=True, help='Mode to run (evaluate, get_action_list, compare)')
    args = parser.parse_args()
    
    if args.mode == 'evaluate':
        evaluate(args.input_files[0])
    elif args.mode == 'get_action_list':
        get_action_list(args.input_files[0])
    elif args.mode == 'compare':
        compare(args.input_files)
    else:
        print(f'Invalid mode: {args.mode}')

if __name__ == '__main__':
    main()
