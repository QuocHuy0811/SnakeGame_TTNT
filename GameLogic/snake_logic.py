"""
    Quản lý vị trí đầu, thân, đuôi, 
"""
from Algorithms.algorithm_helpers import manhattan_distance
from UI import UI_helpers
import config
import pygame

# Biến global để lưu trữ các sprite của rắn, giúp tránh tải lại ảnh nhiều lần
_snake_sprites = None

def load_snake_sprites():
    """
        Tải các sprite gốc của rắn từ file. 
        Việc xoay sẽ được xử lý khi vẽ.
    """
    global _snake_sprites
    if _snake_sprites:
        # Nếu sprite đã được tải, trả về ngay lập tức
        return _snake_sprites

    sprites = {}
    path = 'Assets/Images/Snake/'

    try:
        # Tải các loại đầu rắn (gốc hướng LÊN)
        sprites['head_normal'] = pygame.image.load(f'{path}head_normal.png').convert_alpha()
        sprites['head_ready'] = pygame.image.load(f'{path}head_ready.png').convert_alpha()
        sprites['head_eat'] = pygame.image.load(f'{path}head_eat.png').convert_alpha()

        # Tải thân thẳng (gốc là DỌC)
        sprites['body_straight'] = pygame.image.load(f'{path}body_straight.png').convert_alpha()
        
        # Tải các thân cong (đã có đủ 4 hướng)
        sprites['bend_UP_LEFT'] = pygame.image.load(f'{path}body_bottom_right.png').convert_alpha()
        sprites['bend_UP_RIGHT'] = pygame.image.load(f'{path}body_bottom_left.png').convert_alpha()
        sprites['bend_DOWN_LEFT'] = pygame.image.load(f'{path}body_top_right.png').convert_alpha()
        sprites['bend_DOWN_RIGHT'] = pygame.image.load(f'{path}body_top_left.png').convert_alpha()
        
        # Tải đuôi (gốc hướng LÊN)
        sprites['tail'] = pygame.image.load(f'{path}tail.png').convert_alpha()

    except pygame.error as e:
        print(f"Lỗi khi tải sprite của rắn: {e}")
        return None

    # Thay đổi kích thước tất cả các sprite để vừa với một ô trong game
    size = (config.TILE_SIZE, config.TILE_SIZE)
    for key, sprite in sprites.items():
        sprites[key] = pygame.transform.scale(sprite, size)

    # Lưu vào biến global và trả về
    _snake_sprites = sprites
    return sprites

def create_snake_from_map(map_data):
    """
        Tạo dữ liệu rắn (tọa độ thân, hướng) từ dữ liệu map.
    """
    snake_body_coords = map_data.get('snake_start')

    # Nếu map không có rắn ('x'), tạo một con mặc định
    if not snake_body_coords:
        return {'body': [(5, 5), (4, 5), (3, 5)], 'direction': 'RIGHT'}

    # Dữ liệu snake_start từ map_logic đã được sắp xếp,
    # nên phần tử đầu tiên (index 0) là đầu rắn.
    # Ta chỉ cần đảo ngược lại để có thứ tự [đầu, thân, đuôi]
    snake_body = list(reversed(snake_body_coords))
    
    # Xác định hướng ban đầu dựa trên 2 đốt đầu tiên
    initial_direction = 'RIGHT' # Mặc định
    if len(snake_body) > 1:
        head = snake_body[0]
        neck = snake_body[1]
        if head[0] > neck[0]: initial_direction = 'RIGHT'
        elif head[0] < neck[0]: initial_direction = 'LEFT'
        elif head[1] > neck[1]: initial_direction = 'DOWN'
        elif head[1] < neck[1]: initial_direction = 'UP'

    return {
        'body': snake_body,
        'direction': initial_direction
    }
def get_next_head_position(snake_data):
    """
        Tính toán vị trí tiếp theo của đầu rắn dựa trên hướng hiện tại mà không di chuyển nó.
    """
    direction = snake_data['direction']
    current_head = snake_data['body'][0]
    x, y = current_head
    if direction == 'UP': y -= 1
    elif direction == 'DOWN': y += 1
    elif direction == 'LEFT': x -= 1
    elif direction == 'RIGHT': x += 1
    return (x, y)

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
