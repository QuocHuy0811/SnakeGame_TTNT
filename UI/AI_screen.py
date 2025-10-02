"""
    Giao diện chế độ AI
"""
import pygame
from Algorithms.algorithm_helpers import manhattan_distance
import config
import copy
import time
from UI import UI_helpers
from UI.MainMenu import background_effects
from GameLogic import game_helpers, snake_logic, food_logic
from GameLogic.game_controller import GameController 
from Algorithms import BFS, Astar, UCS, DFS, Greedy, IDS
from UI import AI_selection_screen, history_screen, map_editor_screen 
    
def find_path_with_algorithm(algorithm_func, start_pos, food_data, map_data, snake_body):
    """
    Chạy thuật toán tìm đường MỘT LẦN DUY NHẤT để có kết quả chính xác.
    """
    food_positions = [food['pos'] for food in food_data]
    if not food_positions:
        # THAY ĐỔI: Trả về đúng định dạng mới
        return {'path': None, 'visited_nodes': [], 'generated_count': 0, 'visited_count': 0}

    # Đối với A* và Greedy, chúng cần một mục tiêu duy nhất.
    # Ta sẽ chọn mục tiêu gần nhất dựa trên khoảng cách Manhattan.
    if algorithm_func in [Astar.find_path_astar, Greedy.find_path_greedy]:
        
        # Tìm mục tiêu gần nhất
        target_pos = min(food_positions, key=lambda food: manhattan_distance(start_pos, food))
        
        # Chạy thuật toán một lần duy nhất với mục tiêu đó
        return algorithm_func(start_pos, [target_pos], map_data, snake_body)
    
    # Đối với các thuật toán khác (BFS, UCS, DFS), chúng có thể xử lý nhiều mục tiêu.
    # Chúng sẽ tự động dừng lại khi tìm thấy mục tiêu gần nhất đầu tiên.
    else:
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
    total_visited = 0
    total_generated = 0
    
    # Lịch sử tất cả các vị trí đầu rắn đã đi qua
    path_history = temp_snake_body[:] # Bắt đầu với vị trí ban đầu

    algorithm_map = {"BFS": BFS.find_path_bfs, "A*": Astar.find_path_astar, "UCS": UCS.find_path_ucs, "DFS": DFS.find_path_dfs, "Greedy": Greedy.find_path_greedy,"IDS": IDS.find_path_ids}
    algorithm_to_run = algorithm_map.get(selected_mode)
    if not algorithm_to_run: return None

    while temp_food:
        search_start_time = time.perf_counter() # THAY ĐỔI
        search_result = find_path_with_algorithm(algorithm_to_run, temp_snake_body[0], temp_food, map_data, temp_snake_body)
        path = search_result.get('path')

        total_search_time += (time.perf_counter() - search_start_time) # THAY ĐỔI
        # SỬA LỖI: Lấy đúng các giá trị đếm từ thuật toán
        total_visited += search_result.get('visited_count', 0)
        total_generated += search_result.get('generated_count', 0)

        if not path or len(path) <= 1:
            return {
                'outcome': 'Stuck', 'steps': total_steps, 'search_time': total_search_time,
                'snake': {'body': temp_snake_body, 'direction': 'RIGHT'},
                'visited': total_visited, 'generated': total_generated
            }
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
        'snake': {'body': final_body, 'direction': 'RIGHT'},
        'visited': total_visited, 'generated': total_generated
    }

