import random
import pygame
import config
from UI import UI_helpers
from Algorithms import BFS

def _check_map_solvability(map_data):
    """
    Kiểm tra xem map có thể giải được không bằng cách mô phỏng chính xác
    trạng thái của rắn sau mỗi lần ăn mồi theo đúng thứ tự.
    """
    # Xử lý cả hai định dạng dữ liệu rắn
    snake_data = map_data.get('snake_start')
    initial_snake_body = []
    
    if isinstance(snake_data, dict):
        initial_snake_body = snake_data.get('body', [])
    elif isinstance(snake_data, list):
        if snake_data:
             initial_snake_body = list(reversed(snake_data))

    food_targets = []
    if map_data.get('food_mode') == 'sequential':
        food_targets = map_data.get('food_sequence', [])
    else:
        food_targets = list(map_data.get('food_start', []))

    if not initial_snake_body or not food_targets:
        return False

    # --- BẮT ĐẦU MÔ PHỎNG NÂNG CAO ---
    temp_snake_body = list(initial_snake_body)
    
    width = config.AI_MAP_WIDTH_TILES
    height = config.AI_MAP_HEIGHT_TILES
    temp_layout = ["." * width for _ in range(height)]
    temp_map_for_check = {
        'walls': list(map_data.get('walls', set())),
        'layout': temp_layout
    }

    # Lặp qua từng viên thức ăn THEO THỨ TỰ
    for food_pos in food_targets:
        current_head = temp_snake_body[0]
        current_obstacles = temp_snake_body[1:]

        # Tìm đường từ vị trí hiện tại đến viên thức ăn tiếp theo
        result = BFS.find_path_bfs(current_head, [food_pos], temp_map_for_check, current_obstacles)
        
        # Nếu không tìm thấy đường đi ở bất kỳ bước nào, map không giải được
        if not result or not result.get('path'):
            return False

        # --- MÔ PHỎNG RẮN DI CHUYỂN VÀ DÀI RA CHÍNH XÁC ---
        path = result['path']
        current_length = len(temp_snake_body)
        
        # Thân rắn mới sẽ bao gồm đường đi (đảo ngược) nối với thân cũ,
        # sau đó được cắt theo chiều dài mới (dài hơn 1).
        # Logic này mô phỏng đúng việc thân rắn chiếm lấy các ô trên đường đi.
        new_body_candidate = list(reversed(path)) + temp_snake_body
        temp_snake_body = new_body_candidate[:current_length + 1]

    # Nếu vòng lặp kết thúc (tất cả thức ăn đều được ăn thành công)
    return True

