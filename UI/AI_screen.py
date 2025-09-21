# UI/AI_screen.py
import pygame
import config
from UI import UI_helpers
from UI.MainMenu import background_effects
# V-- CẬP NHẬT: THÊM LẠI CÁC IMPORT BỊ THIẾU --V
from GameLogic import game_helpers, snake_logic, food_logic
from GameLogic.game_controller import GameController 
# A---------------------------------------------A
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

def run_ai_game(screen, clock, selected_map_name):
    # --- 1. KHỞI TẠO ---
    panel_font = pygame.font.Font(config.FONT_PATH, 24); info_font_bold = pygame.font.Font(config.FONT_PATH, 32); info_font = pygame.font.Font(config.FONT_PATH, 26)
    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 200)
    
    controller = GameController(selected_map_name)

    # --- 2. QUẢN LÝ TRẠNG THÁI GIAO DIỆN ---
    game_state, selected_mode = "IDLE", "BFS"; is_mode_combobox_open = False
    ai_path, animation_step, last_animation_time, animation_interval = [], 0, 0, 80
    current_time, total_search_time = 0.0, 0.0

    # --- 3. TẠO CÁC THÀNH PHẦN GIAO DIỆN (UI) ---
    panel_x = config.SCREEN_WIDTH - config.AI_PANEL_WIDTH; panel_center_x = panel_x + config.AI_PANEL_WIDTH / 2
    buttons = { 'solve': UI_helpers.create_button(panel_center_x - 125, 150, 250, 40, "Solve"), 'reset': UI_helpers.create_button(panel_center_x - 125, 200, 250, 40, "Reset"), 'history': UI_helpers.create_button(panel_center_x - 125, 250, 250, 40, "History"), 'back_to_menu': UI_helpers.create_button(panel_center_x - 125, 300, 250, 40, "Back to Menu")}
    mode_combobox = {'header': UI_helpers.create_button(panel_center_x - 125, 350, 250, 40, f"Mode: {selected_mode}"),'options': [UI_helpers.create_button(panel_center_x - 125, 350 + (i + 1) * 45, 250, 35, mode) for i, mode in enumerate(["BFS", "DFS", "A*", "UCS", "Greedy"])]}
    
    running = True
    while running:
        game_data = controller.get_state()
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons.values(): UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(mode_combobox['header'], mouse_pos)
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: UI_helpers.update_button_hover_state(btn, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if UI_helpers.handle_button_events(event, buttons['back_to_menu']): running = False
            if UI_helpers.handle_button_events(event, buttons['reset']):
                controller.reset()
                game_state, ai_path, animation_step = "IDLE", [], 0
                current_time, total_search_time = 0.0, 0.0
            if UI_helpers.handle_button_events(event, buttons['solve']) and game_state == "IDLE":
                game_state, current_time, total_search_time = "AI_AUTOPLAY", 0.0, 0.0
            if UI_helpers.handle_button_events(event, buttons['history']):
                history_screen.run_history_screen(screen, clock)
            if UI_helpers.handle_button_events(event, mode_combobox['header']): is_mode_combobox_open = not is_mode_combobox_open
            elif is_mode_combobox_open:
                for btn in mode_combobox['options']:
                    if UI_helpers.handle_button_events(event, btn):
                        selected_mode, mode_combobox['header']['text'] = btn['text'], f"Mode: {selected_mode}"; is_mode_combobox_open = False; break

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

        # --- VẼ LÊN MÀN HÌNH ---
        current_time = game_data['steps'] * (animation_interval / 1000.0)
        
        game_surface = pygame.Surface((config.AI_MAP_WIDTH_TILES * config.TILE_SIZE, config.AI_MAP_HEIGHT_TILES * config.TILE_SIZE))
        game_area_y = (config.SCREEN_HEIGHT - game_surface.get_height()) / 2
        game_area_x = game_area_y
        background_effects.draw_background(screen)
        game_surface.fill(config.COLORS['bg'])
        UI_helpers.draw_map(game_surface, controller.map_data)
        snake_logic.draw_snake(game_surface, game_data['snake'])
        food_logic.draw_food(game_surface, game_data['food'])
        screen.blit(game_surface, (game_area_x, game_area_y))
        
        middle_area_center_x = game_area_x + game_surface.get_width() + (panel_x - (game_area_x + game_surface.get_width())) / 2
        
        UI_helpers.draw_text("ANIMATION TIME", info_font, config.COLORS['title'], screen, middle_area_center_x, 150); UI_helpers.draw_text(f"{current_time:.4f} s", info_font_bold, config.COLORS['white'], screen, middle_area_center_x, 190)
        UI_helpers.draw_text("STEPS", info_font, config.COLORS['title'], screen, middle_area_center_x, 260); UI_helpers.draw_text(str(game_data['steps']), info_font_bold, config.COLORS['white'], screen, middle_area_center_x, 300)
        UI_helpers.draw_text("SEARCH TIME", info_font, config.COLORS['title'], screen, middle_area_center_x, 370); UI_helpers.draw_text(f"{total_search_time:.4f} s", info_font_bold, config.COLORS['white'], screen, middle_area_center_x, 410)

        panel_rect = pygame.Rect(panel_x, 0, config.AI_PANEL_WIDTH, config.SCREEN_HEIGHT); pygame.draw.rect(screen, config.COLORS['white_bg'], panel_rect, border_radius=20)
        UI_helpers.draw_text("Control Panel", panel_font, config.COLORS['text_dark'], screen, panel_center_x, 50)
        for btn_data in buttons.values(): UI_helpers.draw_button(screen, btn_data)
        UI_helpers.draw_button(screen, mode_combobox['header'])
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: UI_helpers.draw_button(screen, btn)
        
        pygame.display.flip(); clock.tick(config.FPS)