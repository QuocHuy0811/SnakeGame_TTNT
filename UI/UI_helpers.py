"""
    CÁC BIẾN TRONG FOLDER UI
    CÁC HÀM DÙNG CHUNG
"""
import pygame
import config


pygame.init()

# --- Khởi tạo font dùng chung ---
BUTTON_FONT = pygame.font.Font(config.FONT_PATH, config.BUTTON_FONT_SIZE)

# --- Hàm xử lý Văn bản ---
def draw_text(text, font, color, surface, x, y):
    """
        Hàm tiện ích để vẽ văn bản căn giữa.
    """
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# --- Các hàm xử lý Nút bấm (Button) ---

def create_button(x, y, width, height, text):
    """
        Tạo ra một dictionary đại diện cho một nút bấm.
    """
    return {
        'rect': pygame.Rect(x, y, width, height),
        'text': text,
        'color': config.COLORS['btn'],
        'hover_color': config.COLORS['btn_hover'],
        'disabled_color': config.COLORS['btn_disabled'],
        'is_hovered': False,
        'is_enabled': True
    }

def draw_button(surface, button_data):
    """
        Vẽ một nút bấm (dạng dictionary) lên màn hình.
    """
    current_color = button_data['color']
    if not button_data['is_enabled']:
        current_color = button_data['disabled_color']
    elif button_data['is_hovered']:
        current_color = button_data['hover_color']

    pygame.draw.rect(surface, current_color, button_data['rect'], border_radius=10)
    draw_text(button_data['text'], BUTTON_FONT, config.COLORS['white'], surface, button_data['rect'].centerx, button_data['rect'].centery)

def handle_button_events(event, button_data):
    """
        Kiểm tra xem một nút có được click bởi một sự kiện không.
        Trả về True nếu nút được click.
        Trạng thái hover được cập nhật riêng.
    """
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and button_data['is_hovered'] and button_data['is_enabled']:
        return True
    return False

def update_button_hover_state(button_data, mouse_pos):
    """
        Cập nhật trạng thái hover cho một nút.
    """
    if button_data['is_enabled']:
        button_data['is_hovered'] = button_data['rect'].collidepoint(mouse_pos)
    else:
        button_data['is_hovered'] = False

def draw_game_grid(surface):
    """
    Vẽ một lưới ô vuông cho khu vực chơi game.
    """
    # Lấy kích thước từ file config
    game_width = config.MAP_WIDTH_TILES * config.TILE_SIZE
    game_height = config.MAP_HEIGHT_TILES * config.TILE_SIZE
    grid_color = config.COLORS['border'] # Dùng màu 'border' cho đường kẻ

    # Vẽ các đường kẻ dọc
    for x in range(0, game_width, config.TILE_SIZE):
        pygame.draw.line(surface, grid_color, (x, 0), (x, game_height))
    # Vẽ các đường kẻ ngang
    for y in range(0, game_height, config.TILE_SIZE):
        pygame.draw.line(surface, grid_color, (0, y), (game_width, y))
        
def draw_map(surface, map_data):
    """
    Vẽ các bức tường của map lên một bề mặt (surface).
    """
    wall_color = config.COLORS['border']
    
    for wall_pos in map_data['walls']:
        rect = pygame.Rect(
            wall_pos[0] * config.TILE_SIZE,
            wall_pos[1] * config.TILE_SIZE,
            config.TILE_SIZE,
            config.TILE_SIZE
        )
        pygame.draw.rect(surface, wall_color, rect)

def draw_search_visualization(surface, visited_nodes, path_nodes):
    """
    Vẽ các ô đã duyệt (màu trắng) và đường đi cuối cùng (màu đỏ).
    """
    # Vẽ các ô đã duyệt trước
    for pos in visited_nodes:
        center_x = pos[0] * config.TILE_SIZE + config.TILE_SIZE // 2
        center_y = pos[1] * config.TILE_SIZE + config.TILE_SIZE // 2
        pygame.draw.circle(surface, (200, 200, 200, 100), (center_x, center_y), 3) # Chấm trắng mờ

    # Vẽ đường đi cuối cùng đè lên trên
    for pos in path_nodes:
        center_x = pos[0] * config.TILE_SIZE + config.TILE_SIZE // 2
        center_y = pos[1] * config.TILE_SIZE + config.TILE_SIZE // 2
        pygame.draw.circle(surface, (255, 80, 80), (center_x, center_y), 4) # Chấm đỏ

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