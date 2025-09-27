"""
    Quản lý vị trí đầu, thân, đuôi, 
"""
from Algorithms.algorithm_helpers import manhattan_distance
from UI import UI_helpers
import config
import pygame
_snake_sprites = None

def load_snake_sprites():
    """
    Tải các sprite gốc của rắn từ file. Việc xoay sẽ được xử lý khi vẽ.
    """
    global _snake_sprites
    if _snake_sprites:
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

    # Thay đổi kích thước tất cả các sprite để khớp với TILE_SIZE
    size = (config.TILE_SIZE, config.TILE_SIZE)
    for key, sprite in sprites.items():
        sprites[key] = pygame.transform.scale(sprite, size)

    _snake_sprites = sprites
    return sprites


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