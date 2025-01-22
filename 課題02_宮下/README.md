# 課題2
Q1, Q2のMultiChoice, Yes/Noを実装 (鈴木さんの実装とは互換性がないため、ディレクトリを分けています)

## ファイル一覧
<pre>
.
├── action_list.txt # analyze_csv.pyで生成
├── act_movie_mapper.py
├── analyze_csv.py
├── comparison_result
│   ├── comparison_results_2025-01-19_23-29-28.csv # analyze_csv.pyで生成
│   └── ...
├── dijkstra.py
├── extract_rooms.py
├── gpt_inference.py
├── images
│   ├── bathroom11_scene1.jpg # prepare_room_image.pyで生成
│   ├── bathroom11_scene2.jpg
│   └── ...
├── inference.py
├── mp4_files_list.txt # act_movie_mapper.pyで生成
├── outputs
│   ├── q1mult_CompleteData_NoGPT_20250114_203050.csv
│   └── ...
├── prepare_room_image.py
├── q1_solver.py
├── q2_solver.py
└── README.md
</pre>
### 推論関連のファイル
- inference.py # q1_solver, q2_solverを呼び出す
- q1_solver.py
- q2_solver.py
### 事前準備のファイル

## 推論
`python generate_movie_list.py`によりactivity名と動画のパスの割り当てを記述するファイル`mp4_files_list.txt`を生成  
`python inference.py`によりscene1、scene2のQ1/MultiChoiceの問題を推論(結果の標準出力はresult.txtに示している)
