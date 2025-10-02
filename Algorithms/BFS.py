"""
    Thuật toán BFS
"""
from collections import deque
from Algorithms.algorithm_helpers import get_valid_neighbors

def find_path_bfs(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm đường đi ngắn nhất từ start_pos đến bất kỳ thức ăn nào trong food_pos_list bằng BFS.
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách các tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Danh sách các tọa độ tạo thành đường đi, hoặc None nếu không tìm thấy.
    """
    if not food_pos_list:
        return {'path': None, 'visited_nodes': [], 'generated_count': 0, 'visited_count': 0}

    queue = deque([(start_pos, [start_pos])])  # Hàng đợi chứa (vị trí, đường đi tới vị trí đó)
    visited_set = {start_pos} # Set chứa các vị trí đã ghé thăm
    

    generated_count = 1 # Bắt đầu với nút gốc
    visited_count = 0

    while queue:

        # Tăng visited_count mỗi khi lấy 1 nút ra duyệt
        current_pos, path = queue.popleft()
        visited_count += 1

        # Nếu vị trí hiện tại là thức ăn, trả về đường đi
        if current_pos in food_pos_list:
            # Trả về dictionary với cấu trúc mớI
            return {
                'path': path, 
                'visited_nodes': list(visited_set),
                'visited_count': visited_count,
                'generated_count': generated_count
            }

        # Lấy các ô hàng xóm hợp lệ
        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited_set:
                visited_set.add(neighbor)
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))
                generated_count += 1


    # Trả về dictionary với cấu trúc mới khi không tìm thấy đường
    return {
        'path': None, 
        'visited_nodes': list(visited_set),
        'visited_count': visited_count,
        'generated_count': generated_count
    }
