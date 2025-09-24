# UI/AI_screen.py
import pygame
import config
import copy
from UI import UI_helpers
from UI.MainMenu import background_effects
from GameLogic import game_helpers, snake_logic, food_logic
from GameLogic.game_controller import GameController 
from Algorithms import BFS, Astar, UCS, DFS, Greedy
from UI import history_screen

def find_path_with_algorithm(algorithm_func, start_pos, food_data, map_data, snake_body):
    # ... (Hàm này không thay đổi)
    shortest_path = None; min_len = float('inf'); food_positions = [food['pos'] for food in food_data]
    if algorithm_func in [BFS.find_path_bfs, Astar.find_path_astar, Greedy.find_path_greedy]:
        for food_pos in food_positions:
            path = algorithm_func(start_pos, [food_pos], map_data, snake_body)
            if path and len(path) < min_len: min_len, shortest_path = len(path), path
    else: shortest_path = algorithm_func(start_pos, food_positions, map_data, snake_body)
    return shortest_path

def _calculate_full_playthrough(initial_snake, initial_food, selected_mode, map_data):
    """
    Hàm này tính toán toàn bộ quá trình chơi của AI để có được kết quả cuối cùng.
    Nó trả về trạng thái rắn, tổng số bước, và tổng thời gian tìm kiếm.
    """
    # Tạo bản sao sâu để không ảnh hưởng đến game thật
    temp_snake_body = copy.deepcopy(initial_snake['body'])
    temp_food = copy.deepcopy(initial_food)
    
    initial_length = len(temp_snake_body)
    total_food_eaten = 0
    total_steps = 0
    total_search_time = 0.0
    
    # Lịch sử tất cả các vị trí đầu rắn đã đi qua
    path_history = temp_snake_body[:] # Bắt đầu với vị trí ban đầu

    algorithm_map = {"BFS": BFS.find_path_bfs, "A*": Astar.find_path_astar, "UCS": UCS.find_path_ucs, "DFS": DFS.find_path_dfs, "Greedy": Greedy.find_path_greedy}
    algorithm_to_run = algorithm_map.get(selected_mode)
    if not algorithm_to_run: return None

    while temp_food:
        search_start_time = pygame.time.get_ticks()
        path = find_path_with_algorithm(algorithm_to_run, temp_snake_body[0], temp_food, map_data, temp_snake_body)
        total_search_time += (pygame.time.get_ticks() - search_start_time) / 1000.0

        if not path or len(path) <= 1:
            return {'outcome': 'Stuck', 'steps': total_steps, 'search_time': total_search_time, 'snake': {'body': temp_snake_body, 'direction': 'RIGHT'}}

        eaten_food_pos = path[-1]
        
        # Di chuyển con rắn giả lập theo path
        for step in path[1:]:
            temp_snake_body.insert(0, step)
            path_history.append(step) # Ghi lại lịch sử
            total_steps += 1
        
        # Xóa thức ăn đã ăn và tăng số lượng
        temp_food = [f for f in temp_food if f['pos'] != eaten_food_pos]
        total_food_eaten += 1
        
        # Giữ cho rắn dài ra bằng cách không cắt đuôi
        final_snake_length = initial_length + total_food_eaten
        while len(temp_snake_body) > final_snake_length:
            temp_snake_body.pop()

    # --- XÂY DỰNG LẠI THÂN RẮN CUỐI CÙNG ---
    # Thân rắn cuối cùng là các vị trí cuối cùng trong lịch sử di chuyển
    final_snake_length = initial_length + total_food_eaten
    final_body = path_history[-final_snake_length:]
    return {
        'outcome': 'Completed', 'steps': total_steps, 'search_time': total_search_time,
        'snake': {'body': final_body, 'direction': 'RIGHT'} # Hướng không quan trọng
    }

