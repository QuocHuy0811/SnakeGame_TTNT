import pygame
import random
import math
import config

# Biến toàn cục trong module này để lưu trữ trạng thái của tất cả các ngôi sao.
STARS = []
WIDTH, HEIGHT = 0, 0
CENTER_X, CENTER_Y = 0, 0

def init_background(width, height, num_stars):
    """
    Khởi tạo bầu trời sao. Hàm này chỉ cần gọi MỘT LẦN khi game bắt đầu.
    """
    global STARS, WIDTH, HEIGHT, CENTER_X, CENTER_Y
    
    WIDTH, HEIGHT = width, height
    CENTER_X, CENTER_Y = width // 2, height // 2
    
    STARS.clear()
    
    for _ in range(num_stars):
        star = {
            'angle': random.uniform(0, 2 * math.pi),
            'radius': random.uniform(1, WIDTH // 2),
            'speed': random.uniform(0.0005, 0.002),
            'drift': random.uniform(0.05, 0.15),
            'size': random.randint(1, 3),
            'color': (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
        }
        STARS.append(star)

def draw_background(screen):
    """
    Cập nhật vị trí VÀ vẽ bầu trời sao. Hàm này được gọi MỖI FRAME.
    """
    # 1. Vẽ một lớp nền màu tối trước, lấy từ file config.
    screen.fill(config.COLORS['bg'])
    
    # 2. Cập nhật và vẽ từng ngôi sao.
    for star in STARS:
        star['angle'] += star['speed']
        star['radius'] += star['drift']
        
        if star['radius'] > WIDTH // 2:
            star['radius'] = random.uniform(1, 10)
            star['angle'] = random.uniform(0, 2 * math.pi)

        x = CENTER_X + star['radius'] * math.cos(star['angle'])
        y = CENTER_Y + star['radius'] * math.sin(star['angle'])
        
        pygame.draw.circle(screen, star['color'], (int(x), int(y)), star['size'])