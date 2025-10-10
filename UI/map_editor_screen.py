import pygame
import config
from UI import UI_helpers
from Algorithms import BFS
def _check_map_solvability(map_data):
    """
        Kiểm tra xem map có thể giải được không.
        Điều kiện: Phải có đường đi từ đầu rắn đến TẤT CẢ thức ăn.
    """
    # Lấy ra danh sách tọa độ của rắn và thức ăn từ dữ liệu map.
    snake_start = map_data.get('snake_start')
    food_start = map_data.get('food_start')

    # Nếu chưa có rắn hoặc thức ăn thì không cần kiểm tra
    if not snake_start or not food_start:
        return False

    # Xác định đầu rắn (luôn là phần tử đầu tiên trong danh sách).
    snake_head = snake_start[0]
    # Các phần còn lại của rắn được coi là vật cản.
    snake_body_obstacles = snake_start[1:]

    # Dữ liệu map tối giản chỉ cần tường để gửi cho hàm BFS
    width = config.AI_MAP_WIDTH_TILES
    height = config.AI_MAP_HEIGHT_TILES
    temp_layout = ["." * width for _ in range(height)]
    
    # Tạo dữ liệu map tạm thời, lần này bao gồm cả 'layout'
    temp_map_for_check = {
        'walls': list(map_data['walls']),
        'layout': temp_layout
    }

    # Kiểm tra từng viên thức ăn
    for food_pos in food_start:
        # Gọi BFS để tìm đường từ đầu rắn đến một viên thức ăn
        result = BFS.find_path_bfs(snake_head, [food_pos], temp_map_for_check, snake_body_obstacles)
        
        # Nếu không tìm thấy đường đi cho DÙ CHỈ MỘT viên thức ăn, map không giải được
        if not result or not result.get('path'):
            return False

    # Nếu vòng lặp kết thúc (tất cả thức ăn đều có đường đi), map giải được
    return True

