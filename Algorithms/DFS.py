"""
    Thuật toán DFS
"""
from Algorithms.algorithm_helpers import get_valid_neighbors

def find_path_dfs(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm một đường đi từ start_pos đến bất kỳ thức ăn nào bằng DFS.
    LƯU Ý: DFS không đảm bảo tìm ra đường đi ngắn nhất.
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Danh sách các tọa độ tạo thành đường đi, hoặc None nếu không tìm thấy.
    """
    if not food_pos_list:
        return None

    stack = [(start_pos, [start_pos])]  # Ngăn xếp chứa (vị trí, đường đi tới vị trí đó)
    visited = {start_pos} # Set chứa các vị trí đã ghé thăm

    while stack:
        # Lấy phần tử cuối cùng ra (LIFO)
        current_pos, path = stack.pop() 

        # Nếu vị trí hiện tại là thức ăn, trả về đường đi
        if current_pos in food_pos_list:
            return {'path': path, 'visited': list(visited)}

        # Lấy các ô hàng xóm hợp lệ
        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                stack.append((neighbor, new_path))

    return {'path': None, 'visited': list(visited)} # Không tìm thấy đường đi