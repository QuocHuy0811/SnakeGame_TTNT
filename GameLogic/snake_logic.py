"""
    Quản lý vị trí đầu, thân, đuôi, 
"""
from Algorithms.algorithm_helpers import manhattan_distance
from UI import UI_helpers
import config
import pygame

def create_snake_from_map(map_data):
    """
    Tạo ra một dictionary chứa dữ liệu của con rắn dựa trên thông tin từ map_data.
    """
    if not map_data['snake_start']:
        # Nếu map không có rắn, tạo một con mặc định
        # Đảo ngược thứ tự để phần tử đầu tiên (index 0) là ĐẦU RẮN
        return {'body': [(5, 5), (4, 5), (3, 5)], 'direction': 'RIGHT'}

    snake_body = map_data['snake_start'][:]
    # Sắp xếp để đảm bảo tọa độ x nhỏ nhất là đuôi
    snake_body.sort() 
    # Đảo ngược lại để phần tử đầu tiên là ĐẦU RẮN
    snake_body.reverse() 
    
    # Giả định hướng di chuyển ban đầu là 'RIGHT'
    initial_direction = 'RIGHT'
    
    return {
        'body': snake_body,
        'direction': initial_direction
    }

# Hàm mới: Di chuyển con rắn

# Mở file: snake_logic.py

def move_snake(snake_data, grow=False):
    """
    Di chuyển con rắn. Nếu grow=True, rắn sẽ không bị cắt đuôi và dài ra.
    """
    body = snake_data['body']
    direction = snake_data['direction']
    
    # Kiểm tra xem rắn có thân không để tránh lỗi
    if not body:
        return
        
    current_head = body[0]
    
    x, y = current_head
    if direction == 'UP': y -= 1
    elif direction == 'DOWN': y += 1
    elif direction == 'LEFT': x -= 1
    elif direction == 'RIGHT': x += 1
    new_head = (x, y)
    
    body.insert(0, new_head)
    
    # Chỉ cắt đuôi nếu không trong trạng thái phát triển
    if not grow:
        body.pop()


def draw_snake(surface, snake_data, food_data):
    """
    Vẽ con rắn bằng sprite, với logic xoay hình chính xác.
    """
    snake_body = snake_data.get('body')
    snake_direction = snake_data.get('direction')
    
    sprites = UI_helpers.load_snake_sprites()
    if not sprites or not snake_body: return

    tile_size = config.TILE_SIZE
    head_pos = snake_body[0]

    # --- CHỌN ĐÚNG LOẠI ĐẦU RẮN ---
    min_dist = float('inf')
    if food_data:
        food_positions = [food['pos'] for food in food_data]
        min_dist = min(manhattan_distance(head_pos, food_pos) for food_pos in food_positions)
    
    head_type = 'head_normal'
    if min_dist == 1: head_type = 'head_eat'
    elif 1 < min_dist <= 3: head_type = 'head_ready'
    
    # Lấy sprite đầu gốc (hướng LÊN)
    original_head_sprite = sprites.get(head_type)
    
    # --- VẼ CÁC BỘ PHẬN ---
    for i, segment in enumerate(snake_body):
        rect = pygame.Rect(segment[0] * tile_size, segment[1] * tile_size, tile_size, tile_size)

        if i == 0:  # Đầu rắn
            if original_head_sprite:
                # Xoay sprite đầu từ hướng LÊN sang hướng di chuyển
                angle = 0
                if snake_direction == 'DOWN': angle = 180
                elif snake_direction == 'LEFT': angle = 90
                elif snake_direction == 'RIGHT': angle = -90
                head_sprite_rotated = pygame.transform.rotate(original_head_sprite, angle)
                surface.blit(head_sprite_rotated, rect)
        
        elif i == len(snake_body) - 1:  # Đuôi rắn
            prev_segment = snake_body[i-1]
            tail_direction = 'UP'
            if segment[1] > prev_segment[1]: tail_direction = 'UP'
            elif segment[1] < prev_segment[1]: tail_direction = 'DOWN'
            elif segment[0] > prev_segment[0]: tail_direction = 'LEFT'
            elif segment[0] < prev_segment[0]: tail_direction = 'RIGHT'
            
            # Lấy sprite đuôi gốc (hướng LÊN) và xoay
            original_tail_sprite = sprites['tail']
            angle = 0
            if tail_direction == 'DOWN': angle = 180
            elif tail_direction == 'LEFT': angle = 90
            elif tail_direction == 'RIGHT': angle = -90
            tail_sprite_rotated = pygame.transform.rotate(original_tail_sprite, angle)
            surface.blit(tail_sprite_rotated, rect)
        
        else:  # Thân rắn
            prev_segment, next_segment = snake_body[i-1], snake_body[i+1]
            if prev_segment[0] == next_segment[0]: # Thân dọc
                surface.blit(sprites['body_straight'], rect)
            elif prev_segment[1] == next_segment[1]: # Thân ngang
                # Xoay sprite thân thẳng từ DỌC sang NGANG
                body_horizontal = pygame.transform.rotate(sprites['body_straight'], 90)
                surface.blit(body_horizontal, rect)
            else: # Thân cong
                prev_vec = (prev_segment[0] - segment[0], prev_segment[1] - segment[1])
                next_vec = (next_segment[0] - segment[0], next_segment[1] - segment[1])
                
                key = None
                if (prev_vec in [(0, 1), (-1, 0)]) and (next_vec in [(0, 1), (-1, 0)]): key = 'bend_DOWN_LEFT'
                elif (prev_vec in [(0, 1), (1, 0)]) and (next_vec in [(0, 1), (1, 0)]): key = 'bend_DOWN_RIGHT'
                elif (prev_vec in [(0, -1), (-1, 0)]) and (next_vec in [(0, -1), (-1, 0)]): key = 'bend_UP_LEFT'
                elif (prev_vec in [(0, -1), (1, 0)]) and (next_vec in [(0, -1), (1, 0)]): key = 'bend_UP_RIGHT'
                
                if key: surface.blit(sprites[key], rect)
# hàm kiểm tra va chạm của người chơi
def check_collision(snake_data, map_data):
    """
    Kiểm tra xem đầu rắn có va chạm với tường, ranh giới map, hoặc chính nó không.
    Trả về True nếu có va chạm, ngược lại trả về False.
    """
    head = snake_data['body'][0]
    body_without_head = snake_data['body'][1:]

    # 1. Kiểm tra va chạm với tường từ map_data
    if head in map_data['walls']:
        return True

    # 2. Kiểm tra va chạm với ranh giới map (dành cho map không có tường bao)
    head_x, head_y = head
    if not (0 <= head_x < config.DUAL_MAP_WIDTH_TILES and 0 <= head_y < config.DUAL_MAP_HEIGHT_TILES):
        return True
        
    # 3. Kiểm tra va chạm với chính thân nó
    if head in body_without_head:
        return True

    return False
def get_next_head_position(snake_data):
    """
    Tính toán và trả về vị trí tiếp theo của đầu rắn mà không di chuyển nó.
    """
    direction = snake_data['direction']
    current_head = snake_data['body'][0]
    x, y = current_head
    if direction == 'UP': y -= 1
    elif direction == 'DOWN': y += 1
    elif direction == 'LEFT': x -= 1
    elif direction == 'RIGHT': x += 1
    return (x, y)