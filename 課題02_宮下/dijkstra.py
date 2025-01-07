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
    return []



def count_teleport(start_node, goal_node, scene, target):
    if scene == 1:
        graph = {
            'bathroom11_scene1': [('bedroom75_scene1', 1)],
            'bedroom75_scene1': [('bathroom11_scene1', 1), ('kitchen209_scene1', 1)],
            'kitchen209_scene1': [('bedroom75_scene1', 1), ('livingroom342_scene1', 1)],
            'livingroom342_scene1': [('kitchen209_scene1', 1)]
        }
    elif scene == 2:
        graph = {
            'livingroom274_scene2': [('kitchen51_scene2', 1)],
            'kitchen51_scene2': [('livingroom274_scene2', 1), ('bedroom197_scene2', 1)],
            'bedroom197_scene2': [('kitchen51_scene2', 1)]
        }
    else: 
        raise NotImplementedError('Not implemented yet')

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