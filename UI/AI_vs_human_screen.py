# UI/ai_vs_human_screen.py
import pygame
import sys
import config
from UI import UI_helpers
from UI.MainMenu import background_effects
from GameLogic import map_logic, snake_logic, food_logic

def run_ai_vs_human_screen(screen, clock, selected_map_name):
    """Hàm chính để chạy màn hình game AI vs Human."""

    # --- 1. KHỞI TẠO ---
    title_font = pygame.font.Font(config.FONT_PATH, 32)
    info_font = pygame.font.Font(config.FONT_PATH, 22)
    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 200)

    map_width_px = config.DUAL_MAP_WIDTH_TILES * config.TILE_SIZE
    map_height_px = config.DUAL_MAP_HEIGHT_TILES * config.TILE_SIZE
    game_surface_player = pygame.Surface((map_width_px, map_height_px))
    game_surface_ai = pygame.Surface((map_width_px, map_height_px))

    total_content_width = map_width_px * 2 + config.DUAL_CONTROL_PANEL_WIDTH
    start_x = (config.SCREEN_WIDTH - total_content_width) / 2
    player_map_x = start_x
    control_panel_x = player_map_x + map_width_px
    ai_map_x = control_panel_x + config.DUAL_CONTROL_PANEL_WIDTH
    
    map_data = map_logic.load_map_data(selected_map_name)

    # --- 2. QUẢN LÝ TRẠNG THÁI ---
    def reset_game_state():
        player_initial_state = {
            'snake': snake_logic.create_snake_from_map(map_data),
            'food': food_logic.create_food_from_map(map_data),
            'score': 0, 'time': 0.0, 'steps': 0
        }
        player_initial_state['total_food'] = len(player_initial_state['food'])
        return player_initial_state

    player_state = reset_game_state()
    ai_state = {
        'snake': snake_logic.create_snake_from_map(map_data),
        'food': food_logic.create_food_from_map(map_data),
        'score': 0, 'time': 0.0, 'steps': 0
    }
    
    selected_ai_mode = "BFS"
    is_mode_combobox_open = False

    # --- 3. TẠO GIAO DIỆN BẢNG ĐIỀU KHIỂN ---
    panel_center_x = control_panel_x + config.DUAL_CONTROL_PANEL_WIDTH / 2
    buttons = {
        'start': UI_helpers.create_button(panel_center_x - 110, 150, 220, 50, "Start Race"),
        'reset': UI_helpers.create_button(panel_center_x - 110, 220, 220, 50, "Reset"),
        'back': UI_helpers.create_button(panel_center_x - 110, 290, 220, 50, "Back to Menu"),
    }
    mode_combobox = {
        'header': UI_helpers.create_button(panel_center_x - 110, 400, 220, 40, f"AI Mode: {selected_ai_mode}"),
        'options': [UI_helpers.create_button(panel_center_x - 110, 400 + (i + 1) * 45, 220, 45, mode) for i, mode in enumerate(["BFS", "DFS", "A*", "UCS", "Greedy"])]
    }

    def _draw_game_panel(surface, pos_x, title, title_color, state, game_status="playing"):
        UI_helpers.draw_text(title, title_font, title_color, screen, pos_x + map_width_px / 2, title_y)
        surface.fill(config.COLORS['bg'])
        UI_helpers.draw_map(surface, map_data)
        snake_logic.draw_snake(surface, state['snake'])
        food_logic.draw_food(surface, state['food'])
        
        if game_status != "playing":
            overlay = pygame.Surface((map_width_px, map_height_px), pygame.SRCALPHA)
            text_to_show = ""
            if game_status == "dead":
                overlay.fill((50, 50, 50, 180))
                text_to_show = "DEAD"
            elif game_status == "win":
                overlay.fill((0, 80, 150, 180))
                text_to_show = "WIN"
            
            surface.blit(overlay, (0, 0))
            end_font = pygame.font.Font(config.FONT_PATH, 60)
            UI_helpers.draw_text(text_to_show, end_font, config.COLORS['white'], surface, map_width_px / 2, map_height_px / 2)

        screen.blit(surface, (pos_x, map_y))
        
        score_text = f"Score: {state['score']} / {state.get('total_food', 0)}"
        stats_text = f"Time: {state['time']:.2f}s | Steps: {state['steps']}"
        UI_helpers.draw_text(score_text, info_font, config.COLORS['white'], screen, pos_x + map_width_px / 2, stats_y)
        UI_helpers.draw_text(stats_text, info_font, config.COLORS['white'], screen, pos_x + map_width_px / 2, stats_y + 30)

    # --- 4. VÒNG LẶP CHÍNH ---
    running = True
    game_status = "idle"
    last_move_time = 0
    move_interval = 150
    start_time = 0

    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()
        for btn in buttons.values(): UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(mode_combobox['header'], mouse_pos)
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: UI_helpers.update_button_hover_state(btn, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if UI_helpers.handle_button_events(event, buttons['back']): running = False
            if UI_helpers.handle_button_events(event, buttons['start']):
                if game_status == "idle":
                    game_status = "playing"
                    last_move_time = current_time
                    start_time = current_time
            if UI_helpers.handle_button_events(event, buttons['reset']):
                player_state = reset_game_state()
                game_status = "idle"

            if event.type == pygame.KEYDOWN and game_status == "playing":
                current_direction = player_state['snake']['direction']
                if event.key == pygame.K_UP and current_direction != 'DOWN': player_state['snake']['direction'] = 'UP'
                elif event.key == pygame.K_DOWN and current_direction != 'UP': player_state['snake']['direction'] = 'DOWN'
                elif event.key == pygame.K_LEFT and current_direction != 'RIGHT': player_state['snake']['direction'] = 'LEFT'
                elif event.key == pygame.K_RIGHT and current_direction != 'LEFT': player_state['snake']['direction'] = 'RIGHT'
            
            if UI_helpers.handle_button_events(event, mode_combobox['header']): is_mode_combobox_open = not is_mode_combobox_open
            elif is_mode_combobox_open:
                for btn in mode_combobox['options']:
                    if UI_helpers.handle_button_events(event, btn):
                        selected_ai_mode, mode_combobox['header']['text'] = btn['text'], f"AI Mode: {btn['text']}"
                        is_mode_combobox_open = False
                        break
        
        if game_status == "playing":
            # Cập nhật thời gian chơi
            player_state['time'] = (current_time - start_time) / 1000.0

            if current_time - last_move_time > move_interval:
                snake_should_grow = False
                head_after_move = snake_logic.get_next_head_position(player_state['snake'])
                
                eaten_food = None
                for food in player_state['food']:
                    if food['pos'] == head_after_move:
                        eaten_food = food
                        break
                
                if eaten_food:
                    snake_should_grow = True
                    player_state['score'] += 1
                    player_state['food'].remove(eaten_food)
                    if not player_state['food']:
                        game_status = "win"

                snake_logic.move_snake(player_state['snake'], grow=snake_should_grow)
                
                # ### THAY ĐỔI: Tăng bước đếm sau khi di chuyển ###
                player_state['steps'] += 1

                if game_status != "win" and snake_logic.check_collision(player_state['snake'], map_data):
                    game_status = "dead"

                last_move_time = current_time
        
        # --- 5. VẼ LÊN MÀN HÌNH ---
        background_effects.draw_background(screen)
        title_y, map_y = 40, 80
        stats_y = map_y + map_height_px + 40

        player_render_status = "playing" if game_status in ["idle", "playing"] else game_status
        _draw_game_panel(game_surface_player, player_map_x, "PLAYER", config.COLORS['highlight'], player_state, player_render_status)
        _draw_game_panel(game_surface_ai, ai_map_x, "AI", config.COLORS['combo'], ai_state)
        
        for btn_data in buttons.values(): UI_helpers.draw_button(screen, btn_data)
        UI_helpers.draw_button(screen, mode_combobox['header'])
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: UI_helpers.draw_button(screen, btn)
            
        pygame.display.flip()
        clock.tick(config.FPS)