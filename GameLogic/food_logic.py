"""
    Quản lý vị trí thức ăn, tạo vị trí mới, vẽ thức ăn
"""
import config
import pygame

def create_food_from_map(map_data):
    """
    Tạo ra một danh sách các dictionary thức ăn dựa trên thông tin từ map_data.
    Hàm này sẽ tải TẤT CẢ các vị trí có dấu '*' trong file map.
    """
    if not map_data['food_start']:
        # Nếu map không có thức ăn, tạo một viên mặc định để tránh lỗi
        return [{'pos': (15, 15)}]
        
    # Chuyển đổi danh sách tọa độ thành danh sách các đối tượng thức ăn
    return [{'pos': pos} for pos in map_data['food_start']]

def draw_food(surface, food_data, blinking_info=None):
    """
    Vẽ tất cả thức ăn lên màn hình.
    :param blinking_info: Một tuple (vị trí, is_visible) để vẽ hiệu ứng nhấp nháy.
    """
    blinking_pos = None
    is_blink_visible = False
    if blinking_info:
        blinking_pos, is_blink_visible = blinking_info

    for food in food_data:
        pos = food['pos']
        rect = pygame.Rect(
            pos[0] * config.TILE_SIZE,
            pos[1] * config.TILE_SIZE,
            config.TILE_SIZE,
            config.TILE_SIZE
        )
        
        # Luôn vẽ viên thức ăn
        pygame.draw.rect(surface, config.COLORS['food'], rect)
        
        # Nếu đây là thức ăn đích và đang trong chu kỳ "sáng", vẽ vòng tròn highlight
        if pos == blinking_pos and is_blink_visible:
            pygame.draw.circle(surface, config.COLORS['highlight'], rect.center, config.TILE_SIZE // 2 + 3, 3)