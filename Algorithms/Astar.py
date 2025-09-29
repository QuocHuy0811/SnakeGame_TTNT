"""
    Thuật toán A*
"""
import heapq
from Algorithms.algorithm_helpers import get_valid_neighbors, manhattan_distance

def find_path_astar(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm đường đi ngắn nhất từ start_pos đến thức ăn gần nhất bằng A*.
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Danh sách các tọa độ tạo thành đường đi, hoặc None nếu không tìm thấy.
    """
    
    # A* cần tìm đường đến một mục tiêu cụ thể, nên ta sẽ chọn mục tiêu gần nhất
    # dựa trên khoảng cách Manhattan ban đầu.
    if not food_pos_list:
        return None
    
    target_pos = min(food_pos_list, key=lambda food: manhattan_distance(start_pos, food))

    # Hàng đợi ưu tiên chứa (f_score, g_score, vị trí, đường đi)
    # f_score = g_score + h_score
    g_score = 0                                         # Chi phí đã đi
    h_score = manhattan_distance(start_pos, target_pos) # Chi phí ước tính để đến đích
    f_score = g_score + h_score
    
    pq = [(f_score, g_score, start_pos, [start_pos])]
    visited = {start_pos}

    while pq:
        _, current_g, current_pos, path = heapq.heappop(pq)

        if current_pos == target_pos:
            return {'path': path, 'visited': list(visited)}

        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_g = current_g + 1
                new_h = manhattan_distance(neighbor, target_pos)
                new_f = new_g + new_h
                heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))

    return {'path': None, 'visited': list(visited)} # Không tìm thấy đường đi