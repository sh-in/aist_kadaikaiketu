import query
import openai_gpt

# Q3: kitchenに入った直後に何をしたか
def q3(PROJECT_PATH, activities, answer, target_place, scene, accuracy, file_dict, action_list):
    in_kitchen = False
    first_target_place = False
    action = None
    action_label = None
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
            action, action_label = query.do_sparql_query_to_get_action(PROJECT_PATH, activity, scene, j)
            place = first_place
            
            duration = float(query.do_sparql_query_to_get_time(PROJECT_PATH, activity, scene, j))
            # print("place:", place)
            # placeがNoneの場合に、GPTによる補完を実施
            if place is None:
                video_path, place = openai_gpt.call_openai_api(PROJECT_PATH, scene, activity, file_dict, j, time, duration, "room")
            first_places.append(first_place)
            last_places.append(last_place)
            actions.append(action_label)
            # placeがkitchenの場合
            if place == target_place:
                # 前回のplaceがkitchenの場合actionを取得
                # そうでない場合、in_kitchenをTrueにする
                if in_kitchen:
                    action, action_label = query.do_sparql_query_to_get_action(PROJECT_PATH, activity, scene, j)
                    if action_label=="walk":
                        if last_place!=target_place:
                            in_kitchen = False
                        continue
                    elif "Action" in action or action_label is None:
                        # actionがNoneの場合に、GPTによる補完を実施
                        video_path, action_label = openai_gpt.call_openai_api(PROJECT_PATH, scene, activity, file_dict, j, time, duration, "action", action_list)
                        break
                    else:
                        break
                elif j==0:
                    in_kitchen = True
                    first_target_place = True
                else:
                    in_kitchen = True
            elif first_target_place:
                action, action_label = query.do_sparql_query_to_get_action(PROJECT_PATH, activity, scene, j)
                if action_label=="walk":
                    if last_place!=target_place:
                        in_kitchen = False
                    continue
                elif "Action" in action or action_label is None:
                    # actionがNoneの場合に、GPTによる補完を実施
                    video_path, action_label = openai_gpt.call_openai_api(PROJECT_PATH, scene, activity, file_dict, j, time, duration, "action", action_list)
                    break
                else:
                    break
            elif last_place == target_place:
                in_kitchen = True
            else:
                # placeがkitchenでない場合、in_kitchenをFalseにする
                in_kitchen = False
            time += duration
        # 回答を見つけたときにループを抜けるための処理
        if place == target_place and in_kitchen:
            break
        elif first_target_place:
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