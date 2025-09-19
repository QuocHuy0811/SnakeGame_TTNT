"""
    Quản lý vị trí đầu, thân, đuôi, 
"""
import config
import pygame
def create_snake_from_map(map_data):
    """
    Tạo ra một dictionary chứa dữ liệu của con rắn dựa trên thông tin từ map_data.
    """
    if not map_data['snake_start']:
        # Nếu map không có rắn, tạo một con mặc định
        return {'body': [(5, 5), (4, 5), (3, 5)], 'direction': 'RIGHT'}

    # Lấy phần thân rắn từ map data
    snake_body = map_data['snake_start']
    
    # Giả định hướng di chuyển ban đầu là 'RIGHT'
    # (Có thể nâng cấp để tự suy ra hướng dựa trên vị trí đầu và thân)
    initial_direction = 'RIGHT'
    
    return {
        'body': snake_body,
        'direction': initial_direction
    }

def draw_snake(surface, snake_data):
    """Vẽ con rắn lên một bề mặt (surface) được chỉ định."""
    for part in snake_data['body']:
        rect = pygame.Rect(
            part[0] * config.TILE_SIZE,
            part[1] * config.TILE_SIZE,
            config.TILE_SIZE,
            config.TILE_SIZE
        )
        # Vẽ đầu rắn màu khác để phân biệt
        if part == snake_data['body'][-1]: # Giả sử đầu rắn là phần tử cuối
             pygame.draw.rect(surface, config.COLORS['highlight'], rect)
        else:
             pygame.draw.rect(surface, config.COLORS['combo'], rect)