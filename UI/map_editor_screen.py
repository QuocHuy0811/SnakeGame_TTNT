import pygame
import config
from UI import UI_helpers

def run_map_editor(screen, clock):
    """Chạy màn hình vẽ map và trả về dữ liệu map đã tạo."""
    
    # --- 1. KHỞI TẠO ---
    panel_font = pygame.font.Font(config.FONT_PATH, 24)
    info_font = pygame.font.Font(config.FONT_PATH, 18)
    
    # Kích thước map editor (lấy từ config cho nhất quán)
    map_width_tiles = config.AI_MAP_WIDTH_TILES
    map_height_tiles = config.AI_MAP_HEIGHT_TILES
    
    map_width_px = map_width_tiles * config.TILE_SIZE
    map_height_px = map_height_tiles * config.TILE_SIZE
    
    # Bề mặt để vẽ map
    map_surface = pygame.Surface((map_width_px, map_height_px))
    
    # Vị trí của map editor trên màn hình
    panel_width = 300
    map_area_x = panel_width + 50
    map_area_y = (config.SCREEN_HEIGHT - map_height_px) / 2

    # --- 2. QUẢN LÝ TRẠNG THÁI ---
    active_tool = 'wall' # 'wall', 'snake', 'food'
    snake_size_str = '3'
    textbox_active = False
    hover_pos = None # Vị trí ô đang di chuột tới

    # BIẾN MỚI: Thêm các biến để xoay rắn
    snake_orientation = 'RIGHT' # Hướng mặc định
    orientation_cycle = ['RIGHT', 'DOWN', 'LEFT', 'UP']
    orientation_index = 0

    # Dữ liệu map được tạo trong bộ nhớ
    map_width_tiles = config.AI_MAP_WIDTH_TILES
    map_height_tiles = config.AI_MAP_HEIGHT_TILES

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
    
    textbox_rect = pygame.Rect(panel_center_x - 100, 320, 200, 40)

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
                pygame.quit()
                exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Kích hoạt textbox
                if textbox_rect.collidepoint(mouse_pos):
                    textbox_active = True
                else:
                    textbox_active = False
                
                # Xử lý nút
                for tool, btn in tool_buttons.items():
                    if UI_helpers.handle_button_events(event, btn):
                        active_tool = tool
                
                if UI_helpers.handle_button_events(event, done_button):
                    if not map_data['snake_start']:
                        print("Lỗi: Cần phải vẽ rắn trước khi hoàn thành!")
                    else:
                        # Chuyển đổi set thành list để tương thích
                        final_map_data = {
                            'layout': [], # Sẽ được tạo tự động
                            'walls': list(map_data['walls']),
                            'snake_start': map_data['snake_start'],
                            'food_start': list(map_data['food_start'])
                        }
                        return final_map_data # Trả về dữ liệu map
                
                # Xử lý ĐẶT/XÓA cho các đối tượng click 1 lần (như Rắn)
                if hover_pos:
                    # Đặt rắn (click trái)
                    if event.button == 1 and active_tool == 'snake':
                        try:
                            size = int(snake_size_str)
                            px, py = hover_pos
                            snake_body = []
                            if snake_orientation == 'RIGHT':
                                snake_body = [(px - i, py) for i in range(size)]
                            elif snake_orientation == 'LEFT':
                                snake_body = [(px + i, py) for i in range(size)]
                            elif snake_orientation == 'DOWN':
                                snake_body = [(px, py - i) for i in range(size)]
                            elif snake_orientation == 'UP':
                                snake_body = [(px, py + i) for i in range(size)]
                            map_data['snake_start'] = snake_body
                        except ValueError:
                            print("Kích thước rắn không hợp lệ")

                    # Xóa rắn (click phải)
                    elif event.button == 3:
                        # Xóa rắn nếu click vào bất kỳ bộ phận nào của nó
                        if any(part == hover_pos for part in map_data['snake_start']):
                            map_data['snake_start'] = []

            # Xử lý gõ phím cho textbox
            if event.type == pygame.KEYDOWN and textbox_active:
                if event.key == pygame.K_BACKSPACE:
                    snake_size_str = snake_size_str[:-1]
                elif event.unicode.isdigit():
                    snake_size_str += event.unicode
            
            # SỰ KIỆN MỚI: Xử lý lăn chuột để xoay rắn
            if event.type == pygame.MOUSEWHEEL and active_tool == 'snake':
                # event.y > 0 là lăn lên, < 0 là lăn xuống
                if event.y > 0:
                    orientation_index = (orientation_index + 1) % 4
                else:
                    orientation_index = (orientation_index - 1 + 4) % 4
                snake_orientation = orientation_cycle[orientation_index]
        
        # --- LOGIC MỚI: XỬ LÝ NHẤN GIỮ VÀ KÉO CHUỘT ---
        # Lấy trạng thái của cả 3 nút chuột (trái, giữa, phải)
        mouse_buttons = pygame.mouse.get_pressed()
        
        if hover_pos:
            # Nếu nút chuột TRÁI đang được nhấn giữ
            if mouse_buttons[0]:
                if active_tool == 'wall':
                    map_data['walls'].add(hover_pos)
                elif active_tool == 'food':
                    map_data['food_start'].add(hover_pos)
            
            # Nếu nút chuột PHẢI đang được nhấn giữ
            elif mouse_buttons[2]:
                x, y = hover_pos
                is_border = (x == 0 or x == map_width_tiles - 1 or y == 0 or y == map_height_tiles - 1)
                
                # Chỉ cho phép xóa tường và thức ăn (không xóa viền)
                if not is_border:
                    if hover_pos in map_data['walls']: 
                        map_data['walls'].remove(hover_pos)
                    if hover_pos in map_data['food_start']: 
                        map_data['food_start'].remove(hover_pos)

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
            if i == 0: # Đây là đầu rắn
                head_color = (0, 255, 127) # Màu xanh lá cây sáng cho đầu rắn
                pygame.draw.rect(map_surface, head_color, (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))
            else: # Đây là thân rắn
                body_color = (0, 200, 0) # Màu xanh lá cây đậm hơn cho thân
                pygame.draw.rect(map_surface, body_color, (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))

        # Vẽ "ghost" preview khi di chuột
        if hover_pos:
            preview_surface = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
            
            if active_tool == 'wall':
                preview_surface.fill((150, 150, 150, 128))
                map_surface.blit(preview_surface, (hover_pos[0] * config.TILE_SIZE, hover_pos[1] * config.TILE_SIZE))
            
            elif active_tool == 'food':
                preview_surface.fill((*config.COLORS['food'], 128))
                map_surface.blit(preview_surface, (hover_pos[0] * config.TILE_SIZE, hover_pos[1] * config.TILE_SIZE))

            elif active_tool == 'snake':
                try:
                    size = int(snake_size_str)
                    px, py = hover_pos
                    preview_positions = []
                    if snake_orientation == 'RIGHT':
                        preview_positions = [(px - i, py) for i in range(size)]
                    elif snake_orientation == 'LEFT':
                        preview_positions = [(px + i, py) for i in range(size)]
                    elif snake_orientation == 'DOWN':
                        preview_positions = [(px, py - i) for i in range(size)]
                    elif snake_orientation == 'UP':
                        preview_positions = [(px, py + i) for i in range(size)]
                    
                    for pos in preview_positions:
                        preview_surface.fill((0, 200, 0, 128))
                        map_surface.blit(preview_surface, (pos[0] * config.TILE_SIZE, pos[1] * config.TILE_SIZE))
                except ValueError: pass

        screen.blit(map_surface, (map_area_x, map_area_y))
        
        # Vẽ panel điều khiển
        UI_helpers.draw_text("Map Editor", panel_font, config.COLORS['title'], screen, panel_center_x, 50)
        for tool, btn in tool_buttons.items():
            if tool == active_tool: # Highlight nút đang được chọn
                btn['color'], btn['hover_color'] = config.COLORS['btn_hover'], config.COLORS['btn_hover']
            else:
                btn['color'], btn['hover_color'] = config.COLORS['btn'], config.COLORS['btn_hover']
            UI_helpers.draw_button(screen, btn)
        
        # Vẽ textbox
        UI_helpers.draw_text("Snake Size:", info_font, config.COLORS['white'], screen, panel_center_x, 300)
        pygame.draw.rect(screen, config.COLORS['border'] if textbox_active else config.COLORS['box'], textbox_rect, border_radius=5)
        UI_helpers.draw_text(snake_size_str, panel_font, config.COLORS['white'], screen, textbox_rect.centerx, textbox_rect.centery)

        UI_helpers.draw_button(screen, done_button)
        
        pygame.display.flip()
        clock.tick(config.FPS)