def run_map_editor(screen, clock):
    """Chạy màn hình vẽ map và trả về dữ liệu map đã tạo."""
    
    # --- 1. KHỞI TẠO ---
    panel_font = pygame.font.Font(config.FONT_PATH, 24)
    info_font = pygame.font.Font(config.FONT_PATH, 18)
    # Font mới cho phần hướng dẫn
    instruction_font = pygame.font.Font(config.FONT_PATH, 16)
    
    # Kích thước map editor (lấy từ config cho nhất quán)
    map_width_tiles = config.AI_MAP_WIDTH_TILES
    map_height_tiles = config.AI_MAP_HEIGHT_TILES
    
    map_width_px = map_width_tiles * config.TILE_SIZE
    map_height_px = map_height_tiles * config.TILE_SIZE
    
    # Bề mặt để vẽ map
    map_surface = pygame.Surface((map_width_px, map_height_px))
    
    # # Vị trí của map editor trên màn hình
    panel_width = config.EDITOR_PANEL_WIDTH
    padding = config.PADDING

    # Cột 1: Panel điều khiển (bên trái)
    panel_x = padding
    panel_center_x = panel_x + panel_width / 2

    # Cột 2: Khu vực vẽ map (ở giữa)
    map_area_x = panel_x + panel_width + padding
    map_area_y = (config.EDITOR_SCREEN_HEIGHT - map_height_px) / 2

    # Cột 3: Panel hướng dẫn (bên phải)
    instructions_x = map_area_x + map_width_px + padding

    # --- 2. QUẢN LÝ TRẠNG THÁI ---
    # Biến này theo dõi xem công cụ nào đang được chọn (vẽ Tường, Rắn, hay Thức ăn)
    active_tool = 'wall' # 'wall', 'snake', 'food'
    hover_pos = None # Vị trí ô đang di chuột tới
    # Một cờ (flag) đặc biệt để bật/tắt chế độ vẽ thân rắn bằng bàn phím.
    is_drawing_snake = False

    # --- TẠO KHUNG VIỀN MẶC ĐỊNH ---
    initial_walls = set()
    # Vẽ tường trên và dưới
    for x in range(map_width_tiles):
        initial_walls.add((x, 0))
        initial_walls.add((x, map_height_tiles - 1))
    # Vẽ tường trái và phải
    for y in range(map_height_tiles):
        initial_walls.add((0, y))
        initial_walls.add((map_width_tiles - 1, y))

    # Dữ liệu map được tạo trong bộ nhớ, bắt đầu với khung viền có sẵn
    map_data = {
        'walls': initial_walls,
        'snake_start': [],
        'food_start': set()
    }

    # --- 3. TẠO GIAO DIỆN ---
    panel_center_x = panel_width / 2
    
    tool_buttons = {
        'wall': UI_helpers.create_button(panel_center_x - 100, 100, 200, 50, "Wall"),
        'snake': UI_helpers.create_button(panel_center_x - 100, 160, 200, 50, "Snake"),
        'food': UI_helpers.create_button(panel_center_x - 100, 220, 200, 50, "Food"),
    }
    done_button = UI_helpers.create_button(panel_center_x - 100, config.SCREEN_HEIGHT - 100, 200, 50, "Done")

    # --- 4. VÒNG LẶP CHÍNH ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Tính toán vị trí chuột trên grid
        if map_area_x < mouse_pos[0] < map_area_x + map_width_px and \
           map_area_y < mouse_pos[1] < map_area_y + map_height_px:
            grid_x = int((mouse_pos[0] - map_area_x) // config.TILE_SIZE)
            grid_y = int((mouse_pos[1] - map_area_y) // config.TILE_SIZE)
            hover_pos = (grid_x, grid_y)
        else:
            hover_pos = None

        # Cập nhật hover cho các nút
        for btn in tool_buttons.values(): UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(done_button, mouse_pos)
        
        # --- 5. XỬ LÝ SỰ KIỆN ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # Dừng vòng lặp của editor và quay lại màn hình trước đó
            
            # --- Xử lý nhấn chuột ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Xử lý nút
                # Nếu click vào nút công cụ -> đổi `active_tool`.
                for tool, btn in tool_buttons.items():
                    if UI_helpers.handle_button_events(event, btn):
                        active_tool = tool

                # Nếu click vào nút "Done" -> kiểm tra, định dạng lại dữ liệu và `return final_map_data`.
                if UI_helpers.handle_button_events(event, done_button):
                    if not map_data['snake_start']:
                        print("Lỗi: Cần phải vẽ rắn trước khi hoàn thành!")
                    else:
                        # CHỈ ĐẢO NGƯỢC RẮN MỘT LẦN DUY NHẤT TẠI ĐÂY
                        final_snake_data = list(map_data['snake_start'])
                        final_snake_data.reverse()

                        final_map_data = {
                            'layout': [],
                            'walls': list(map_data['walls']),
                            'snake_start': final_snake_data, # Dùng dữ liệu rắn đã đảo ngược
                            'food_start': list(map_data['food_start'])
                        }
                        return final_map_data
                
                # Xử lý ĐẶT/XÓA cho các đối tượng click 1 lần (như Rắn)
                if hover_pos and active_tool == 'snake':
                    # Click trái: Đặt đầu rắn và bắt đầu vẽ
                    if event.button == 1:
                    # Chỉ đặt rắn nếu ô đó không phải là tường và không phải là thức ăn
                        if hover_pos not in map_data['walls'] and hover_pos not in map_data['food_start']:
                            is_drawing_snake = True
                            map_data['snake_start'] = [hover_pos] # Chỉ đặt đầu rắn
                        else:
                            print("Lỗi: Không thể đặt rắn lên tường hoặc thức ăn!")
                    
                    # Click phải: Xóa toàn bộ con rắn nếu click vào nó
                    elif event.button == 3:
                        if any(part == hover_pos for part in map_data['snake_start']):
                            map_data['snake_start'] = []
                            is_drawing_snake = False # Dừng chế độ vẽ nếu xóa rắn

            # Xử lý gõ phím cho textbox
            if event.type == pygame.KEYDOWN:
                if is_drawing_snake:
                    head = map_data['snake_start'][0]
                    new_head = None
                    
                    if event.key == pygame.K_UP:
                        new_head = (head[0], head[1] - 1)
                    elif event.key == pygame.K_DOWN:
                        new_head = (head[0], head[1] + 1)
                    elif event.key == pygame.K_LEFT:
                        new_head = (head[0] - 1, head[1])
                    elif event.key == pygame.K_RIGHT:
                        new_head = (head[0] + 1, head[1])
                    
                    elif event.key == pygame.K_BACKSPACE and len(map_data['snake_start']) > 1:
                        map_data['snake_start'].pop()
                    
                    elif event.key == pygame.K_RETURN:
                        # Nhấn Enter để kết thúc việc vẽ rắn.
                        is_drawing_snake = False

                    if new_head:
                        is_valid_move = True
                        if new_head in map_data['walls'] or new_head in map_data['snake_start'] or new_head in map_data['food_start']:
                            is_valid_move = False
                        if len(map_data['snake_start']) > 1 and new_head == map_data['snake_start'][1]:
                            is_valid_move = False

                        if is_valid_move:
                            map_data['snake_start'].insert(0, new_head)
                    
        # Lấy trạng thái của cả 3 nút chuột (trái, giữa, phải)
        mouse_buttons = pygame.mouse.get_pressed()
        if hover_pos and (active_tool == 'wall' or active_tool == 'food'):
            x, y = hover_pos
            is_border = (x == 0 or x == map_width_tiles - 1 or y == 0 or y == map_height_tiles - 1)
            if not is_border:
                if mouse_buttons[0]: # Chuột trái
                    # Nếu vẽ TƯỜNG, kiểm tra xem ô đó có phải là THỨC ĂN hoặc RẮN không
                    if active_tool == 'wall' and hover_pos not in map_data['food_start'] and hover_pos not in map_data['snake_start']:
                        map_data['walls'].add(hover_pos)
                    # Nếu vẽ THỨC ĂN, kiểm tra xem ô đó có phải là TƯỜNG hoặc RẮN không
                    elif active_tool == 'food' and hover_pos not in map_data['walls'] and hover_pos not in map_data['snake_start']:
                        map_data['food_start'].add(hover_pos)
                elif mouse_buttons[2]: # Chuột phải
                    if active_tool == 'wall' and hover_pos in map_data['walls']: map_data['walls'].remove(hover_pos)
                    elif active_tool == 'food' and hover_pos in map_data['food_start']: map_data['food_start'].remove(hover_pos)

        # --- 6. VẼ LÊN MÀN HÌNH ---
        screen.fill(config.COLORS['bg'])
        map_surface.fill(config.COLORS['black']) # Nền đen cho map

        # Vẽ lưới
        for x in range(0, map_width_px, config.TILE_SIZE):
            pygame.draw.line(map_surface, config.COLORS['border'], (x, 0), (x, map_height_px))
        for y in range(0, map_height_px, config.TILE_SIZE):
            pygame.draw.line(map_surface, config.COLORS['border'], (0, y), (map_width_px, y))

        # Vẽ các block đã đặt
        for x, y in map_data['walls']: pygame.draw.rect(map_surface, (150, 150, 150), (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))
        for x, y in map_data['food_start']: pygame.draw.rect(map_surface, config.COLORS['food'], (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))
        
        # Vẽ con rắn, phân biệt đầu và thân
        for i, (x, y) in enumerate(map_data['snake_start']):
            if i == 0:
                head_color = (0, 255, 127) # Màu xanh lá cây sáng cho đầu rắn
                pygame.draw.rect(map_surface, head_color, (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))
            else: # Đây là thân rắn
                body_color = (0, 200, 0) # Màu xanh lá cây đậm hơn cho thân
                pygame.draw.rect(map_surface, body_color, (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))

        # Vẽ "ghost" preview khi di chuột
        # Vẽ preview cho các công cụ Wall và Food
        if hover_pos and not is_drawing_snake and (active_tool == 'wall' or active_tool == 'food'):
            preview_surface = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
            if active_tool == 'wall': 
                preview_surface.fill((150, 150, 150, 128))
            else: 
                preview_surface.fill((*config.COLORS['food'], 128))
            map_surface.blit(preview_surface, (hover_pos[0] * config.TILE_SIZE, hover_pos[1] * config.TILE_SIZE))

        screen.blit(map_surface, (map_area_x, map_area_y))
        
        # --- VẼ PANEL ĐIỀU KHIỂN ---
        UI_helpers.draw_text("Map Editor", panel_font, config.COLORS['title'], screen, panel_center_x, 50)
        for tool, btn in tool_buttons.items():
            if tool == active_tool: # Highlight nút đang được chọn
                btn['color'], btn['hover_color'] = config.COLORS['btn_hover'], config.COLORS['btn_hover']
            else:
                btn['color'], btn['hover_color'] = config.COLORS['btn'], config.COLORS['btn_hover']
            UI_helpers.draw_button(screen, btn)
        UI_helpers.draw_button(screen, done_button)
        is_solvable = _check_map_solvability(map_data)

        status_text = ""
        status_color = config.COLORS['white']

        if not map_data['snake_start'] or not map_data['food_start']:
            status_text = "Trạng thái: Cần có Rắn và Thức ăn"
            status_color = (255, 255, 0) # Màu vàng
        elif is_solvable:
            status_text = "Trạng thái: Có thể giải được"
            status_color = (0, 255, 127) # Màu xanh lá
        else:
            status_text = "Trạng thái: Không giải được"
            status_color = (255, 100, 100) # Màu đỏ
        # --- VẼ HƯỚNG DẪN SỬ DỤNG ---
        instructions = [
            "HƯỚNG DẪN:",
            "- Chọn Wall/Food: Giữ Chuột Trái/Phải để Thêm/Xóa.",

            "",
            "- Chọn Snake:",
            "  1. CLICK TRÁI để đặt ĐUÔI.",
            "  2. Dùng MŨI TÊN để kéo dài ĐẦU.",
            "  3. Dùng BACKSPACE để xóa lùi.",
            "  4. Nhấn ENTER để hoàn thành.",
            "",
            "Nhấn 'Done' để lưu và thoát."
        ]
        
        # Vị trí bắt đầu vẽ hướng dẫn
        inst_start_x = instructions_x
        inst_start_y = map_area_y
        line_height = 22

        # Vẽ từng dòng hướng dẫn
        for i, line in enumerate(instructions):
            text_surf = instruction_font.render(line, True, config.COLORS['white'])
            screen.blit(text_surf, (inst_start_x, inst_start_y + i * line_height))
            status_y_pos = inst_start_y + len(instructions) * line_height + 20 # Vị trí ngay dưới hướng dẫn
            status_surf = info_font.render(status_text, True, status_color)
            screen.blit(status_surf, (inst_start_x, status_y_pos))

        pygame.display.flip()
        clock.tick(config.FPS)