# 課題2
Q1, Q2のMultiChoice, Yes/Noを実装 (鈴木さんの実装とは互換性がないため、ディレクトリを分けています)

## ファイル一覧
<pre>
.
├── action_list.txt # analyze_csv.pyで生成
├── act_movie_mapper.py # Action名からビデオのパスを取得するユーティリティ
├── analyze_csv.py # inference.pyで出力したcsvファイル(outputs/*.csv)から定量評価、事例別の比較を行うスクリプト
├── comparison_result
│   ├── comparison_results_2025-01-19_23-29-28.csv # analyze_csv.pyで生成
│   └── ...
├── dijkstra.py # q1_solver.pyに呼び出される
├── extract_rooms.py # room名一覧を取得するのに使用、dijkstra.pyのグラフ作成の参考に
├── gpt_inference.py # q1,q2_solver.pyに呼び出される
├── images # Q1の補完に使う部屋の画像
│   ├── bathroom11_scene1.jpg # prepare_room_image.pyで生成
│   ├── bathroom11_scene2.jpg
│   └── ...
├── inference.py
├── mp4_files_list.txt # act_movie_mapper.pyで生成
├── outputs
│   ├── q1mult_CompleteData_NoGPT_20250114_203050.csv # inference.pyで生成
│   └── ...
├── prepare_room_image.py # Q1の補完に使う部屋の画像を取得
├── q1_solver.py # inference.pyに呼び出される
├── q2_solver.py # inference.pyに呼び出される
└── README.md
</pre>
## 事前準備 
**(事前準備で生成されたファイルがレポジトリに含まれているため、同じデータで実行する場合は不要)**  
`../Knowledge-Graph-Reasoning-Challenge/`以下にDataset( https://github.com/KGRC4SI/DataSet/tree/kgrc4si?tab=readme-ov-file )とmovie( https://kgrc4si.home.kg/Movie/ )が配置されていればファイルパスは変更しなくても動作すると思います

### アクションリストの生成 (action_list.txt)
CompleteData、q2multで`inference.py`を動作させた後、出力のcsvファイルを用いて、`python analyze_csv.py --input_files ./outputs/{output}.csv --mode get_action_list`で生成

### アクティビティ名からファイルパス取得の下準備 (mp4_files_list.txt)
`python act_movie_mapper.py`で出力(ディレクトリはハードコードされています)

### 部屋の画像の取得 (images/*.jpg)
mp4_files_list.txtが必要で、`python prepare_room_image.py`

## 推論
`OPENAI_API_KEY={実際のAPIキー} python inference.py --question q1mult --use_gpt`    
- --question 解く問題を選択する引数で、以下の中から1つを入力: q1mult, q2mult, q1yesno, q2yesno
- --completedata フラグを付けるとCompleteDataでの推論、つけないとPartiallyMissingDataでの推論
- --use_gpt フラグを付けるとPartiallyMissingDataでの推論時、GPTでの補完を行うようになる(つけないと補完せず、欠損したデータを無視する)
inference.pyは50問だけ解くように制限されているので、全問題に対して評価する場合は適宜修正してください。

## 分析
inference.pyを実行すると`./outputs/{question}_{Complete or Missing}_{GPT Completion}_{DateTime}.csv}`に各問題の推論結果や正解、推論に使った部屋の経路やアクション一覧などの情報が記載されたcsvが出力されます。
`python generate_movie_list.py`によりactivity名と動画のパスの割り当てを記述するファイル`mp4_files_list.txt`を生成  
`python inference.py`によりscene1、scene2のQ1/MultiChoiceの問題を推論(結果の標準出力はresult.txtに示している)
