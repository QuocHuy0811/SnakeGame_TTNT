"""
    CÁC HÀM DÙNG CHUNG TRONG FOLDER ALGORITHMS: Hàm tìm vị trí xung quanh (neighbors), Hàm tính khoảng các mahatan 
"""
# Algorithms/algorithm_helpers.py
import config

def get_valid_neighbors(position, map_data, snake_body):
    """
    Tìm tất cả các ô hàng xóm hợp lệ từ một vị trí cho trước.
    Ô hợp lệ là ô nằm trong bản đồ, không phải tường và không phải thân rắn.
    """
    neighbors = []
    x, y = position
    # Các hướng di chuyển có thể: (dx, dy) -> Lên, Xuống, Trái, Phải
    possible_moves = [ (0, -1), (0, 1), (-1, 0), (1, 0) ]

    for dx, dy in possible_moves:
        nx, ny = x + dx, y + dy

        # Kiểm tra xem có nằm trong ranh giới bản đồ không
        if 0 <= nx < config.AI_MAP_WIDTH_TILES and 0 <= ny < config.AI_MAP_HEIGHT_TILES:
            neighbor_pos = (nx, ny)
            # Kiểm tra xem có phải là tường hoặc thân rắn không
            if neighbor_pos not in map_data['walls'] and neighbor_pos not in snake_body:
                neighbors.append(neighbor_pos)

    return neighbors
def manhattan_distance(pos1, pos2):
    """Tính khoảng cách Manhattan giữa hai điểm."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])