"""
    CÁC BIẾN TRONG FOLDER UI
    CÁC HÀM DÙNG CHUNG
"""
import pygame
import config
from GameLogic import snake_logic, food_logic, map_logic
from Algorithms.algorithm_helpers import manhattan_distance


pygame.init()
pygame.mixer.init()
# Tải âm thanh cho nút bấm, có xử lý lỗi nếu không tìm thấy file.
try:
    _click_sound = pygame.mixer.Sound("Assets/Sounds/click_button.mp3")
except pygame.error as e:
    print(f"Lỗi: Không thể tải file âm thanh 'click_button.mp3': {e}")
    _click_sound = None
try:
    _hover_sound = pygame.mixer.Sound("Assets/Sounds/cuon.wav")
except pygame.error as e:
    print(f"Lỗi: Không thể tải file âm thanh cuon.wav: {e}")
    _hover_sound = None
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
        'was_hovered': False, # <-- THÊM DÒNG NÀY
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
        # --- THÊM MỚI: Phát âm thanh khi click ---
        if _click_sound:
            _click_sound.play()
        # -----------------------------------------
        return True
    return False

def update_button_hover_state(button_data, mouse_pos):
    """
        Cập nhật trạng thái hover cho một nút và phát âm thanh khi bắt đầu hover.
    """
    if not button_data['is_enabled']:
        button_data['is_hovered'] = False
        return

    # Lấy trạng thái hover của frame trước
    was_hovered = button_data.get('was_hovered', False)

    # Tính trạng thái hover của frame này
    is_hovered_now = button_data['rect'].collidepoint(mouse_pos)
    button_data['is_hovered'] = is_hovered_now

    # Chỉ phát âm thanh nếu trạng thái thay đổi từ không-hover sang hover
    if is_hovered_now and not was_hovered:
        if _hover_sound:
            _hover_sound.play()

    # Cập nhật lại trạng thái 'was_hovered' cho frame tiếp theo
    button_data['was_hovered'] = is_hovered_now

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
    Vẽ TOÀN BỘ map: bao gồm cả nền lót (tile) và các block tường.
    """
    # --- PHẦN 1: VẼ NỀN LÓT (TILE) ---
    map_bg_sprite = map_logic.load_map_background_sprite()
    
    if map_bg_sprite == "error":
        surface.fill(config.COLORS['bg']) # Tô màu nền mặc định nếu lỗi
    else:
        surface_width, surface_height = surface.get_size()
        tile_size = config.TILE_SIZE
        for x in range(0, surface_width, tile_size):
            for y in range(0, surface_height, tile_size):
                surface.blit(map_bg_sprite, (x, y))

    # --- PHẦN 2: VẼ TƯỜNG LÊN TRÊN NỀN ---
    wall_sprite_image = map_logic.load_wall_sprite()
    
    if wall_sprite_image != "error":
        for x, y in map_data['walls']:
            rect = pygame.Rect(x * config.TILE_SIZE, y * config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE)
            surface.blit(wall_sprite_image, rect)
    else: # Fallback nếu sprite tường lỗi
        wall_color = config.COLORS['border'] 
        for x, y in map_data['walls']:
            rect = pygame.Rect(x * config.TILE_SIZE, y * config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE)
            pygame.draw.rect(surface, wall_color, rect)

# def draw_search_visualization(surface, visited_nodes, path_nodes):
#     """
#         Vẽ các ô đã duyệt (màu trắng) và đường đi cuối cùng (màu đỏ).
#     """
#     # Vẽ các ô đã duyệt trước
#     for pos in visited_nodes:
#         center_x = pos[0] * config.TILE_SIZE + config.TILE_SIZE // 2
#         center_y = pos[1] * config.TILE_SIZE + config.TILE_SIZE // 2
#         pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 3) # Chấm trắng

#     # Vẽ đường đi cuối cùng đè lên trên
#     for pos in path_nodes:
#         center_x = pos[0] * config.TILE_SIZE + config.TILE_SIZE // 2
#         center_y = pos[1] * config.TILE_SIZE + config.TILE_SIZE // 2
#         pygame.draw.circle(surface, (255, 80, 80), (center_x, center_y), 4) # Chấm đỏ

