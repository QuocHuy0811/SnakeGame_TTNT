"""
    Giao diện chế độ AI
"""
import pygame
import config
import copy
from UI import UI_helpers
from UI.MainMenu import background_effects
from GameLogic import game_helpers, snake_logic, food_logic
from GameLogic.game_controller import GameController 
from Algorithms import BFS, Astar, UCS, DFS, Greedy
from UI import AI_selection_screen, history_screen

def find_path_with_algorithm(algorithm_func, start_pos, food_data, map_data, snake_body):
    food_positions = [food['pos'] for food in food_data]
    
    # Đối với các thuật toán tìm đường đến 1 food gần nhất
    if algorithm_func in [BFS.find_path_bfs, Astar.find_path_astar, Greedy.find_path_greedy]:
        shortest_result = {'path': None, 'visited': []}
        min_len = float('inf')
        
        all_visited_nodes = set()
        for food_pos in food_positions:
            result = algorithm_func(start_pos, [food_pos], map_data, snake_body)
            all_visited_nodes.update(result['visited']) # Gom tất cả các nút đã duyệt
            if result['path'] and len(result['path']) < min_len:
                min_len = len(result['path'])
                shortest_result['path'] = result['path']
        
        shortest_result['visited'] = list(all_visited_nodes)
        return shortest_result
    else: # Đối với các thuật toán khác
        return algorithm_func(start_pos, food_positions, map_data, snake_body)

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
        search_result = find_path_with_algorithm(algorithm_to_run, temp_snake_body[0], temp_food, map_data, temp_snake_body)
        path = search_result.get('path')

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
    instruction_font = pygame.font.Font(config.FONT_PATH, 18)

    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 1000)
    
    # Tải controller và dữ liệu map
    controller = GameController(selected_map_name)
    map_data = controller.map_data

    # Lấy kích thước thực tế từ map_data (số hàng và số cột)
    map_height_tiles = len(map_data['layout'])
    map_width_tiles = len(map_data['layout'][0]) if map_height_tiles > 0 else 0
    
    # Tạo bề mặt (surface) riêng cho khu vực game
    game_area_width = map_width_tiles * config.TILE_SIZE
    game_area_height = map_height_tiles * config.TILE_SIZE
    game_surface = pygame.Surface((game_area_width, game_area_height), pygame.SRCALPHA)

    # Tính khoảng đệm trên/dưới để căn giữa theo chiều dọc
    game_area_y = (config.SCREEN_HEIGHT - game_area_height) / 2
    # Gán khoảng đệm bên trái bằng đúng khoảng đệm trên/dưới
    game_area_x = game_area_y   
    
    

    # --- 2. QUẢN LÝ TRẠNG THÁI GIAO DIỆN ---
    game_state = "IDLE"
    selected_mode =  "Player"

    if selected_mode == "Player":
        game_state = "PLAYER_READY"

    ai_path = [] 
    animation_step = 0 
    last_animation_time = 0 
    animation_interval = 80

    visited_nodes = []
    path_nodes_to_draw = []

    visualization_timer_start = 0
    VISUALIZATION_DELAY = 500 #ms

    player_move_interval = 200 # Tốc độ di chuyển của người chơi
    last_player_move_time = 0

    current_time = 0.0 
    total_search_time = 0.0

    # --- THÊM BIẾN CHO HIỆU ỨNG NHẤP NHÁY ---
    target_food_pos = None
    is_blinking_visible = True
    last_blink_time = 0
    BLINK_INTERVAL = 200 # Tốc độ nháy (ms)

    # --- 3. TẠO CÁC THÀNH PHẦN GIAO DIỆN (UI) ---
    panel_x = config.SCREEN_WIDTH - config.AI_PANEL_WIDTH
    panel_center_x = panel_x + config.AI_PANEL_WIDTH / 2
    
    buttons = {
        'create_map': UI_helpers.create_button(panel_center_x - 125, 100, 250, 40, "Create Map"),
        'solve': UI_helpers.create_button(panel_center_x - 125, 150, 250, 40, "Solve"),
        'reset': UI_helpers.create_button(panel_center_x - 125, 200, 250, 40, "Reset"),
        'history': UI_helpers.create_button(panel_center_x - 125, 250, 250, 40, "History"),
        'back_to_menu': UI_helpers.create_button(panel_center_x - 125, 300, 250, 40, "Back to Menu"),
        'change_mode': UI_helpers.create_button(panel_center_x - 125, 350, 250, 40, f"Mode: {selected_mode}")
    }

    map_end_x = game_area_x + game_area_width
    middle_area_center_x = map_end_x + (panel_x - map_end_x) / 2 - 100
    skip_button = UI_helpers.create_button(middle_area_center_x - 100, 550, 200, 50, "Skip")
    
    if selected_mode == "Player":
        buttons['solve']['is_enabled'] = False
        buttons['solve']['text'] = "Start Game"

    running = True
    while running:
        game_data = controller.get_state()
        mouse_pos = pygame.mouse.get_pos()
        current_ticks = pygame.time.get_ticks()
        
        # Cập nhật hover
        for btn in buttons.values(): 
            UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(skip_button, mouse_pos)

        if game_state in ["AI_AUTOPLAY", "VISUALIZING", "ANIMATING_PATH"]:
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

                visited_nodes = []
                path_nodes_to_draw = []
                target_food_pos = None

                if selected_mode == "Player":
                    game_state = "PLAYER_READY"
                else: # Các chế độ AI
                    game_state = "IDLE"

            if UI_helpers.handle_button_events(event, buttons['solve']) and game_state == "IDLE":
                if selected_mode == "Player":
                    game_state = "PLAYER_PLAYING"
                    last_player_move_time = pygame.time.get_ticks()
                else: # Chế độ AI
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
                    ai_path  = []

                    visited_nodes = []
                    path_nodes_to_draw = []
                    target_food_pos = None
            
            if UI_helpers.handle_button_events(event, buttons['change_mode']):
                # Gọi cửa sổ pop-up và chờ kết quả trả về
                new_mode = AI_selection_screen.run_algorithm_selection(screen)
                if new_mode is not None: # Nếu người dùng chọn một mode mới
                    selected_mode = new_mode
                    buttons['change_mode']['text'] = f"Mode: {selected_mode}"
                    
                    # Cập nhật trạng thái nút Solve
                    if selected_mode == "Player":
                        buttons['solve']['is_enabled'] = False
                        buttons['solve']['text'] = "Start Game"
                        game_state = "PLAYER_READY" # Chuyển sang trạng thái sẵn sàng
                    else:
                        buttons['solve']['is_enabled'] = True
                        buttons['solve']['text'] = "Solve"
                        game_state = "IDLE" # Chuyển về trạng thái chờ cho AI

            if event.type == pygame.KEYDOWN:
                # Nếu game đang chờ, phím bấm đầu tiên sẽ bắt đầu game
                if game_state == "PLAYER_READY":
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        game_state = "PLAYER_PLAYING"
                        last_player_move_time = pygame.time.get_ticks()
                        # Đặt hướng đi ngay lập tức
                        if event.key == pygame.K_UP: controller.set_direction('UP')
                        elif event.key == pygame.K_DOWN: controller.set_direction('DOWN')
                        elif event.key == pygame.K_LEFT: controller.set_direction('LEFT')
                        elif event.key == pygame.K_RIGHT: controller.set_direction('RIGHT')

                # Nếu game đang chạy, phím bấm chỉ đổi hướng
                elif game_state == "PLAYER_PLAYING":
                    if event.key == pygame.K_UP: controller.set_direction('UP')
                    elif event.key == pygame.K_DOWN: controller.set_direction('DOWN')
                    elif event.key == pygame.K_LEFT: controller.set_direction('LEFT')
                    elif event.key == pygame.K_RIGHT: controller.set_direction('RIGHT')

        # --- LOGIC ĐIỀU KHIỂN ---
        if game_state == "PLAYER_PLAYING":
            # current_ticks = pygame.time.get_ticks()
            if current_ticks - last_player_move_time > player_move_interval:
                controller.update() # Gọi hàm update của controller cho người chơi
                last_player_move_time = current_ticks
            
            # Kiểm tra kết thúc game
            if game_data['outcome'] != "Playing":
                game_state = "IDLE"

        elif game_state == "AI_AUTOPLAY" and game_data['food']:
            if not ai_path and game_data['food']:
                algorithm_map = {"BFS": BFS.find_path_bfs, "A*": Astar.find_path_astar, "UCS": UCS.find_path_ucs, "DFS": DFS.find_path_dfs, "Greedy": Greedy.find_path_greedy}
                algorithm_to_run = algorithm_map.get(selected_mode)
                
                if algorithm_to_run:
                    search_start_time = pygame.time.get_ticks()
                    search_result = find_path_with_algorithm(algorithm_to_run, game_data['snake']['body'][0], game_data['food'], controller.map_data, game_data['snake']['body'])
                    total_search_time += (pygame.time.get_ticks() - search_start_time) / 1000.0
                    
                    visited_nodes = search_result.get('visited', [])
                    ai_path = search_result.get('path', None)
                    
                    if ai_path: 
                        path_nodes_to_draw = ai_path
                        target_food_pos = ai_path[-1]
                        game_state = "VISUALIZING"
                        visualization_timer_start = pygame.time.get_ticks()
                    else:
                        controller.outcome = "Stuck"
                        game_helpers.save_game_result(selected_map_name, selected_mode, game_data['steps'], current_time, total_search_time, "Stuck")
                        game_state = "IDLE"

        if game_state == "VISUALIZING":
            if current_ticks - last_blink_time > BLINK_INTERVAL:
                is_blinking_visible = not is_blinking_visible
                last_blink_time = current_ticks

            if current_ticks - visualization_timer_start > VISUALIZATION_DELAY:
                game_state = "ANIMATING_PATH"
                last_animation_time = current_ticks
                animation_step = 1

        elif game_state == "ANIMATING_PATH":
            current_render_time = pygame.time.get_ticks()
            if current_render_time - last_animation_time > animation_interval:
                # Kiểm tra xem có còn bước đi trong path không
                if animation_step < len(ai_path):
                    controller.update_by_path_step(ai_path[animation_step])
                    animation_step += 1
                    last_animation_time = current_render_time
                # Nếu đã đi hết path, animation cho đoạn này kết thúc
                else: 
                    visited_nodes, path_nodes_to_draw = [], [] # Xóa các chấm visualize
                    ai_path = [] # Xóa path cũ
                    target_food_pos = None
                    game_state = "AI_AUTOPLAY" # Quay lại tìm đường cho miếng mồi tiếp theo

            # Kiểm tra điều kiện thắng (có thể xảy ra bất cứ lúc nào trong lúc di chuyển)
            if controller.get_state()['outcome'] == "Completed":
                game_state = "IDLE"
                target_food_pos = None
                current_time = controller.get_state()['steps'] * (animation_interval / 1000.0)
                game_helpers.save_game_result(selected_map_name, selected_mode, controller.get_state()['steps'], current_time, total_search_time, "Completed")
                visited_nodes, path_nodes_to_draw = [], [] # Xóa các chấm visualize khi thắng

        # --- VẼ LÊN MÀN HÌNH ---\
        background_effects.draw_background(screen)
        game_surface.fill((0,0,0,0))

        if visited_nodes:
            UI_helpers.draw_search_visualization(game_surface, visited_nodes, path_nodes_to_draw)
        UI_helpers.draw_map(game_surface, controller.map_data)
        snake_logic.draw_snake(game_surface, game_data['snake'], game_data['food'])
        blinking_info = None
        if game_state == "VISUALIZING" and target_food_pos:
            blinking_info = (target_food_pos, is_blinking_visible)
        food_logic.draw_food(game_surface, game_data['food'], blinking_info)

        screen.blit(game_surface, (game_area_x, game_area_y))

        if selected_mode == "Player":
            instruction_y = game_area_y + game_area_height + 25
            instruction_x = game_area_x +  280
            UI_helpers.draw_text(
                "Di chuyển bằng phím mũi tên",
                instruction_font,
                config.COLORS['white'],
                screen,
                instruction_x,
                instruction_y
            )

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
        
        pygame.display.flip(); 
        clock.tick(config.FPS)