"""
    Thuật toán Greedy
"""
# Algorithms/Greedy.py
import heapq
from Algorithms.algorithm_helpers import get_valid_neighbors, manhattan_distance

def find_path_greedy(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm đường đi từ start_pos đến thức ăn gần nhất bằng thuật toán Greedy Best-First Search.
    LƯU Ý: Thuật toán này nhanh nhưng không đảm bảo tìm ra đường đi ngắn nhất.
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Danh sách các tọa độ tạo thành đường đi, hoặc None nếu không tìm thấy.
    """
    if not food_pos_list:
        return None
    
    # Greedy cần một mục tiêu cụ thể, ta sẽ chọn mục tiêu gần nhất theo heuristic ban đầu.
    target_pos = min(food_pos_list, key=lambda food: manhattan_distance(start_pos, food))

    # Hàng đợi ưu tiên chỉ chứa (h_score, vị trí, đường đi)
    h_score = manhattan_distance(start_pos, target_pos)
    
    pq = [(h_score, start_pos, [start_pos])]
    visited = {start_pos}

    while pq:
        _, current_pos, path = heapq.heappop(pq)

        if current_pos == target_pos:
            return path

        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_h = manhattan_distance(neighbor, target_pos)
                heapq.heappush(pq, (new_h, neighbor, path + [neighbor]))

    return None # Không tìm thấy đường đi