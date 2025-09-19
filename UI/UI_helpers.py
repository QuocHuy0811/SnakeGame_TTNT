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
        'is_hovered': False
    }

def draw_button(surface, button_data):
    """
        Vẽ một nút bấm (dạng dictionary) lên màn hình.
    """
    current_color = button_data['hover_color'] if button_data['is_hovered'] else button_data['color']
    pygame.draw.rect(surface, current_color, button_data['rect'], border_radius=10)
    draw_text(button_data['text'], BUTTON_FONT, config.COLORS['white'], surface, button_data['rect'].centerx, button_data['rect'].centery)

def handle_button_events(event, button_data):
    """
        Kiểm tra xem một nút có được click bởi một sự kiện không.
        Trả về True nếu nút được click.
        Trạng thái hover được cập nhật riêng.
    """
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and button_data['is_hovered']:
        return True
    return False

def update_button_hover_state(button_data, mouse_pos):
    """
        Cập nhật trạng thái hover cho một nút.
    """
    button_data['is_hovered'] = button_data['rect'].collidepoint(mouse_pos)

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