def run_map_editor(screen, clock):
    """Chạy màn hình vẽ map và trả về dữ liệu map đã tạo."""
    
    panel_font = pygame.font.Font(config.FONT_PATH, 24)
    info_font = pygame.font.Font(config.FONT_PATH, 18)
    instruction_font = pygame.font.Font(config.FONT_PATH, 16)
    
    map_width_tiles = config.AI_MAP_WIDTH_TILES
    map_height_tiles = config.AI_MAP_HEIGHT_TILES
    map_width_px = map_width_tiles * config.TILE_SIZE
    map_height_px = map_height_tiles * config.TILE_SIZE
    
    map_surface = pygame.Surface((map_width_px, map_height_px))
    
    panel_width = config.EDITOR_PANEL_WIDTH
    padding = config.PADDING
    panel_x = padding
    map_area_x = panel_x + panel_width + padding
    map_area_y = (config.EDITOR_SCREEN_HEIGHT - map_height_px) / 2
    instructions_x = map_area_x + map_width_px + padding

    active_tool = 'wall'
    hover_pos = None
    is_drawing_snake = False

    target_food_count = 10
    input_box_text = str(target_food_count)
    input_box_rect = pygame.Rect(panel_x + 20, 300, 100, 40)
    input_box_active = False

    initial_walls = set()
    for x in range(map_width_tiles):
        initial_walls.add((x, 0))
        initial_walls.add((x, map_height_tiles - 1))
    for y in range(map_height_tiles):
        initial_walls.add((0, y))
        initial_walls.add((map_width_tiles - 1, y))

    map_data = {
        'walls': initial_walls,
        'snake_start': [],
        'food_start': []
    }

    panel_center_x = panel_width / 2
    tool_buttons = {
        'wall': UI_helpers.create_button(panel_center_x - 100, 100, 200, 50, "Wall"),
        'snake': UI_helpers.create_button(panel_center_x - 100, 160, 200, 50, "Snake"),
        'food': UI_helpers.create_button(panel_center_x - 100, 220, 200, 50, "Food"),
    }
    done_button = UI_helpers.create_button(panel_center_x - 100, config.SCREEN_HEIGHT - 100, 200, 50, "Done")

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        if map_area_x < mouse_pos[0] < map_area_x + map_width_px and \
           map_area_y < mouse_pos[1] < map_area_y + map_height_px:
            grid_x = int((mouse_pos[0] - map_area_x) // config.TILE_SIZE)
            grid_y = int((mouse_pos[1] - map_area_y) // config.TILE_SIZE)
            hover_pos = (grid_x, grid_y)
        else:
            hover_pos = None

        for btn in tool_buttons.values(): UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(done_button, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            is_button_click = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box_rect.collidepoint(event.pos):
                    input_box_active = not input_box_active
                else:
                    input_box_active = False
            
            for tool, btn in tool_buttons.items():
                if UI_helpers.handle_button_events(event, btn):
                    active_tool = tool
                    is_button_click = True
            
            if event.type == pygame.KEYDOWN and input_box_active:
                if event.key == pygame.K_RETURN:
                    input_box_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_box_text = input_box_text[:-1]
                elif event.unicode.isdigit():
                    input_box_text += event.unicode
                target_food_count = int(input_box_text) if input_box_text else 0
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if UI_helpers.handle_button_events(event, done_button):
                    if not map_data['snake_start'] or target_food_count == 0:
                        print("Lỗi: Cần có rắn và số lượng thức ăn > 0!")
                    else:
                        ordered_food = list(map_data['food_start'])
                        food_needed = target_food_count - len(ordered_food)
                        
                        if food_needed > 0:
                            all_pos = set((x, y) for x in range(map_width_tiles) for y in range(map_height_tiles))
                            occupied_pos = map_data['walls'].union(set(map_data['snake_start'])).union(set(map_data['food_start']))
                            available_pos = list(all_pos - occupied_pos)
                            
                            if len(available_pos) >= food_needed:
                                random_food = random.sample(available_pos, food_needed)
                                ordered_food.extend(random_food)
                            else:
                                print(f"Không đủ chỗ, chỉ sinh thêm được {len(available_pos)} thức ăn.")
                                ordered_food.extend(random.sample(available_pos, len(available_pos)))
                        
                        final_snake_data = list(map_data['snake_start'])
                        final_map_data = {
                            'layout': [],
                            'walls': list(map_data['walls']),
                            'snake_start': {'body': final_snake_data, 'direction': 'RIGHT'},
                            'food_sequence': ordered_food,
                            'food_mode': 'sequential'
                        }
                        if _check_map_solvability(final_map_data):
                             return final_map_data
                        else:
                             print("Map không hợp lệ! Rắn không thể đến được viên thức ăn đầu tiên.")

                if not is_button_click and hover_pos:
                    if active_tool == 'snake':
                        if event.button == 1:
                            if hover_pos not in map_data['walls'] and hover_pos not in map_data['food_start']:
                                is_drawing_snake = True
                                map_data['snake_start'] = [hover_pos] 
                            else:
                                print("Lỗi: Không thể đặt rắn lên tường hoặc thức ăn!")
                        elif event.button == 3:
                            if any(part == hover_pos for part in map_data['snake_start']):
                                map_data['snake_start'] = []
                                is_drawing_snake = False

            if event.type == pygame.KEYDOWN:
                if is_drawing_snake:
                    head = map_data['snake_start'][0]
                    new_head = None
                    if event.key == pygame.K_UP: new_head = (head[0], head[1] - 1)
                    elif event.key == pygame.K_DOWN: new_head = (head[0], head[1] + 1)
                    elif event.key == pygame.K_LEFT: new_head = (head[0] - 1, head[1])
                    elif event.key == pygame.K_RIGHT: new_head = (head[0] + 1, head[1])
                    elif event.key == pygame.K_BACKSPACE and len(map_data['snake_start']) > 1:
                        map_data['snake_start'].pop(0) # Xóa đầu
                    elif event.key == pygame.K_RETURN:
                        is_drawing_snake = False

                    if new_head:
                        is_valid_move = True
                        if new_head in map_data['walls'] or new_head in map_data['snake_start'] or new_head in map_data['food_start']:
                            is_valid_move = False
                        if len(map_data['snake_start']) > 1 and new_head == map_data['snake_start'][1]:
                            is_valid_move = False
                        if is_valid_move:
                            map_data['snake_start'].insert(0, new_head)
        
        mouse_buttons = pygame.mouse.get_pressed()
        if hover_pos and (active_tool == 'wall' or active_tool == 'food'):
            x, y = hover_pos
            is_border = (x == 0 or x == map_width_tiles - 1 or y == 0 or y == map_height_tiles - 1)
            if not is_border:
                if mouse_buttons[0]:
                    if active_tool == 'wall' and hover_pos not in map_data['food_start'] and hover_pos not in map_data['snake_start']:
                        map_data['walls'].add(hover_pos)
                    elif active_tool == 'food' and len(map_data['food_start']) < target_food_count and hover_pos not in map_data['walls'] and hover_pos not in map_data['snake_start'] and hover_pos not in map_data['food_start']:
                        map_data['food_start'].append(hover_pos)
                elif mouse_buttons[2]:
                    if active_tool == 'wall':
                        map_data['walls'].discard(hover_pos)
                    elif active_tool == 'food':
                        if hover_pos in map_data['food_start']:
                            map_data['food_start'].remove(hover_pos)

        screen.fill(config.COLORS['bg'])
        map_surface.fill(config.COLORS['black'])

        for x in range(0, map_width_px, config.TILE_SIZE):
            pygame.draw.line(map_surface, config.COLORS['border'], (x, 0), (x, map_height_px))
        for y in range(0, map_height_px, config.TILE_SIZE):
            pygame.draw.line(map_surface, config.COLORS['border'], (0, y), (map_width_px, y))

        for x, y in map_data['walls']: pygame.draw.rect(map_surface, (150, 150, 150), (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))
        
        # Vẽ số thứ tự cho thức ăn
        for i, (x, y) in enumerate(map_data['food_start']):
            food_rect = pygame.Rect(x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE)
            pygame.draw.rect(map_surface, config.COLORS['food'], food_rect)
            UI_helpers.draw_text(str(i+1), info_font, (0,0,0), map_surface, food_rect.centerx, food_rect.centery)

        for i, (x, y) in enumerate(map_data['snake_start']):
            color = (0, 255, 127) if i == 0 else (0, 200, 0)
            pygame.draw.rect(map_surface, color, (x*config.TILE_SIZE, y*config.TILE_SIZE, config.TILE_SIZE, config.TILE_SIZE))

        if hover_pos and not is_drawing_snake and (active_tool == 'wall' or active_tool == 'food'):
            preview_surface = pygame.Surface((config.TILE_SIZE, config.TILE_SIZE), pygame.SRCALPHA)
            color = (150, 150, 150, 128) if active_tool == 'wall' else (*config.COLORS['food'], 128)
            preview_surface.fill(color)
            map_surface.blit(preview_surface, (hover_pos[0] * config.TILE_SIZE, hover_pos[1] * config.TILE_SIZE))

        screen.blit(map_surface, (map_area_x, map_area_y))
        
        UI_helpers.draw_text("Map Editor", panel_font, config.COLORS['title'], screen, panel_center_x, 50)
        for tool, btn in tool_buttons.items():
            is_active = (tool == active_tool)
            btn['color'] = config.COLORS['btn_hover'] if is_active else config.COLORS['btn']
            btn['hover_color'] = config.COLORS['btn_hover']
            UI_helpers.draw_button(screen, btn)
        UI_helpers.draw_button(screen, done_button)
        
        is_solvable = _check_map_solvability(map_data)
        status_text = "Trạng thái: Cần Rắn và Thức ăn"
        status_color = (255, 255, 0)
        if map_data['snake_start'] and map_data['food_start']:
            if is_solvable:
                status_text = "Trạng thái: Có thể giải được"
                status_color = (0, 255, 127)
            else:
                status_text = "Trạng thái: Không giải được"
                status_color = (255, 100, 100)

        UI_helpers.draw_text("Food Quantity:", info_font, config.COLORS['white'], screen, input_box_rect.centerx, input_box_rect.y - 20)
        box_color = config.COLORS['highlight'] if input_box_active else config.COLORS['white']
        pygame.draw.rect(screen, box_color, input_box_rect, 2, 5)
        UI_helpers.draw_text(input_box_text, info_font, config.COLORS['white'], screen, input_box_rect.centerx, input_box_rect.centery)
        food_count_text = f"Placed: {len(map_data['food_start'])} / {target_food_count}"
        UI_helpers.draw_text(food_count_text, info_font, config.COLORS['white'], screen, input_box_rect.centerx + 130, input_box_rect.centery)
        
        instructions = [
            "HƯỚNG DẪN:",
            "- Chọn Wall/Food: Giữ Chuột Trái/Phải để Thêm/Xóa.",
            "  (Thứ tự thức ăn dựa trên lúc tạo)",
            "",
            "- Chọn Snake:",
            "  1. CLICK TRÁI để đặt ĐUÔI.",
            "  2. Dùng MŨI TÊN để kéo dài ĐẦU.",
            "  3. Dùng BACKSPACE để xóa lùi.",
            "  4. Nhấn ENTER để hoàn thành.",
            "",
            "Nhấn 'Done' để lưu và thoát."
        ]
        
        inst_start_x = instructions_x
        inst_start_y = map_area_y
        line_height = 22
        for i, line in enumerate(instructions):
            text_surf = instruction_font.render(line, True, config.COLORS['white'])
            screen.blit(text_surf, (inst_start_x, inst_start_y + i * line_height))
        
        status_y_pos = inst_start_y + len(instructions) * line_height + 20
        status_surf = info_font.render(status_text, True, status_color)
        screen.blit(status_surf, (inst_start_x, status_y_pos))

        pygame.display.flip()
        clock.tick(config.FPS)