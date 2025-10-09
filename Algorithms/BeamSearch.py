# Algorithms/BeamSearch.py

import heapq
from Algorithms.algorithm_helpers import get_valid_neighbors, manhattan_distance

def find_path_beam_search(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm đường đi từ start_pos đến thức ăn gần nhất bằng Beam Search.
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Dictionary chứa đường đi và các thống kê.
    """
    # --- THAM SỐ CỦA BEAM SEARCH ---
    BEAM_WIDTH = 5  # Giữ lại 3 nút tốt nhất ở mỗi cấp độ

    if not food_pos_list:
        return {'path': None, 'visited_nodes': [], 'generated_count': 0, 'visited_count': 0}

    # Chọn mục tiêu là thức ăn gần nhất theo heuristic
    target_pos = min(food_pos_list, key=lambda food: manhattan_distance(start_pos, food))

    # Hàng đợi ưu tiên chứa (h_score, vị trí, đường đi)
    pq = [(manhattan_distance(start_pos, target_pos), start_pos, [start_pos])]
    
    visited_set = {start_pos}
    generated_count = 1
    visited_count = 0

    while pq:
        # Lấy tất cả các nút hiện tại trong hàng đợi để xử lý cấp độ này
        current_level_nodes = [heapq.heappop(pq) for _ in range(len(pq))]
        visited_count += len(current_level_nodes)
        
        next_level_candidates = []

        for h_score, current_pos, path in current_level_nodes:
            if current_pos == target_pos:
                return {
                    'path': path,
                    'visited_nodes': list(visited_set),
                    'visited_count': visited_count,
                    'generated_count': generated_count
                }

            neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
            for neighbor in neighbors:
                if neighbor not in visited_set:
                    visited_set.add(neighbor)
                    new_h = manhattan_distance(neighbor, target_pos)
                    # Thêm tất cả các nút con hợp lệ vào danh sách ứng viên
                    heapq.heappush(next_level_candidates, (new_h, neighbor, path + [neighbor]))
                    generated_count += 1
        
        # --- BƯỚC CẮT TỈA (PRUNING) CỦA BEAM SEARCH ---
        # Chỉ giữ lại BEAM_WIDTH ứng viên tốt nhất cho cấp độ tiếp theo
        
        # Tạo hàng đợi mới từ các ứng viên tốt nhất
        pq = []
        num_to_keep = min(BEAM_WIDTH, len(next_level_candidates))
        for _ in range(num_to_keep):
            heapq.heappush(pq, heapq.heappop(next_level_candidates))


    # Không tìm thấy đường đi
    return {
        'path': None,
        'visited_nodes': list(visited_set),
        'visited_count': visited_count,
        'generated_count': generated_count
    }