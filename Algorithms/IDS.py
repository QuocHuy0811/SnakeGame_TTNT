"""
    Thuật toán IDS (Iterative Deepening Search)
"""
from Algorithms.algorithm_helpers import get_valid_neighbors

def find_path_dls(start_pos, food_pos_list, map_data, snake_body, limit):
    """
    Thực hiện Tìm kiếm theo chiều sâu có giới hạn (Depth-Limited Search - DLS).
    Đây là một hàm trợ giúp cho IDS.
    :param limit: Giới hạn độ sâu cho việc tìm kiếm.
    """
    # DLS là DFS có limit

    stack = [(start_pos, [start_pos])]  # Ngăn xếp chứa (vị trí, đường đi)
    visited = {start_pos}  # Set chứa các vị trí đã ghé thăm trong lần lặp DLS này

    while stack:
        current_pos, path = stack.pop()

        # Nếu tìm thấy thức ăn, trả về kết quả
        if current_pos in food_pos_list:
            # Trả về cả đường đi và tập hợp các nút đã duyệt để trực quan hóa
            return {'path': path, 'visited': visited}

        # Dừng việc tìm kiếm nhánh này nếu đã vượt quá giới hạn độ sâu
        if len(path) > limit:
            continue

        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in reversed(neighbors): # Đảo ngược để có thứ tự duyệt giống đệ quy hơn (tùy chọn)
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                stack.append((neighbor, new_path))
    
    # Không tìm thấy đường đi trong giới hạn độ sâu này
    return {'path': None, 'visited': visited}


def find_path_ids(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm đường đi ngắn nhất từ start_pos đến thức ăn gần nhất bằng IDS.
    IDS kết hợp ưu điểm của DFS (bộ nhớ thấp) và BFS (tìm đường đi ngắn nhất).
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Danh sách các tọa độ tạo thành đường đi, hoặc None nếu không tìm thấy.
    """
    if not food_pos_list:
        return None

    # Giới hạn độ sâu tối đa có thể bằng tổng số ô trên bản đồ
    max_depth = len(map_data) * len(map_data[0]) 
    
    all_visited_nodes = set()

    # Lặp qua từng giới hạn độ sâu, từ 0 đến max_depth
    for depth in range(max_depth): 
        result = find_path_dls(start_pos, food_pos_list, map_data, snake_body, depth)
        
        # Gộp các nút đã duyệt từ mỗi lần lặp DLS để có cái nhìn tổng quan
        if result['visited']:
            all_visited_nodes.update(result['visited'])

        # Nếu DLS tìm thấy một đường đi, đó là đường đi ngắn nhất. Trả về ngay lập tức.
        if result['path'] is not None:
            return {'path': result['path'], 'visited': list(all_visited_nodes)}

    # Nếu vòng lặp kết thúc mà không tìm thấy, tức là không có đường đi
    return {'path': None, 'visited': list(all_visited_nodes)}