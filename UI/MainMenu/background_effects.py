import pygame
import random
import math
import config

# --- Class cho mỗi hạt (Particle) ---
class Particle:
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        # Vận tốc ngẫu nhiên cho mỗi hạt
        self.vx = random.uniform(-config.PARTICLE_MAX_VELOCITY, config.PARTICLE_MAX_VELOCITY)
        self.vy = random.uniform(-config.PARTICLE_MAX_VELOCITY, config.PARTICLE_MAX_VELOCITY)
        self.radius = config.PARTICLE_RADIUS
        self.color = config.COLORS['particle_color']
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self):
        # Cập nhật vị trí
        self.x += self.vx
        self.y += self.vy

        # Xử lý khi hạt chạm biên màn hình: bật lại
        if self.x <= 0 or self.x >= self.screen_width:
            self.vx *= -1
            self.x = max(0, min(self.x, self.screen_width)) # Đảm bảo hạt không ra ngoài biên
        if self.y <= 0 or self.y >= self.screen_height:
            self.vy *= -1
            self.y = max(0, min(self.y, self.screen_height))

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# --- Khởi tạo danh sách các hạt ---
particles = []
# Biến để đảm bảo chỉ khởi tạo một lần
_initialized = False

def init_background(screen_width, screen_height):
    """
    Khởi tạo các hạt. Chỉ gọi một lần.
    """
    global particles, _initialized
    if not _initialized:
        particles.clear()
        for _ in range(config.PARTICLE_COUNT):
            particles.append(Particle(screen_width, screen_height))
        _initialized = True

def draw_background(screen):
    """
    Vẽ nền, cập nhật và vẽ các hạt, sau đó vẽ đường nối.
    """
    # 1. Vẽ nền
    screen.fill(config.COLORS['bg_dark_blue'])

    # 2. Cập nhật và vẽ các hạt
    for p in particles:
        p.update()
        p.draw(screen)

    # 3. Vẽ đường nối giữa các hạt đủ gần
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            p1 = particles[i]
            p2 = particles[j]

            # Tính khoảng cách giữa hai hạt
            distance = math.hypot(p1.x - p2.x, p1.y - p2.y)

            if distance < config.CONNECT_DISTANCE:
                # Tính độ trong suốt của đường dựa trên khoảng cách
                # Càng gần thì càng rõ, càng xa thì càng mờ
                alpha = int(255 * (1 - (distance / config.CONNECT_DISTANCE)))
                
                # Vẽ đường nối với độ trong suốt
                # Chú ý: pygame.draw.aaline hỗ trợ alpha tốt hơn trên một số hệ thống
                # và cho đường kẻ mượt hơn.
                # Cần truyền màu có 4 thành phần (R, G, B, Alpha).
                line_color_with_alpha = config.COLORS['line_color'] + (alpha,)
                pygame.draw.line(screen, line_color_with_alpha, (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y)), 1)