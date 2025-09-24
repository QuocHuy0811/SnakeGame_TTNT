import pygame
import config
from UI import UI_helpers, AI_selection_screen
from UI.MainMenu import background_effects
from GameLogic.game_controller import GameController # <-- DÙNG GAMECONTROLLER
from GameLogic import snake_logic, food_logic
from Algorithms import BFS, Astar, UCS, DFS, Greedy # (Giả định AI cũng dùng các thuật toán này)

def find_path_for_ai(controller, selected_mode):
    """Hàm tìm đường đi cho AI dựa vào thuật toán được chọn."""
    game_data = controller.get_state()
     # Kiểm tra xem rắn có thân không
    if not game_data['snake']['body']: return None
    start_pos = game_data['snake']['body'][0]
    food_positions = [food['pos'] for food in game_data['food']]
    
    # Map để tra cứu hàm thuật toán tương ứng
    algorithm_map = {
        "BFS": BFS.find_path_bfs, "A*": Astar.find_path_astar,
        "UCS": UCS.find_path_ucs, "DFS": DFS.find_path_dfs,
        "Greedy": Greedy.find_path_greedy
    }
    algorithm_to_run = algorithm_map.get(selected_mode)
    if not algorithm_to_run:
        return None # Nếu không tìm thấy thuật toán, trả về None

    # Các thuật toán giờ trả về dictionary, ta cần lấy ra 'path'
    result = algorithm_to_run(start_pos, food_positions, controller.map_data, game_data['snake']['body'])
    return result.get('path')

