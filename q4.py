import query
import openai_gpt

# Q4: kitchenに入る直前に何をしたか
def q4(PROJECT_PATH, activities, answer, target_place, scene, accuracy, file_dict, action_list, qa_num):
    in_kitchen = False
    action = None
    action_label = None
    prev_action = None
    prev_action_label = None
    video_path = None
    first_places = []
    last_places = []
    actions = []
    for i,activity in enumerate(activities):
        event_num = query.do_sparql_query_to_get_events(PROJECT_PATH, activity, scene)
        # print("-"*20)
        # print("activity:", activity)
        time = 0
        for j in range(int(event_num)):
            first_place = query.do_sparql_query_to_get_first_place(PROJECT_PATH, activity, scene, j)
            last_place = query.do_sparql_query_to_get_last_place(PROJECT_PATH, activity, scene, j)
            place = first_place
            action, action_label = query.do_sparql_query_to_get_action(PROJECT_PATH, activity, scene, j)
            duration = float(query.do_sparql_query_to_get_time(PROJECT_PATH, activity, scene, j))
            # placeがNoneの場合に、GPTによる補完を実施
            if place is None:
                video_path, place = openai_gpt.call_openai_api(PROJECT_PATH, scene, activity, file_dict, j, time, duration, "room")            
            first_places.append(first_place)
            last_places.append(last_place)
            actions.append(action_label)
            if "Action" in action or action_label is None:
                # actionがActionXXX[0,1,2,3]の場合が存在する←いったんnoneとして処理
                video_path, action_label = openai_gpt.call_openai_api(PROJECT_PATH, scene, activity, file_dict, j, time, duration, "action", action_list, qa_num)
                continue

            time += duration
            # placeがkitchenの場合
            if place == target_place:
                in_kitchen = True
                if prev_action is not None:
                    action = prev_action
                    action_label = prev_action_label
                break
            else:
                # placeがkitchenでない場合、prev_actionを更新
                prev_action = action
                prev_action_label = action_label
        # 回答を見つけたときにループを抜けるための処理
        if place == target_place and in_kitchen:
            break
    # 回答が一致しているか確認
    print("first_places:", first_places)
    print("last_places:", last_places)
    print("actions:", actions)
    print("answer:", answer)
    print("action_label:", action_label)
    if action_label is None:
        print("None")
    elif action_label.upper() == answer:
        print("correct")
        accuracy += 1
    else:
        print("incorrect")
    return action_label, video_path, accuracy