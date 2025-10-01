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

    visited_in_dls = {start_pos}  # Set chứa các vị trí đã ghé thăm trong lần lặp DLS này
    
    generated_count = 1 # Bắt đầu với nút gốc
    visited_count = 0

    while stack:
        current_pos, path = stack.pop()
        visited_count += 1

        # Nếu tìm thấy thức ăn, trả về kết quả
        if current_pos in food_pos_list:
            return {
                'path': path, 
                'visited_nodes': visited_in_dls, 
                'visited_count': visited_count,
                'generated_count': generated_count
            }

        # Dừng việc tìm kiếm nhánh này nếu đã vượt quá giới hạn độ sâu
        if len(path) > limit:
            continue

        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in reversed(neighbors): # Đảo ngược để có thứ tự duyệt giống đệ quy hơn (tùy chọn)
            if neighbor not in visited_in_dls:
                visited_in_dls.add(neighbor)
                new_path = path + [neighbor]
                stack.append((neighbor, new_path))
                generated_count += 1

    # Không tìm thấy đường đi trong giới hạn độ sâu này
 
    return {
        'path': None, 
        'visited_nodes': visited_in_dls, 
        'visited_count': visited_count,
        'generated_count': generated_count
    }


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

        return {'path': None, 'visited_nodes': [], 'generated_count': 0, 'visited_count': 0}

    layout = map_data.get('layout', [])
    max_depth = len(layout) * len(layout[0]) if layout and layout[0] else 500 # Giới hạn an toàn
    
    all_visited_nodes = set()
    total_generated_nodes = 0
    total_visited_count = 0

    # Lặp qua từng giới hạn độ sâu, từ 0 đến max_depth
    for depth in range(max_depth): 
        result = find_path_dls(start_pos, food_pos_list, map_data, snake_body, depth)
        
        total_generated_nodes += result.get('generated_count', 0)
        total_visited_count += result.get('visited_count', 0)
        
        # Gộp các nút đã duyệt từ mỗi lần lặp DLS để có cái nhìn tổng quan
        if result['visited_nodes']:
            all_visited_nodes.update(result['visited_nodes'])

        # Nếu DLS tìm thấy một đường đi, đó là đường đi ngắn nhất. Trả về ngay lập tức.
        if result['path'] is not None:
  
            return {
                'path': result['path'], 
                'visited_nodes': list(all_visited_nodes),
                'visited_count': total_visited_count,
                'generated_count': total_generated_nodes
            }

    # Nếu vòng lặp kết thúc mà không tìm thấy, tức là không có đường đi

    return {
        'path': None, 
        'visited_nodes': list(all_visited_nodes),
        'visited_count': total_visited_count,
        'generated_count': total_generated_nodes
    }