def run_ai_vs_human_screen(screen, clock, selected_map_name):
    """Hàm chính để chạy màn hình game AI vs Human."""
    # --- 1. KHỞI TẠO ---
    title_font = pygame.font.Font(config.FONT_PATH, 32)
    info_font = pygame.font.Font(config.FONT_PATH, 22)
    end_font = pygame.font.Font(config.FONT_PATH, 60)
    
    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 1000)

    # Tạo 2 controller riêng biệt cho Player và AI
    player_controller = GameController(selected_map_name)
    ai_controller = GameController(selected_map_name)
    
    map_width_px = config.DUAL_MAP_WIDTH_TILES * config.TILE_SIZE
    map_height_px = config.DUAL_MAP_HEIGHT_TILES * config.TILE_SIZE
    game_surface_player = pygame.Surface((map_width_px, map_height_px))
    game_surface_ai = pygame.Surface((map_width_px, map_height_px))

    # --- 2. QUẢN LÝ TRẠNG THÁI GIAO DIỆN ---
    game_status = "IDLE" # Các trạng thái: IDLE, playing, game_over
    player_time = 0.0
    ai_time = 0.0
    ai_path = []
    ai_animation_step = 0
    last_move_time = 0
    move_interval = 150 # Nhịp game

    selected_ai_mode = "BFS"

    # --- 3. GIAO DIỆN BẢNG ĐIỀU KHIỂN ---
    total_content_width = map_width_px * 2 + config.DUAL_CONTROL_PANEL_WIDTH
    start_x = (config.SCREEN_WIDTH - total_content_width) / 2
    player_map_x = start_x
    control_panel_x = player_map_x + map_width_px
    ai_map_x = control_panel_x + config.DUAL_CONTROL_PANEL_WIDTH
    panel_center_x = control_panel_x + config.DUAL_CONTROL_PANEL_WIDTH / 2
    
    buttons = {
        'start': UI_helpers.create_button(panel_center_x - 110, 150, 220, 50, "Start Race"),
        'reset': UI_helpers.create_button(panel_center_x - 110, 220, 220, 50, "Reset"),
        'back': UI_helpers.create_button(panel_center_x - 110, 290, 220, 50, "Back to Menu"),
        'change_mode': UI_helpers.create_button(panel_center_x - 110, 400, 220, 40, f"AI Mode: {selected_ai_mode}")
    }
    
    def _draw_game_panel(surface, pos_x, title, title_color, controller, time):
        """Hàm vẽ một khu vực chơi game, sử dụng controller."""
        game_data = controller.get_state()
        UI_helpers.draw_text(title, title_font, title_color, screen, pos_x + map_width_px / 2, 40)
        surface.fill(config.COLORS['bg'])
        UI_helpers.draw_map(surface, controller.map_data)
        snake_logic.draw_snake(surface, game_data['snake'])
        food_logic.draw_food(surface, game_data['food'])
        
        if game_data['outcome'] != "Playing":
            overlay = pygame.Surface((map_width_px, map_height_px), pygame.SRCALPHA)
            text_to_show = "YOU DIED" if game_data['outcome'] == "Stuck" else "YOU WIN"
            overlay.fill((50, 50, 50, 180) if text_to_show == "YOU DIED" else (0, 80, 150, 180))
            surface.blit(overlay, (0, 0))
            UI_helpers.draw_text(text_to_show, end_font, config.COLORS['white'], surface, map_width_px/2, map_height_px/2)

        screen.blit(surface, (pos_x, 80))
        
        total_food = len(controller.map_data['food_start'])
        score = total_food - len(game_data['food'])
        stats_y = 80 + map_height_px + 40
        UI_helpers.draw_text(f"Score: {score} / {total_food}", info_font, config.COLORS['white'], screen, pos_x + map_width_px/2, stats_y)
        UI_helpers.draw_text(f"Time: {time:.2f}s | Steps: {game_data['steps']}", info_font, config.COLORS['white'], screen, pos_x + map_width_px/2, stats_y + 30)

    # --- 4. VÒNG LẶP CHÍNH ---
    running = True
    start_time = 0
    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_ticks = pygame.time.get_ticks()
        
        for btn in buttons.values(): 
            UI_helpers.update_button_hover_state(btn, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
                
            if UI_helpers.handle_button_events(event, buttons['back']): 
                running = False

            if UI_helpers.handle_button_events(event, buttons['change_mode']):
                new_mode = AI_selection_screen.run_algorithm_selection(screen)
                if new_mode is not None and new_mode != "Player": # Bỏ qua lựa chọn "Player"
                    selected_ai_mode = new_mode
                    buttons['change_mode']['text'] = f"AI Mode: {selected_ai_mode}"
            
            if UI_helpers.handle_button_events(event, buttons['start']) and game_status == "IDLE":
                game_status = "playing"
                start_time = current_ticks
                last_move_time = current_ticks
                ai_path = find_path_for_ai(ai_controller, selected_ai_mode)
                ai_animation_step = 1

            if UI_helpers.handle_button_events(event, buttons['reset']):
                player_controller.reset()
                ai_controller.reset()
                game_status = "IDLE"
                player_time = 0.0
                ai_time = 0.0

            # Xử lý input cho người chơi
            if event.type == pygame.KEYDOWN and game_status == "playing":
                if event.key == pygame.K_UP: player_controller.set_direction('UP')
                elif event.key == pygame.K_DOWN: player_controller.set_direction('DOWN')
                elif event.key == pygame.K_LEFT: player_controller.set_direction('LEFT')
                elif event.key == pygame.K_RIGHT: player_controller.set_direction('RIGHT')
        
        # --- CẬP NHẬT LOGIC GAME ---
        if game_status == "playing":
            # Cập nhật thời gian cho cả hai
            if player_controller.get_state()['outcome'] == "Playing": 
                player_time = (current_ticks - start_time) / 1000.0
            if ai_controller.get_state()['outcome'] == "Playing": 
                ai_time = (current_ticks - start_time) / 1000.0

            if current_ticks - last_move_time > move_interval:
                # Cập nhật trạng thái của người chơi
                player_controller.update()
                
                # Cập nhật trạng thái của AI
                if ai_path and ai_animation_step < len(ai_path):
                    next_pos = ai_path[ai_animation_step]
                    ai_controller.update_by_path_step(next_pos)
                    ai_animation_step += 1

                    # Kiểm tra xem AI có vừa ăn mồi không để tìm đường mới
                    is_food_eaten = True
                    for food in ai_controller.get_state()['food']:
                        if food['pos'] == next_pos:
                            is_food_eaten = False
                            break
                    # Nếu AI đã đến ô thức ăn (ô đó không còn trong list food) hoặc hết đường đi
                    if is_food_eaten or ai_animation_step >= len(ai_path):
                        ai_path = find_path_for_ai(ai_controller, selected_ai_mode)
                        ai_animation_step = 1 # Reset bước đi

                last_move_time = current_ticks
            
            if player_controller.get_state()['outcome'] != "Playing" or ai_controller.get_state()['outcome'] != "Playing":
                game_status = "game_over"

        # --- 5. VẼ LÊN MÀN HÌNH ---
        screen.fill(config.COLORS['bg'])
        _draw_game_panel(game_surface_player, player_map_x, "PLAYER", config.COLORS['highlight'], player_controller, player_time)
        _draw_game_panel(game_surface_ai, ai_map_x, "AI", config.COLORS['combo'], ai_controller, ai_time)
        for btn_data in buttons.values(): 
            UI_helpers.draw_button(screen, btn_data)
        
        pygame.display.flip()
        clock.tick(config.FPS)