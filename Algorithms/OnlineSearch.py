from functools import partial
from Algorithms import Astar
from Algorithms.algorithm_helpers import manhattan_distance
def _get_safe_neighbor_moves(head, snake_body, walls):
    """
        Tìm các hướng đi an toàn (không đi lùi, không va chạm tường, không va chạm thân).
        Đây là hàm trợ giúp quan trọng.
    """
    moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    
    # Logic chống đi lùi (đã được xác nhận là chính xác)
    if len(snake_body) > 1:
        neck = snake_body[1]
        if head[1] - 1 == neck[1]: moves.remove('UP')
        if head[1] + 1 == neck[1]: moves.remove('DOWN')
        if head[0] - 1 == neck[0]: moves.remove('LEFT')
        if head[0] + 1 == neck[0]: moves.remove('RIGHT')
            
    safe_moves = []
    for move in moves:
        new_head = None
        if move == 'UP': new_head = (head[0], head[1] - 1)
        elif move == 'DOWN': new_head = (head[0], head[1] + 1)
        elif move == 'LEFT': new_head = (head[0] - 1, head[1])
        elif move == 'RIGHT': new_head = (head[0] + 1, head[1])
        
        # Kiểm tra va chạm tường và thân
        if new_head and new_head not in walls and new_head not in snake_body:
            safe_moves.append(move)
            
    return safe_moves

def find_best_next_move(snake_data, food_data, map_data):
    """
        Hàm quyết định nước đi tốt nhất tiếp theo bằng cách "nhìn trước" (lookahead) sử dụng A*.
        Nó sẽ thử mỗi nước đi an toàn và chọn nước đi nào mở ra con đường A* ngắn nhất đến thức ăn.
    """
    snake_body = snake_data.get('body')
    if not snake_body:
        return {
            'move': None, 
            'path': None, 
            'visited_nodes': [], 
            'visited_count': 0, 
            'generated_count': 0
        }
    
    head = snake_body[0]
    
    safe_moves = _get_safe_neighbor_moves(head, snake_body, map_data.get('walls', []))
    
    if not safe_moves:
        return {
            'move': None, 
            'path': None, 
            'visited_nodes': [], 
            'visited_count': 0, 
            'generated_count': 0
        }

    food_positions = [food['pos'] for food in food_data]
    if not food_positions:
        return {
                'move': safe_moves[0], 
                'path': None, 
                'visited_nodes': [], 
                'visited_count': 0, 
                'generated_count': 0
            }

    move_options = []
    total_visited_nodes_set = set()
    total_visited_count = 0
    total_generated_count = 0

    astar = partial(Astar.find_path_astar, heuristic_func=manhattan_distance)
    for move in safe_moves:
        new_head = None
        if move == 'UP': new_head = (head[0], head[1] - 1)
        elif move == 'DOWN': new_head = (head[0], head[1] + 1)
        elif move == 'LEFT': new_head = (head[0] - 1, head[1])
        elif move == 'RIGHT': new_head = (head[0] + 1, head[1])

        result = astar(new_head, food_positions, map_data, snake_body)
        path = result.get('path')
        total_visited_nodes_set.update(result.get('visited_nodes', set()))
        total_visited_count += result.get('visited_count', 0)
        total_generated_count += result.get('generated_count', 0)

        if path:
            path_length = len(path)
            move_options.append({'move': move, 'length': path_length, 'path': path})
        else:
            move_options.append({'move': move, 'length': float('inf'), 'path': None})

    best_option = min(move_options, key=lambda x: x['length'])
    
    if best_option['length'] == float('inf'):
        # 1. Tìm thức ăn gần nhất
        target_pos = min(food_positions, key=lambda food: manhattan_distance(head, food))

        survival_options = []
        # 2. "Thử" từng nước đi an toàn
        for move in safe_moves:
            new_head = None
            if move == 'UP': new_head = (head[0], head[1] - 1)
            elif move == 'DOWN': new_head = (head[0], head[1] + 1)
            elif move == 'LEFT': new_head = (head[0] - 1, head[1])
            elif move == 'RIGHT': new_head = (head[0] + 1, head[1])

            # 3. Tính khoảng cách từ vị trí mới đến mục tiêu
            dist_to_food = manhattan_distance(new_head, target_pos)
            survival_options.append({'move': move, 'dist': dist_to_food})

        # 4. Chọn nước đi có khoảng cách Manhattan nhỏ nhất
        best_survival_move = min(survival_options, key=lambda x: x['dist'])
        return {
            'move': best_survival_move['move'],
            'path': None,
            'visited_nodes': list(total_visited_nodes_set),
            'visited_count': total_visited_count,
            'generated_count': total_generated_count
        }
        
    return {
        'move': best_option['move'],
        'path': best_option['path'],
        'visited_nodes': list(total_visited_nodes_set),
        'visited_count': total_visited_count,
        'generated_count': total_generated_count
    }