def run_ai_game(screen, clock, selected_map_name):
    # --- 1. KHỞI TẠO ---
    panel_font = pygame.font.Font(config.FONT_PATH, 24); 
    info_font_bold = pygame.font.Font(config.FONT_PATH, 32); 
    info_font = pygame.font.Font(config.FONT_PATH, 26)

    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 200)
    
    # Tạo bề mặt (surface) riêng cho khu vực game
    game_area_width = config.AI_MAP_WIDTH_TILES * config.TILE_SIZE
    game_area_height = config.AI_MAP_HEIGHT_TILES * config.TILE_SIZE
    game_surface = pygame.Surface((game_area_width, game_area_height))

    # Tính khoảng đệm trên/dưới để căn giữa theo chiều dọc
    game_area_y = (config.SCREEN_HEIGHT - game_area_height) / 2
    # Gán khoảng đệm bên trái bằng đúng khoảng đệm trên/dưới
    game_area_x = game_area_y   
    
    controller = GameController(selected_map_name)

    # --- 2. QUẢN LÝ TRẠNG THÁI GIAO DIỆN ---
    game_state = "IDLE"
    selected_mode =  "Player"
    is_mode_combobox_open = False

    ai_path = [] 
    animation_step = 0 
    last_animation_time = 0 
    animation_interval = 80

    current_time = 0.0 
    total_search_time = 0.0

    # --- 3. TẠO CÁC THÀNH PHẦN GIAO DIỆN (UI) ---
    panel_x = config.SCREEN_WIDTH - config.AI_PANEL_WIDTH
    panel_center_x = panel_x + config.AI_PANEL_WIDTH / 2
    
    buttons = {
        'load_snake': UI_helpers.create_button(panel_center_x - 125, 100, 250, 40, "Load Snake"),
        'solve': UI_helpers.create_button(panel_center_x - 125, 150, 250, 40, "Solve"),
        'reset': UI_helpers.create_button(panel_center_x - 125, 200, 250, 40, "Reset"),
        'history': UI_helpers.create_button(panel_center_x - 125, 250, 250, 40, "History"),
        'back_to_menu': UI_helpers.create_button(panel_center_x - 125, 300, 250, 40, "Back to Menu")
    }
    mode_combobox = {
        'header': UI_helpers.create_button(panel_center_x - 125, 350, 250, 40, f"Mode: {selected_mode}"),
        'options': [UI_helpers.create_button(panel_center_x - 125, 350 + (i + 1) * 45, 250, 35, mode) for i, mode in enumerate(["Player", "BFS", "DFS", "A*", "UCS", "Greedy"])]
    }

    map_end_x = game_area_x + game_area_width
    middle_area_center_x = map_end_x + (panel_x - map_end_x) / 2
    middle_area_center_x -= 100 
    skip_button = UI_helpers.create_button(middle_area_center_x - 100, 550, 200, 50, "Skip")
    
    running = True
    while running:
        game_data = controller.get_state()
        mouse_pos = pygame.mouse.get_pos()
        
        # Cập nhật hover
        for btn in buttons.values(): UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(mode_combobox['header'], mouse_pos)
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(skip_button, mouse_pos)

        if game_state in ["AI_AUTOPLAY", "ANIMATING_PATH"]:
            UI_helpers.update_button_hover_state(skip_button, mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False

            if UI_helpers.handle_button_events(event, buttons['back_to_menu']): 
                running = False

            if UI_helpers.handle_button_events(event, buttons['reset']):
                controller.reset()
                game_state = "IDLE"
                ai_path = []
                animation_step = 0
                current_time = 0.0
                total_search_time = 0.0

            if UI_helpers.handle_button_events(event, buttons['solve']) and game_state == "IDLE":
                game_state = "AI_AUTOPLAY"
                current_time = 0.0
                total_search_time = 0.0

            if UI_helpers.handle_button_events(event, buttons['history']):
                history_screen.run_history_screen(screen, clock)

            if UI_helpers.handle_button_events(event, skip_button) and game_state in ["AI_AUTOPLAY", "ANIMATING_PATH"]:
                final_result = _calculate_full_playthrough(game_data['snake'], game_data['food'], selected_mode, controller.map_data)
                
                if final_result:
                    # Cập nhật controller với kết quả cuối cùng
                    controller.snake_data = final_result['snake']
                    controller.steps = final_result['steps']
                    controller.food_data = [] # Ăn hết thức ăn
                    controller.outcome = final_result['outcome']

                    # Cập nhật các biến hiển thị
                    total_search_time = final_result['search_time']
                    current_time = 0.0 # Animation time = 0 theo yêu cầu

                    # Lưu kết quả và quay về trạng thái chờ
                    game_helpers.save_game_result(selected_map_name, selected_mode, controller.steps, current_time, total_search_time, controller.outcome)
                    game_state = "IDLE"
                    ai_path = []
            
            if UI_helpers.handle_button_events(event, mode_combobox['header']):
                is_mode_combobox_open = not is_mode_combobox_open
            elif is_mode_combobox_open:
                for btn in mode_combobox['options']:
                    if UI_helpers.handle_button_events(event, btn):
                        selected_mode = btn['text']
                        mode_combobox['header']['text'] = f"Mode: {selected_mode}"
                        is_mode_combobox_open = False
                        break

        # --- LOGIC ĐIỀU KHIỂN ---
        if game_state == "AI_AUTOPLAY":
            if not ai_path and game_data['food']:
                algorithm_to_run = None
                if selected_mode == "BFS": algorithm_to_run = BFS.find_path_bfs
                elif selected_mode == "A*": algorithm_to_run = Astar.find_path_astar
                elif selected_mode == "UCS": algorithm_to_run = UCS.find_path_ucs
                elif selected_mode == "DFS": algorithm_to_run = DFS.find_path_dfs
                elif selected_mode == "Greedy": algorithm_to_run = Greedy.find_path_greedy
                if algorithm_to_run:
                    search_start_time = pygame.time.get_ticks()
                    path = find_path_with_algorithm(algorithm_to_run, game_data['snake']['body'][0], game_data['food'], controller.map_data, game_data['snake']['body'])
                    total_search_time += (pygame.time.get_ticks() - search_start_time) / 1000.0
                    if path: 
                        ai_path, animation_step, game_state = path, 0, "ANIMATING_PATH"; last_animation_time = pygame.time.get_ticks()
                    else:
                        controller.outcome = "Stuck"
                        game_helpers.save_game_result(selected_map_name, selected_mode, game_data['steps'], current_time, total_search_time, "Stuck")
                        game_state = "IDLE"
        
        if game_state == "ANIMATING_PATH":
            current_render_time = pygame.time.get_ticks()
            if current_render_time - last_animation_time > animation_interval:
                animation_step += 1
                if animation_step < len(ai_path):
                    controller.update_by_path_step(ai_path[animation_step])
                    last_animation_time = current_render_time
                    if controller.get_state()['outcome'] == "Completed":
                        game_state = "IDLE"
                        ai_path = []
                        current_time = controller.get_state()['steps'] * (animation_interval / 1000.0)
                        game_helpers.save_game_result(selected_map_name, selected_mode, controller.get_state()['steps'], current_time, total_search_time, "Completed")
                else:
                    ai_path, game_state = [], "AI_AUTOPLAY"

        # --- VẼ LÊN MÀN HÌNH ---\
        background_effects.draw_background(screen)

        game_surface.fill(config.COLORS['bg'])
        UI_helpers.draw_map(game_surface, controller.map_data)
        snake_logic.draw_snake(game_surface, game_data['snake'])
        food_logic.draw_food(game_surface, game_data['food'])
        
        screen.blit(game_surface, (game_area_x, game_area_y))

        current_time = game_data['steps'] * (animation_interval / 1000.0)
        
        game_surface = pygame.Surface((config.AI_MAP_WIDTH_TILES * config.TILE_SIZE, config.AI_MAP_HEIGHT_TILES * config.TILE_SIZE))
        
        UI_helpers.draw_text("ANIMATION TIME", info_font, config.COLORS['title'], screen, middle_area_center_x, 180) 
        UI_helpers.draw_text(f"{current_time:.4f} s", info_font_bold, config.COLORS['white'], screen, middle_area_center_x, 220)
        
        UI_helpers.draw_text("STEPS", info_font, config.COLORS['title'], screen, middle_area_center_x, 270)
        UI_helpers.draw_text(str(game_data['steps']), info_font_bold, config.COLORS['white'], screen, middle_area_center_x, 310)
        
        UI_helpers.draw_text("SEARCH TIME", info_font, config.COLORS['title'], screen, middle_area_center_x, 360); 
        UI_helpers.draw_text(f"{total_search_time:.4f} s", info_font_bold, config.COLORS['white'], screen, middle_area_center_x, 400)
        
        if game_state in ["AI_AUTOPLAY", "ANIMATING_PATH"]:
            UI_helpers.draw_button(screen, skip_button)

        panel_rect = pygame.Rect(panel_x, 0, config.AI_PANEL_WIDTH, config.SCREEN_HEIGHT); 
        pygame.draw.rect(screen, config.COLORS['white_bg'], panel_rect, border_radius=20)
        
        UI_helpers.draw_text("Control Panel", panel_font, config.COLORS['text_dark'], screen, panel_center_x, 50)
        
        for btn_data in buttons.values(): 
            UI_helpers.draw_button(screen, btn_data)
        
        UI_helpers.draw_button(screen, mode_combobox['header'])
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: 
                UI_helpers.draw_button(screen, btn)
        
        pygame.display.flip(); 
        clock.tick(config.FPS)