def draw_search_visualization(surface, visited_nodes, path_nodes):
    """
    Vẽ số thứ tự cho các ô đã duyệt và tô đỏ các số thuộc đường đi cuối cùng.
    
    :param surface: Bề mặt (Surface) để vẽ lên.
    :param visited_nodes: Danh sách các nút đã duyệt (đã có thứ tự).
    :param path_nodes: Danh sách các nút thuộc đường đi cuối cùng.
    """
    # 1. Khởi tạo một font chữ nhỏ để vẽ số.
    # Bạn có thể thay đổi kích thước '12' để số to hoặc nhỏ hơn.
    visualization_font = pygame.font.Font(config.FONT_PATH, 10)
    
    # 2. Chuyển danh sách đường đi thành một 'set' để kiểm tra nhanh hơn.
    path_set = set(path_nodes)

    # 3. Lặp qua danh sách các nút đã duyệt bằng 'enumerate'.
    #    'enumerate' sẽ trả về cả chỉ số (i) và giá trị (pos) cho mỗi phần tử.
    for i, pos in enumerate(visited_nodes):
        # Số để vẽ là chỉ số (i) + 1 (để bắt đầu từ 1 thay vì 0).
        number_text = str(i + 1)
        
        # 4. Mặc định màu số là màu trắng.
        text_color = config.COLORS['white']
        
        # Nếu vị trí hiện tại (pos) cũng nằm trong đường đi cuối cùng (path_set).
        if pos in path_set:
            # Đổi màu số thành màu đỏ nổi bật.
            text_color = (255, 80, 80)

        # 5. Tính toán tọa độ tâm của ô để vẽ số vào chính giữa.
        center_x = pos[0] * config.TILE_SIZE + config.TILE_SIZE // 2
        center_y = pos[1] * config.TILE_SIZE + config.TILE_SIZE // 2
        
        # 6. Gọi hàm draw_text để vẽ số đã được định dạng lên màn hình.
        draw_text(number_text, visualization_font, text_color, surface, center_x, center_y)

def draw_snake(surface, snake_data, food_data):
    """
    Vẽ con rắn bằng sprite, kết hợp cả hai logic:
    1. Thay đổi 'biểu cảm' đầu rắn khi đến gần mồi.
    2. Xoay tất cả các bộ phận theo hướng di chuyển thực tế.
    """
    snake_body = snake_data.get('body')
    if not snake_body: return

    # Gọi hàm load_snake_sprites từ chính module này
    sprites = snake_logic.load_snake_sprites()
    if not sprites or sprites == "error": return

    tile_size = config.TILE_SIZE
    
    # --- VẼ CÁC BỘ PHẬN ---
    for i, segment in enumerate(snake_body):
        rect = pygame.Rect(segment[0] * tile_size, segment[1] * tile_size, tile_size, tile_size)
        
        # --- 1. VẼ ĐẦU RẮN ---
        if i == 0:
            head_pos = segment

            # 1a. Chọn loại đầu rắn dựa vào khoảng cách đến mồi
            min_dist = float('inf')
            if food_data:
                food_positions = [food['pos'] for food in food_data]
                if food_positions:
                    min_dist = min(manhattan_distance(head_pos, food_pos) for food_pos in food_positions)
            
            head_type = 'head_normal'
            if min_dist == 1: head_type = 'head_eat'
            elif 1 < min_dist <= 3: head_type = 'head_ready'
            
            original_head_sprite = sprites.get(head_type)

            # 1b. Xác định hướng xoay dựa vào hướng di chuyển thực tế
            actual_direction = snake_data.get('direction', 'UP')
            if len(snake_body) > 1:
                next_pos = snake_body[1]
                if head_pos[0] > next_pos[0]: actual_direction = 'RIGHT'
                elif head_pos[0] < next_pos[0]: actual_direction = 'LEFT'
                elif head_pos[1] > next_pos[1]: actual_direction = 'DOWN'
                elif head_pos[1] < next_pos[1]: actual_direction = 'UP'

            # 1c. Xoay và vẽ đầu rắn
            if original_head_sprite:
                angle = 0
                if actual_direction == 'DOWN': angle = 180
                elif actual_direction == 'LEFT': angle = 90
                elif actual_direction == 'RIGHT': angle = -90
                rotated_head = pygame.transform.rotate(original_head_sprite, angle)
                surface.blit(rotated_head, rect)

        # --- 2. VẼ ĐUÔI RẮN ---
        elif i == len(snake_body) - 1:
            prev_segment = snake_body[i-1]
            tail_direction = 'UP'
            if segment[1] > prev_segment[1]: tail_direction = 'UP'
            elif segment[1] < prev_segment[1]: tail_direction = 'DOWN'
            elif segment[0] > prev_segment[0]: tail_direction = 'LEFT'
            elif segment[0] < prev_segment[0]: tail_direction = 'RIGHT'
            
            original_tail = sprites['tail']
            angle = 0
            if tail_direction == 'DOWN': angle = 180
            elif tail_direction == 'LEFT': angle = 90
            elif tail_direction == 'RIGHT': angle = -90
            rotated_tail = pygame.transform.rotate(original_tail, angle)
            surface.blit(rotated_tail, rect)
        
        # --- 3. VẼ THÂN RẮN ---
        else:
            prev_segment = snake_body[i-1]
            next_segment = snake_body[i+1]
            if prev_segment[0] == next_segment[0]: # Thân dọc
                surface.blit(sprites['body_straight'], rect)
            elif prev_segment[1] == next_segment[1]: # Thân ngang
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