def run_ai_game(screen, clock, selected_map_name):
    # --- 1. KHỞI TẠO ---
    panel_font = pygame.font.Font(config.FONT_PATH, 24); 
    info_font_bold = pygame.font.Font(config.FONT_PATH, 32); 
    info_font = pygame.font.Font(config.FONT_PATH, 26)
    instruction_font = pygame.font.Font(config.FONT_PATH, 18)
    end_game_font = pygame.font.Font(config.FONT_PATH, 50)
    #  Lưu kết quả tính toán đầy đủ khi nhấn Solve
    full_playthrough_result = None
    #  Thêm một bộ đếm cho các map tự tạo
    custom_map_counter = 1

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
    total_visited_nodes = 0
    total_generated_nodes = 0

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
    middle_area_center_x = map_end_x + (panel_x - map_end_x) / 2
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

            if UI_helpers.handle_button_events(event, buttons['create_map']):
                # Gọi màn hình editor
                created_map_data = map_editor_screen.run_map_editor(screen, clock)

                # Nếu người dùng hoàn thành và trả về map mới
                if created_map_data:
                    # Tạo một tên map mới và duy nhất
                    new_map_name = f"Create{custom_map_counter}"
                    custom_map_counter += 1
                    selected_map_name = new_map_name # Gán tên mới cho biến lưu tên map

                    # Khởi tạo lại controller với map mới
                    controller = GameController(created_map_data)
                    map_data = controller.map_data

                    # Tính toán lại kích thước và vị trí game area
                    map_height_tiles = len(map_data['layout'])
                    map_width_tiles = len(map_data['layout'][0]) if map_height_tiles > 0 else 0
                    game_area_width = map_width_tiles * config.TILE_SIZE
                    game_area_height = map_height_tiles * config.TILE_SIZE
                    game_surface = pygame.Surface((game_area_width, game_area_height), pygame.SRCALPHA)
                    game_area_y = (config.SCREEN_HEIGHT - game_area_height) / 2
                    game_area_x = game_area_y

                    # Reset lại toàn bộ trạng thái của màn hình AI (giống như nhấn nút Reset)
                    game_state = "IDLE"
                    ai_path = []
                    animation_step = 0
                    current_time = 0.0
                    total_search_time = 0.0
                    total_visited_nodes = 0
                    total_generated_nodes = 0
                    visited_nodes = []
                    path_nodes_to_draw = []
                    target_food_pos = None
                    if selected_mode == "Player":
                        game_state = "PLAYER_READY"

            if UI_helpers.handle_button_events(event, buttons['back_to_menu']): 
                running = False

            if UI_helpers.handle_button_events(event, buttons['reset']):
                controller.reset()
                game_state = "IDLE"
                ai_path = []
                animation_step = 0
                current_time = 0.0
                total_search_time = 0.0
                total_visited_nodes = 0
                total_generated_nodes = 0
                visited_nodes = []
                path_nodes_to_draw = []
                target_food_pos = None
                
                full_playthrough_result = None # <-- THÊM DÒNG QUAN TRỌNG NÀY

                if selected_mode == "Player":
                    game_state = "PLAYER_READY"
                else: # Các chế độ AI
                    game_state = "IDLE"

            if UI_helpers.handle_button_events(event, buttons['solve']):
                if game_state == "IDLE" or game_state == "PLAYER_READY":
                    controller.reset()
                    # Reset các biến và kết quả đã lưu
                    total_search_time = 0.0
                    total_visited_nodes = 0
                    total_generated_nodes = 0
                    full_playthrough_result = None 

                    if selected_mode == "Player":
                        game_state = "PLAYER_PLAYING"
                        last_player_move_time = pygame.time.get_ticks()
                    else:
                        # TÍNH TOÁN TRƯỚC TOÀN BỘ LỜI GIẢI VÀ LƯU LẠI
                        initial_snake = snake_logic.create_snake_from_map(controller.map_data)
                        initial_food = food_logic.create_food_from_map(controller.map_data)
                        full_playthrough_result = _calculate_full_playthrough(initial_snake, initial_food, selected_mode, controller.map_data)
                        
                        # Sau khi có kết quả, bắt đầu chế độ autoplay như bình thường
                        game_state = "AI_AUTOPLAY"

            if UI_helpers.handle_button_events(event, buttons['history']):
                history_screen.run_history_screen(screen, clock)

            if UI_helpers.handle_button_events(event, skip_button) and game_state in ["AI_AUTOPLAY", "ANIMATING_PATH"]:
                # Nếu đã có kết quả tính toán trước, hãy sử dụng nó
                if full_playthrough_result:
                    # Cập nhật controller với trạng thái cuối cùng
                    controller.snake_data = full_playthrough_result['snake']
                    controller.steps = full_playthrough_result['steps']
                    controller.food_data = [] 
                    controller.outcome = full_playthrough_result['outcome']

                    # Lưu kết quả CHÍNH XÁC đã tính toán trước đó
                    game_helpers.save_game_result(
                        selected_map_name, selected_mode, controller.steps, 
                        0.0, # Animation time khi skip là 0
                        full_playthrough_result['search_time'], 
                        controller.outcome,
                        full_playthrough_result['visited'], 
                        full_playthrough_result['generated']
                    )
                    
                    # Dọn dẹp và quay về trạng thái chờ
                    game_state = "IDLE"
                    ai_path, visited_nodes, path_nodes_to_draw = [], [], []
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

            if selected_mode == "Player":
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
                algorithm_map = {"BFS": BFS.find_path_bfs, "A*": Astar.find_path_astar, "UCS": UCS.find_path_ucs, "DFS": DFS.find_path_dfs, "Greedy": Greedy.find_path_greedy, "IDS": IDS.find_path_ids}
                algorithm_to_run = algorithm_map.get(selected_mode)
                
                if algorithm_to_run:
                    search_start_time = pygame.time.get_ticks()
                    search_result = find_path_with_algorithm(algorithm_to_run, game_data['snake']['body'][0], game_data['food'], controller.map_data, game_data['snake']['body'])
                    total_search_time += (pygame.time.get_ticks() - search_start_time) / 1000.0

                    # SỬA LỖI: Lấy đúng các giá trị đếm
                    total_visited_nodes += search_result.get('visited_count', 0)
                    total_generated_nodes += search_result.get('generated_count', 0)
                    
                    # Lấy danh sách các nút đã duyệt để vẽ
                    visited_nodes = search_result.get('visited_nodes', [])
                    ai_path = search_result.get('path', None)
                    
                    if ai_path: 
                        path_nodes_to_draw = ai_path
                        target_food_pos = ai_path[-1]
                        game_state = "VISUALIZING"
                        visualization_timer_start = pygame.time.get_ticks()
                    else:
                        controller.outcome = "Stuck"
                        # Sử dụng kết quả đã tính toán trước để lưu
                        if full_playthrough_result:
                            game_helpers.save_game_result(
                                selected_map_name, selected_mode, game_data['steps'], current_time, 
                                full_playthrough_result['search_time'], "Stuck", 
                                full_playthrough_result['visited'], full_playthrough_result['generated']
                            )
                        else: # Fallback trong trường hợp không có dữ liệu tính trước
                             game_helpers.save_game_result(
                                selected_map_name, selected_mode, game_data['steps'], current_time, 
                                total_search_time, "Stuck", total_visited_nodes, total_generated_nodes
                            )
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
                
                # Sử dụng kết quả đã tính toán trước để lưu
                if full_playthrough_result:
                    game_helpers.save_game_result(
                        selected_map_name, selected_mode, controller.get_state()['steps'],
                        current_time, full_playthrough_result['search_time'], "Completed",
                        full_playthrough_result['visited'], full_playthrough_result['generated']
                    )
                else: # Fallback
                    game_helpers.save_game_result(
                        selected_map_name, selected_mode, controller.get_state()['steps'],
                        current_time, total_search_time, "Completed",
                        total_visited_nodes, total_generated_nodes
                    )
                visited_nodes, path_nodes_to_draw = [], [] # Xóa các chấm visualize khi thắng

        # --- VẼ LÊN MÀN HÌNH ---
        background_effects.draw_background(screen)
        game_surface.fill((0,0,0,0))

        UI_helpers.draw_map(game_surface, controller.map_data)
        if visited_nodes:
            UI_helpers.draw_search_visualization(game_surface, visited_nodes, path_nodes_to_draw)
        UI_helpers.draw_snake(game_surface, game_data['snake'], game_data['food'])
        
        blinking_info = None
        if game_state == "VISUALIZING" and target_food_pos:
            blinking_info = (target_food_pos, is_blinking_visible)
        UI_helpers.draw_food(game_surface, game_data['food'], blinking_info)

        # Vẽ màn hình Game Over nếu cần
        if game_data['outcome'] != "Playing":   
            overlay = pygame.Surface((game_area_width, game_area_height), pygame.SRCALPHA)
            text_to_show = "YOU DIED" if game_data['outcome'] == "Stuck" else "YOU WIN"
            overlay.fill((50, 50, 50, 180) if text_to_show == "YOU DIED" else (0, 80, 150, 180))
            game_surface.blit(overlay, (0, 0))
            UI_helpers.draw_text(text_to_show, end_game_font, config.COLORS['white'], game_surface, game_area_width/2, game_area_height/2)

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
