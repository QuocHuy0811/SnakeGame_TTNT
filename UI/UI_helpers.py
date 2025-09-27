"""
    CÁC BIẾN TRONG FOLDER UI
    CÁC HÀM DÙNG CHUNG
"""
import pygame
import config
from GameLogic import snake_logic, food_logic
from Algorithms.algorithm_helpers import manhattan_distance


pygame.init()

_snake_sprites = None
_food_sprite = None

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

def draw_snake(surface, snake_data, food_data):
    """
    Vẽ con rắn bằng sprite, với logic xoay hình chính xác.
    """
    snake_body = snake_data.get('body')
    snake_direction = snake_data.get('direction')
    
    sprites = snake_logic.load_snake_sprites()
    if not sprites or not snake_body: return

    tile_size = config.TILE_SIZE
    head_pos = snake_body[0]

    # --- CHỌN ĐÚNG LOẠI ĐẦU RẮN ---
    min_dist = float('inf')
    if food_data:
        food_positions = [food['pos'] for food in food_data]
        min_dist = min(manhattan_distance(head_pos, food_pos) for food_pos in food_positions)
    
    head_type = 'head_normal'
    if min_dist == 1: head_type = 'head_eat'
    elif 1 < min_dist <= 3: head_type = 'head_ready'
    
    # Lấy sprite đầu gốc (hướng LÊN)
    original_head_sprite = sprites.get(head_type)
    
    # --- VẼ CÁC BỘ PHẬN ---
    for i, segment in enumerate(snake_body):
        rect = pygame.Rect(segment[0] * tile_size, segment[1] * tile_size, tile_size, tile_size)

        if i == 0:  # Đầu rắn
            if original_head_sprite:
                # Xoay sprite đầu từ hướng LÊN sang hướng di chuyển
                angle = 0
                if snake_direction == 'DOWN': angle = 180
                elif snake_direction == 'LEFT': angle = 90
                elif snake_direction == 'RIGHT': angle = -90
                head_sprite_rotated = pygame.transform.rotate(original_head_sprite, angle)
                surface.blit(head_sprite_rotated, rect)
        
        elif i == len(snake_body) - 1:  # Đuôi rắn
            prev_segment = snake_body[i-1]
            tail_direction = 'UP'
            if segment[1] > prev_segment[1]: tail_direction = 'UP'
            elif segment[1] < prev_segment[1]: tail_direction = 'DOWN'
            elif segment[0] > prev_segment[0]: tail_direction = 'LEFT'
            elif segment[0] < prev_segment[0]: tail_direction = 'RIGHT'
            
            # Lấy sprite đuôi gốc (hướng LÊN) và xoay
            original_tail_sprite = sprites['tail']
            angle = 0
            if tail_direction == 'DOWN': angle = 180
            elif tail_direction == 'LEFT': angle = 90
            elif tail_direction == 'RIGHT': angle = -90
            tail_sprite_rotated = pygame.transform.rotate(original_tail_sprite, angle)
            surface.blit(tail_sprite_rotated, rect)
        
        else:  # Thân rắn
            prev_segment, next_segment = snake_body[i-1], snake_body[i+1]
            if prev_segment[0] == next_segment[0]: # Thân dọc
                surface.blit(sprites['body_straight'], rect)
            elif prev_segment[1] == next_segment[1]: # Thân ngang
                # Xoay sprite thân thẳng từ DỌC sang NGANG
                body_horizontal = pygame.transform.rotate(sprites['body_straight'], 90)
                surface.blit(body_horizontal, rect)
            else: # Thân cong
                prev_vec = (prev_segment[0] - segment[0], prev_segment[1] - segment[1])
                next_vec = (next_segment[0] - segment[0], next_segment[1] - segment[1])
                
                key = None
                if (prev_vec in [(0, 1), (-1, 0)]) and (next_vec in [(0, 1), (-1, 0)]): key = 'bend_DOWN_LEFT'
                elif (prev_vec in [(0, 1), (1, 0)]) and (next_vec in [(0, 1), (1, 0)]): key = 'bend_DOWN_RIGHT'
                elif (prev_vec in [(0, -1), (-1, 0)]) and (next_vec in [(0, -1), (-1, 0)]): key = 'bend_UP_LEFT'
                elif (prev_vec in [(0, -1), (1, 0)]) and (next_vec in [(0, -1), (1, 0)]): key = 'bend_UP_RIGHT'
                
                if key: surface.blit(sprites[key], rect)

def draw_food(surface, food_data, blinking_info=None):
    food_sprite = food_logic.load_food_sprite()
    blinking_pos, is_blink_visible = (None, False)
    if blinking_info:
        blinking_pos, is_blink_visible = blinking_info

    for food in food_data:
        rect = pygame.Rect(food['pos'][0] * config.TILE_SIZE, food['pos'][1] * config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE)
        if food_sprite != "error":
            surface.blit(food_sprite, rect)
        else:
            pygame.draw.rect(surface, config.COLORS['food'], rect)
        
        if food['pos'] == blinking_pos and is_blink_visible:
            pygame.draw.circle(surface, config.COLORS['highlight'], rect.center, config.TILE_SIZE // 2 + 3, 3)