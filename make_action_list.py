# all_actions.csv -> action_list.csv
# all_actions.csv: sparqlで取得したactionのリスト
# action_list.csv: actionのリスト
import pandas as pd

df = pd.read_csv('all_actions.csv')
actions = df['action'].tolist()
actions = list(set(actions))
action_list = []
for action in actions:
    action_list.append(action.split("/")[-1])
output_df = pd.DataFrame(action_list)
output_df.to_csv('action_list.csv', index=False, header=False)