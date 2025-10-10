"""
    Hàm vẽ map
"""
import os

import pygame
import config

def load_map_data(map_filename):
    """
    Tải dữ liệu map từ file .txt.
    """
    # Khởi tạo cấu trúc dữ liệu cho map
    map_data = {
        'layout': [],
        'walls': [],
        'snake_start': [],
        'food_sequence': [],
        'food_mode': 'all_at_once' # Sẽ được đổi nếu tìm thấy thức ăn
    }
    
    full_path = f"Maps/{map_filename}"
    
    if not os.path.exists(full_path):
        print(f"Lỗi: Không tìm thấy file map '{full_path}'")
        return None

    # Biến tạm để lưu thức ăn theo thứ tự trước khi sắp xếp
    temp_sequential_food = []

    with open(full_path, 'r') as f:
        lines = f.readlines()
        if not lines:
            print(f"Lỗi: File map '{full_path}' bị trống.")
            return None

        for y, line in enumerate(lines):
            clean_line = line.strip()
            map_data['layout'].append(clean_line)
            for x, char in enumerate(clean_line):
                if char == '#':
                    map_data['walls'].append((x, y))
                elif char == 'x':
                    map_data['snake_start'].append((x, y))
                elif char.isdigit():
                    # Chỉ nhận diện các ký tự là số để làm thức ăn
                    order = int(char)
                    temp_sequential_food.append((order, (x, y)))
    
    # Sắp xếp lại vị trí của rắn để đảm bảo đúng thứ tự
    map_data['snake_start'].sort(key=lambda pos: (pos[1], pos[0]))

    # Nếu có bất kỳ thức ăn nào được tìm thấy, kích hoạt chế độ tuần tự
    if temp_sequential_food:
        map_data['food_mode'] = 'sequential'
        
        # Sắp xếp các viên thức ăn theo đúng thứ tự (1, 2, 3, ...)
        temp_sequential_food.sort(key=lambda item: item[0])
        
        # Lưu lại chuỗi tọa độ thức ăn đã sắp xếp
        map_data['food_sequence'] = [pos for order, pos in temp_sequential_food]

    return map_data

_wall_sprite = None

def load_wall_sprite():
    """Tải sprite tường 'wall.png' một lần duy nhất."""
    global _wall_sprite
    if _wall_sprite is not None:
        return _wall_sprite

    path = 'Assets/Images/Wall/wall.png'
    try:
        original_image = pygame.image.load(path).convert_alpha()
        _wall_sprite = pygame.transform.scale(original_image, (config.TILE_SIZE, config.TILE_SIZE))
        print(f"Tải sprite tường '{path}' thành công.")
    except pygame.error as e:
        print(f"LỖI: Không thể tải sprite tường '{path}'. Sẽ vẽ hình vuông thay thế. Lỗi: {e}")
        _wall_sprite = "error" # Đánh dấu lỗi
        
    return _wall_sprite

_map_bg_sprite = None

def load_map_background_sprite():
    """Tải sprite nền 'bg.png' một lần duy nhất."""
    global _map_bg_sprite
    if _map_bg_sprite is not None:
        return _map_bg_sprite

    path = 'Assets/Images/Wall/bg.png'
    try:
        original_image = pygame.image.load(path).convert() # Dùng .convert() cho ảnh không trong suốt
        _map_bg_sprite = pygame.transform.scale(original_image, (config.TILE_SIZE, config.TILE_SIZE))
        print(f"Tải sprite nền map '{path}' thành công.")
    except pygame.error as e:
        print(f"LỖI: Không thể tải sprite nền map '{path}'. Lỗi: {e}")
        _map_bg_sprite = "error"
        
    return _map_bg_sprite

