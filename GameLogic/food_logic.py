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

def draw_food(surface, food_list):
    """Vẽ tất cả thức ăn trong danh sách lên một bề mặt."""
    food_color = (255, 196, 0) # Có thể lấy từ config.COLORS
    for food in food_list:
        rect = pygame.Rect(
            food['pos'][0] * config.TILE_SIZE,
            food['pos'][1] * config.TILE_SIZE,
            config.TILE_SIZE,
            config.TILE_SIZE
        )
        pygame.draw.rect(surface, food_color, rect)