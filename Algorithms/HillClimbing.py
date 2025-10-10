from Algorithms.algorithm_helpers import get_valid_neighbors, manhattan_distance

def find_path_hill_climbing(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm MỘT bước đi tiếp theo tốt nhất bằng thuật toán Hill Climbing.
    Nó chỉ trả về một đường đi ngắn gồm vị trí hiện tại và bước đi tiếp theo.
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Dictionary chứa đường đi 2 bước và các thống kê.
    """
    if not food_pos_list:
        return {'path': None, 'visited_nodes': [], 'generated_count': 0, 'visited_count': 0}

    # 1. Chọn mục tiêu là thức ăn gần nhất
    target_pos = min(food_pos_list, key=lambda food: manhattan_distance(start_pos, food))

    # 2. Tìm tất cả các hàng xóm hợp lệ
    neighbors = get_valid_neighbors(start_pos, map_data, snake_body)
    
    visited_order = [start_pos] + neighbors

    # Thống kê cho việc trực quan hóa
    generated_count = len(neighbors)
    visited_count = len(neighbors) # Coi như đã duyệt tất cả các hàng xóm
    

    if not neighbors:
        # Bị kẹt, không có đường đi
        return {
            'path': None, 
            'visited_nodes': visited_order, 
            'generated_count': 1, 
            'visited_count': 1
        }

    # 3. Đánh giá tất cả các hàng xóm và chọn ra hàng xóm tốt nhất
    # (hàng xóm có khoảng cách Manhattan đến mục tiêu nhỏ nhất)
    best_neighbor = min(neighbors, key=lambda pos: manhattan_distance(pos, target_pos))

    # 4. Trả về một "đường đi" chỉ gồm 2 bước
    path = [start_pos, best_neighbor]

    return {
        'path': path,
        'visited_nodes': visited_order,
        'visited_count': visited_count,
        'generated_count': generated_count
    }