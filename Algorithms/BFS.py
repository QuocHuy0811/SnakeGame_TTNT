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
    queue = deque([(start_pos, [start_pos])])  # Hàng đợi chứa (vị trí, đường đi tới vị trí đó)
    visited = {start_pos} # Set chứa các vị trí đã ghé thăm

    while queue:
        #Lấy vị trí hiện tại và đường đi đến vị trí đó (Đầu hàng đợi)
        current_pos, path = queue.popleft()

        # Nếu vị trí hiện tại là thức ăn, trả về đường đi
        if current_pos in food_pos_list:
            return {'path': path, 'visited': list(visited)}

        # Lấy các ô hàng xóm hợp lệ
        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                queue.append((neighbor, new_path))

    return {'path': None, 'visited': list(visited)} # Không tìm thấy đường đi