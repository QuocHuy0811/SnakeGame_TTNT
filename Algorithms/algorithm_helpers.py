"""
    CÁC HÀM DÙNG CHUNG TRONG FOLDER ALGORITHMS: Hàm tìm vị trí xung quanh (neighbors), Hàm tính khoảng các mahatan 
"""
import math

def get_valid_neighbors(position, map_data, snake_body):
    """
    Tìm tất cả các ô hàng xóm hợp lệ từ một vị trí cho trước.
    Ô hợp lệ là ô nằm trong bản đồ, không phải tường và không phải thân rắn.
    """
    neighbors = []
    x, y = position
    # Các hướng di chuyển có thể: (dx, dy) -> Lên, Xuống, Trái, Phải
    possible_moves = [ (0, -1), (0, 1), (-1, 0), (1, 0) ]

    # Lấy kích thước map động
    map_height = len(map_data['layout'])
    map_width = len(map_data['layout'][0]) if map_height > 0 else 0

    for dx, dy in possible_moves:
        nx, ny = x + dx, y + dy

        # Kiểm tra xem có nằm trong ranh giới bản đồ không
        if 0 <= nx < map_width and 0 <= ny < map_height:
            neighbor_pos = (nx, ny)
            if neighbor_pos not in map_data['walls'] and neighbor_pos not in snake_body:
                neighbors.append(neighbor_pos)

    return neighbors
def manhattan_distance(pos1, pos2):
    """
        Tính khoảng cách Manhattan giữa hai điểm.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
def euclidean_distance(pos1, pos2):
    """
        Tính khoảng cách Euclid (đường chim bay) giữa hai điểm.
    """
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx**2 + dy**2)