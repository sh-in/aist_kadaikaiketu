# 課題解決型演習
## 実装内容について(鈴木担当分)
main.pyをベースとして、QAに解答する機能を実装しました。  
引数としては、
- qa_type: QAの種類を指定する引数: MultiChoice, YesNo(実装途中)
- qa_num: QAの種類を指定する引数: 3, 4  

コード実行例:   
`python main.py --qa_type MultiChoice --qa_num 3`

## パスの指定について
main.py, openai_gpt.pyにはデータセットへのパスを指定するための変数があります。  
openai_gpt.pyにはAPI_KEYを指定する必要があります。

## 事前準備
1. prepare.pyを実行することによって、activityと動画の対応リストの作成
2. make_action_list.pyを実行することによって、データセットに存在する行動のリストを作成

## 宮下担当分
宮下担当分のQ1, 2については「課題02_宮下」のディレクトリいかに格納しています。