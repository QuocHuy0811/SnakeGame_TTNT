from Algorithms import Astar

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
        return None
    
    head = snake_body[0]
    
    # 1. Lấy tất cả các hướng đi an toàn từ vị trí hiện tại
    safe_moves = _get_safe_neighbor_moves(head, snake_body, map_data.get('walls', []))
    
    if not safe_moves:
        return None # Bị kẹt hoàn toàn, không có nước đi an toàn nào

    food_positions = [food['pos'] for food in food_data]
    if not food_positions:
        # Nếu không còn thức ăn, chỉ cần đi một nước an toàn bất kỳ để không đứng yên
        return safe_moves[0] 

    move_options = []

    # 2. Với mỗi nước đi an toàn, chạy A* để đánh giá "chất lượng" của nó
    for move in safe_moves:
        # Tính toán vị trí đầu rắn mới nếu đi theo hướng 'move'
        new_head = None
        if move == 'UP': new_head = (head[0], head[1] - 1)
        elif move == 'DOWN': new_head = (head[0], head[1] + 1)
        elif move == 'LEFT': new_head = (head[0] - 1, head[1])
        elif move == 'RIGHT': new_head = (head[0] + 1, head[1])

        # Chạy A* từ vị trí giả định mới này để xem có tìm được đường đến thức ăn không
        # Thân rắn hiện tại được dùng làm vật cản cho A*
        result = Astar.find_path_astar(new_head, food_positions, map_data, snake_body)
        path = result.get('path')

        if path:
            # Nếu tìm thấy đường, "chất lượng" của nước đi là độ dài của con đường đó
            path_length = len(path)
            move_options.append({'move': move, 'length': path_length})
        else:
            # Nếu không tìm thấy đường, nước đi này dẫn vào ngõ cụt, chất lượng rất tệ
            move_options.append({'move': move, 'length': float('inf')})

    # 3. Chọn ra nước đi có "chất lượng" tốt nhất (độ dài path ngắn nhất)
    if not move_options:
        # Trường hợp hiếm: có safe_moves nhưng không có lựa chọn nào (vô lý nhưng để phòng vệ)
        return safe_moves[0] if safe_moves else None

    best_option = min(move_options, key=lambda x: x['length'])
    
    # Nếu tất cả các lựa chọn đều dẫn vào ngõ cụt (độ dài là vô cực)
    if best_option['length'] == float('inf'):
        # Đây là chế độ sinh tồn: AI không thể đến thức ăn, nhưng vẫn có thể di chuyển
        # Nó sẽ chọn một nước đi an toàn bất kỳ để không đứng yên và hy vọng tình thế thay đổi.
        return safe_moves[0]
        
    # Trả về nước đi tốt nhất đã được tính toán
    return best_option['move']