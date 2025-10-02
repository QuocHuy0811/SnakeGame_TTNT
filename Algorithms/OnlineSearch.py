# Algorithms/LRTAstar.py
import copy

# ======================================================================
# --- BỘ NHỚ CỦA AI ---
# ======================================================================
# heuristic_table sẽ lưu trữ kiến thức mà AI đã học.
# Dạng: {trạng_thái: chi_phí_ước_tính}
heuristic_table = {}

def reset_lrta_memory():
    """Xóa toàn bộ bộ nhớ đã học của AI."""
    global heuristic_table
    heuristic_table.clear()

# ======================================================================
# --- CÁC HÀM TRỢ GIÚP ---
# ======================================================================

def _get_state_representation(snake_body):
    """
    Tạo ra một 'key' định danh cho trạng thái hiện tại của con rắn.
    Dùng tuple để có thể làm key cho dictionary.
    """
    return tuple(snake_body)

def _get_initial_heuristic(head, food_data):
    """
    Ước tính heuristic ban đầu khi gặp một trạng thái chưa từng thấy.
    Sử dụng khoảng cách Manhattan đến miếng mồi gần nhất.
    """
    if not food_data:
        return float('inf') # Nếu không có mồi, chi phí là vô cực
    
    return min(abs(head[0] - f['pos'][0]) + abs(head[1] - f['pos'][1]) for f in food_data)

def _get_safe_neighbor_moves(head, snake_body, walls):
    """Tìm các hướng đi an toàn (không đi lùi, không va chạm)."""
    moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    if len(snake_body) > 1:
        neck = snake_body[-2]
        if head[1] - 1 == neck[1] and 'UP' in moves: moves.remove('UP')
        if head[1] + 1 == neck[1] and 'DOWN' in moves: moves.remove('DOWN')
        if head[0] - 1 == neck[0] and 'LEFT' in moves: moves.remove('LEFT')
        if head[0] + 1 == neck[0] and 'RIGHT' in moves: moves.remove('RIGHT')
        
    safe_moves = []
    for move in moves:
        new_head = None
        if move == 'UP': new_head = (head[0], head[1] - 1)
        elif move == 'DOWN': new_head = (head[0], head[1] + 1)
        elif move == 'LEFT': new_head = (head[0] - 1, head[1])
        elif move == 'RIGHT': new_head = (head[0] + 1, head[1])
        
        if new_head and new_head not in walls and new_head not in snake_body:
            safe_moves.append(move)
            
    return safe_moves

# ======================================================================
# --- HÀM CHÍNH CỦA LRTA* ---
# ======================================================================
def find_best_next_move(snake_data, food_data, map_data):
    """
    Hàm quyết định nước đi tiếp theo sử dụng thuật toán LRTA*.
    """
    global heuristic_table
    snake_body = snake_data['body']
    if not snake_body: return None
    head = snake_body[-1]

    # 1. QUAN SÁT: Xác định trạng thái hiện tại
    current_state_key = _get_state_representation(snake_body)
    
    # 2. TÍNH TOÁN: Xem xét các nước đi tiếp theo
    safe_moves = _get_safe_neighbor_moves(head, snake_body, map_data['walls'])
    
    if not safe_moves:
        # Nếu bị kẹt, học rằng trạng thái này rất tệ (chi phí vô cực)
        heuristic_table[current_state_key] = float('inf')
        return None

    costs = []
    for move in safe_moves:
        # Tạo trạng thái giả lập của neighbor
        new_head = None
        if move == 'UP': new_head = (head[0], head[1] - 1)
        elif move == 'DOWN': new_head = (head[0], head[1] + 1)
        elif move == 'LEFT': new_head = (head[0] - 1, head[1])
        elif move == 'RIGHT': new_head = (head[0] + 1, head[1])
        
        neighbor_snake_body = snake_body[1:] + [new_head]
        neighbor_state_key = _get_state_representation(neighbor_snake_body)
        
        # Lấy heuristic đã học của neighbor từ "bộ nhớ"
        # Nếu chưa gặp, tính heuristic ban đầu
        h_neighbor = heuristic_table.get(neighbor_state_key)
        if h_neighbor is None:
            h_neighbor = _get_initial_heuristic(new_head, food_data)
            heuristic_table[neighbor_state_key] = h_neighbor

        # Chi phí dự kiến = chi phí di chuyển (1) + heuristic của neighbor
        cost = 1 + h_neighbor
        costs.append((cost, move))
    
    # Tìm ra nước đi có chi phí dự kiến thấp nhất
    min_cost, best_move = min(costs)

    # 3. HỌC HỎI: Cập nhật "bộ nhớ" về trạng thái hiện tại
    heuristic_table[current_state_key] = min_cost
    
    # 4. HÀNH ĐỘNG: Trả về nước đi tốt nhất
    return best_move