# Algorithms/DLS.py

from Algorithms.algorithm_helpers import get_valid_neighbors
import config

def find_path_dls(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm một đường đi từ start_pos đến thức ăn bằng DLS (Depth-Limited Search).
     phiên bản này đã được sửa lỗi và tinh chỉnh.
    """
    
    # === THAY ĐỔI QUAN TRỌNG NHẤT ===
    # Giảm giới hạn độ sâu xuống một con số hợp lý (ví dụ: 150).
    # Điều này ngăn thuật toán bị "lạc" trong các nhánh tìm kiếm quá dài trên các map phức tạp,
    # giải quyết vấn đề game bị "treo".
    depth_limit = 150

    # Stack chứa (vị trí, đường đi tới vị trí đó)
    stack = [(start_pos, [start_pos])]
    
    # Sử dụng `visited` để tìm kiếm hiệu quả, giống như thuật toán DFS gốc của bạn.
    visited = {start_pos}

    while stack:
        current_pos, path = stack.pop()

        # Nếu tìm thấy thức ăn, trả về kết quả
        if current_pos in food_pos_list:
            # Trả về tập `visited` để phục vụ cho việc visualize
            return {'path': path, 'visited': list(visited)}

        # Nếu đường đi đã dài bằng giới hạn, không đi tiếp nhánh này
        if len(path) >= depth_limit:
            continue

        # Lấy các ô hàng xóm hợp lệ
        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                stack.append((neighbor, new_path))

    # Nếu không tìm thấy đường đi sau khi duyệt hết stack
    return {'path': None, 'visited': list(visited)}