"""
    Thuật toán Greedy
"""
import heapq
from Algorithms.algorithm_helpers import get_valid_neighbors, manhattan_distance, euclidean_distance

def find_path_greedy(start_pos, food_pos_list, map_data, snake_body, heuristic_func=manhattan_distance):
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
        # Trả về đúng định dạng mới
        return {'path': None, 'visited_nodes': [], 'generated_count': 0, 'visited_count': 0}
    
    # Greedy cần một mục tiêu cụ thể, ta sẽ chọn mục tiêu gần nhất theo heuristic ban đầu.
    target_pos = min(food_pos_list, key=lambda food: heuristic_func(start_pos, food))

    # Hàng đợi ưu tiên chỉ chứa (h_score, vị trí, đường đi)
    h_score = heuristic_func(start_pos, target_pos)
    
    pq = [(h_score, start_pos, [start_pos])]

    visited_set = {start_pos}
    visited_order = []

    generated_count = 1 # Bắt đầu với nút gốc
    visited_count = 0

    while pq:

        _, current_pos, path = heapq.heappop(pq)
        visited_count += 1
        visited_order.append(current_pos)

        if current_pos == target_pos:
            return {
                'path': path, 
                'visited_nodes': visited_order,
                'visited_count': visited_count,
                'generated_count': generated_count
            }

        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited_set:
                visited_set.add(neighbor)
                new_h = heuristic_func(neighbor, target_pos)
                heapq.heappush(pq, (new_h, neighbor, path + [neighbor]))
                generated_count += 1

    return {
        'path': None, 
        'visited_nodes': visited_order,
        'visited_count': visited_count,
        'generated_count': generated_count
    }