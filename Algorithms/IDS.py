"""
    Thuật toán IDS (Iterative Deepening Search)
"""
from Algorithms.algorithm_helpers import get_valid_neighbors

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
        return {
            'path': None, 
            'visited_nodes': [], 
            'generated_count': 0, 
            'visited_count': 0
        }

    layout = map_data.get('layout', [])
    max_depth = len(layout) * len(layout[0]) if layout and layout[0] else 500 # Giới hạn an toàn
    
    generated_count = 1
    visited_count = 0
    
    visited_order = []
    unique_in_visited = set()

    # Lặp qua từng giới hạn độ sâu, từ 0 đến max_depth
    for depth in range(1, max_depth): 
        current_depth_visited_set = {start_pos}
        stack = [(start_pos, [start_pos])]

        # Mô phỏng lại DLS (tìm kiếm DFS có chiều sâu)
        while stack:
            current_pos, path = stack.pop()

            if current_pos not in unique_in_visited:
                visited_order.append(current_pos)
                unique_in_visited.add(current_pos)

            visited_count += 1

            if current_pos in food_pos_list:
                return {
                    'path': path,
                    'visited_nodes': visited_order,
                    'visited_count': visited_count,
                    'generated_count': generated_count
                }
            
            if len(path) >= depth:
                continue
            
            neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
            for neighbor in reversed(neighbors): # Đảo ngược để có thứ tự duyệt giống đệ quy hơn (tùy chọn)
                if neighbor not in current_depth_visited_set:
                    current_depth_visited_set.add(neighbor)
                    stack.append((neighbor, path + [neighbor]))
                    generated_count += 1
        
    return {
        'path': None,
        'visited_nodes': visited_order,
        'visited_count': visited_count,
        'generated_count': generated_count
    }