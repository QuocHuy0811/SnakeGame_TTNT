"""
    Thuật toán UCS
"""
import heapq
from Algorithms.algorithm_helpers import get_valid_neighbors

def find_path_ucs(start_pos, food_pos_list, map_data, snake_body):
    """
    Tìm đường đi ngắn nhất từ start_pos đến thức ăn gần nhất bằng UCS.
    Trong trường hợp chi phí mỗi bước là 1, UCS hoạt động giống hệt BFS.
    :param start_pos: Tọa độ (x, y) của đầu rắn.
    :param food_pos_list: Danh sách tọa độ (x, y) của thức ăn.
    :param map_data: Dữ liệu map (tường).
    :param snake_body: Danh sách tọa độ các bộ phận của rắn.
    :return: Danh sách các tọa độ tạo thành đường đi, hoặc None nếu không tìm thấy.
    """
    if not food_pos_list:
        return None

    # Hàng đợi ưu tiên chứa (chi phí, vị trí, đường đi)
    # Chi phí ở đây chính là g_score (quãng đường đã đi)
    cost = 0
    pq = [(cost, start_pos, [start_pos])]
    visited = {start_pos}
    

    while pq:
        current_cost, current_pos, path = heapq.heappop(pq)
        #  pq được sx từ bé đén lớn -> lấy ra thì luôn là phần tử có chi phí nhỏ nhất

        # Nếu vị trí hiện tại là một trong các mục tiêu, trả về đường đi
        if current_pos in food_pos_list:
            return {'path': path, 'visited': list(visited)}

        neighbors = get_valid_neighbors(current_pos, map_data, snake_body)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                new_cost = current_cost + 1 # Giả sử mỗi bước đi tốn 1 chi phí
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    return {'path': None, 'visited': list(visited)} # Không tìm thấy đường đi