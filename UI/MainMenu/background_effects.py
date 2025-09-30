import math
import random
import pygame


_stars = []
_shooting_stars = []
_width, _height = 0, 0
_last_shooting_star_spawn = 0

def init_background(screen_width, screen_height, num_stars):
    """Khởi tạo nền sao tĩnh."""
    global _stars, _width, _height, _shooting_stars
    _width, _height = screen_width, screen_height
    _stars = []
    _shooting_stars = [] # Reset sao băng khi khởi tạo

    for _ in range(num_stars):
        _stars.append({
            'pos': (random.randint(0, _width), random.randint(0, _height)),
            'size': random.randint(1, 2),
            'color': (random.randint(150, 200), random.randint(150, 200), random.randint(150, 200))
        })

def _spawn_shooting_star():
    """Tạo một sao băng mới với các thuộc tính ngẫu nhiên."""
    length = random.randint(150, 300) # Chiều dài vệt sáng
    speed = random.uniform(8, 15)     # Tốc độ bay

    # Sao băng bay từ góc trên bên trái hoặc trên bên phải
    if random.random() < 0.5: # Bay từ trái sang phải
        x = -length
        y = random.randint(0, _height // 2)
        angle = math.radians(random.uniform(10, 30)) # Góc bay chéo xuống
    else: # Bay từ phải sang trái
        x = _width + length
        y = random.randint(0, _height // 2)
        angle = math.radians(random.uniform(150, 170)) # Góc bay chéo xuống

    _shooting_stars.append({
        'x': x,
        'y': y,
        'vx': math.cos(angle) * speed,
        'vy': math.sin(angle) * speed,
        'length': length,
        'color': (220, 220, 255) # Màu trắng xanh cho vệt sáng
    })

def draw_background(surface):
    """Vẽ nền đen, sao tĩnh và các sao băng chuyển động."""
    global _last_shooting_star_spawn
    current_time = pygame.time.get_ticks()

    # 1. Tô nền đen
    surface.fill((10, 10, 25)) # Màu đen hơi xanh thẫm

    # 2. Vẽ các ngôi sao tĩnh
    for star in _stars:
        pygame.draw.circle(surface, star['color'], star['pos'], star['size'])

    # 3. Tạo sao băng mới theo chu kỳ
    # Mỗi 2-5 giây sẽ có một sao băng mới, giới hạn 100 sao băng cùng lúc
    if current_time - _last_shooting_star_spawn > random.randint(200, 500):
        if len(_shooting_stars) < 100:
            _spawn_shooting_star()
        _last_shooting_star_spawn = current_time

    # 4. Cập nhật và vẽ sao băng
    shooting_stars_to_remove = []
    for i, s_star in enumerate(_shooting_stars):
        # Cập nhật vị trí đầu của sao băng
        s_star['x'] += s_star['vx']
        s_star['y'] += s_star['vy']

        # Tính toán vị trí đuôi của sao băng
        end_x = s_star['x'] - s_star['vx'] * (s_star['length'] / 15) # Điều chỉnh độ dài vệt
        end_y = s_star['y'] - s_star['vy'] * (s_star['length'] / 15)

        # Vẽ vệt sáng bằng một đường thẳng (dùng aaline để có hiệu ứng mượt hơn)
        pygame.draw.aaline(surface, s_star['color'], (s_star['x'], s_star['y']), (end_x, end_y))
        pygame.draw.circle(surface, s_star['color'], (int(s_star['x']), int(s_star['y'])), 3)

        # Đánh dấu để xóa sao băng nếu nó đã bay ra khỏi màn hình
        if s_star['x'] < -s_star['length'] or s_star['x'] > _width + s_star['length']:
            shooting_stars_to_remove.append(i)
    
    # Xóa các sao băng đã bay hết
    for i in reversed(shooting_stars_to_remove):
        _shooting_stars.pop(i)

