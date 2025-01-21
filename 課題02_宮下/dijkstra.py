import heapq

def dijkstra_(graph, start, goal):
    queue = [(0, start, [])] # ヒープは第一要素でソートされる
    seen = set()
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in seen:
            continue
        path = path + [node]
        seen.add(node)
        if node == goal:
            return path
        for next_node, weight in graph.get(node, []):
            if next_node not in seen:
                heapq.heappush(queue, (cost + weight, next_node, path))
    raise ValueError(f"No path found {start} => {goal}")
    # return []



def count_teleport(start_node, goal_node, scene, target): # idが不明の部屋については部屋名+scene_idをとりあえず入力
    if scene == 1:
        graph = {
            'bathroom11_scene1': [('bedroom75_scene1', 1), ('toilet46_scene1', 1)],
            'toilet46_scene1': [('bathroom11_scene1', 1)],
            'bedroom75_scene1': [('bathroom11_scene1', 1), ('kitchen209_scene1', 1)],
            'kitchen209_scene1': [('bedroom75_scene1', 1), ('livingroom342_scene1', 1)],
            'livingroom342_scene1': [('kitchen209_scene1', 1)]
        }
    elif scene == 2:
        graph = {
            'livingroom274_scene2': [('kitchen51_scene2', 1)],
            'kitchen51_scene2': [('livingroom274_scene2', 1), ('bedroom197_scene2', 1), ('bathroom11_scene2', 1)],
            'bedroom197_scene2': [('kitchen51_scene2', 1)],
            'bathroom11_scene2': [('kitchen51_scene2', 1), ('toilet_scene2', 1)],
            'toilet_scene2': [('bathroom11_scene2', 1)]
        }
    elif scene == 3:
        graph = {
            'bedroom_scene3': [('livingroom194_scene3', 1)],
            'livingroom194_scene3': [('bedroom_scene3', 1), ('kitchen11_scene3', 1)],
            'kitchen11_scene3': [('livingroom194_scene3', 1), ('bedroom358_scene3', 1)],
            'bedroom358_scene3': [('kitchen11_scene3', 1), ('bathroom297_scene3', 1)],
            'bathroom297_scene3': [('bedroom358_scene3', 1), ('toilet333_scene3', 1)],
            'toilet333_scene3': [('bathroom297_scene3', 1)]
        }
    elif scene == 4:
        graph = {
            'toilet193_scene4': [('bathroom177_scene4', 1)],
            'bathroom177_scene4': [('toilet193_scene4', 1), ('kitchen11_scene4', 1)],
            'kitchen11_scene4': [('bathroom177_scene4', 1), ('bedroom216_scene4', 1)],
            'bedroom216_scene4': [('kitchen11_scene4', 1), ('livingroom274_scene4', 1)],
            'livingroom274_scene4': [('bedroom216_scene4', 1)]
        }
    elif scene == 5:
        graph = {
            'toilet315_scene5': [('bathroom295_scene5', 1)],
            'bathroom295_scene5': [('toilet315_scene5', 1), ('livingroom11_scene5', 1)],
            'livingroom11_scene5': [('bathroom295_scene5', 1), ('kitchen112_scene5', 1)],
            'kitchen112_scene5': [('livingroom11_scene5', 1), ('bedroom231_scene5', 1)],
            'bedroom231_scene5': [('kitchen112_scene5', 1)]
        }
    elif scene == 6:
        graph = {
            'kitchen161_scene6': [('bedroom70_scene6', 1)],
            'bedroom70_scene6': [('kitchen161_scene6', 1), ('livingroom260_scene6', 1), ('bathroom11_scene6', 1)],
            'livingroom260_scene6': [('bedroom70_scene6', 1)],
            'bathroom11_scene6': [('bedroom70_scene6', 1), ('toilet46_scene6', 1)],
            'toilet46_scene6': [('bathroom11_scene6', 1)]
        }
    elif scene == 7:
        graph = {
            'bedroom_scene7': [('kitchen56_scene7', 1)],
            'kitchen56_scene7': [('bedroom_scene7', 1), ('bathroom11_scene7', 1), ('livingroom205_scene7', 1)],
            'bathroom11_scene7': [('kitchen56_scene7', 1), ('toilet_scene7', 1)],
            'toilet_scene7': [('bathroom11_scene7', 1)],
            'livingroom205_scene7': [('kitchen56_scene7', 1)]
        }
    else: 
        raise NotImplementedError('Not implemented yet')

    # 初回の推論では、回数のカウントが不要なため、0を返す
    if start_node is None:
        return 0
    shortest_path = dijkstra_(graph, start_node, goal_node)
    for room in shortest_path[1:]:
        if target in room: # 例: kitchen in kitchen209_scene1
            return 1
    return 0
    
# Example usage2:
# print("Graph: bathroom <-> livingroom <-> kitchen <-> bedroom")
# print("Start: bathroom, Goal: bedroom, Target: livingroom", count_teleport('bathroom', 'bedroom', 1, 'livingroom')) # 1
# print("Start: bathroom, Goal: bedroom, Target: kitchen", count_teleport('bathroom', 'bedroom', 1, 'kitchen')) # 1
# print("Start: bathroom, Goal: bedroom, Target: bedroom", count_teleport('bathroom', 'bedroom', 1, 'bedroom')) # 1
# print("Start: bathroom, Goal: bedroom, Target: bathroom", count_teleport('bathroom', 'bedroom', 1, 'bathroom')) # 0

# # Example usage:
# graph = {
#     'A': [('B', 1), ('C', 4)],
#     'B': [('A', 1), ('C', 2), ('D', 5)],
#     'C': [('A', 4), ('B', 2), ('D', 1)],
#     'D': [('B', 5), ('C', 1)]
# }

# start_node = 'A'
# goal_node = 'A'
# shortest_path = dijkstra_(graph, start_node, goal_node)
# print("Shortest path from {} to {} is: {}".format(start_node, goal_node, shortest_path)) # 開始と終了が同じ時は、1つのノードのみを返す