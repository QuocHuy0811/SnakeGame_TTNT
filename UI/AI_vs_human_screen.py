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
    # Fonts
    title_font = pygame.font.Font(config.FONT_PATH, 32)
    info_font = pygame.font.Font(config.FONT_PATH, 22)

    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 200)

    # Kích thước và bề mặt
    map_width_px = config.DUAL_MAP_WIDTH_TILES * config.TILE_SIZE
    map_height_px = config.DUAL_MAP_HEIGHT_TILES * config.TILE_SIZE
    game_surface_player = pygame.Surface((map_width_px, map_height_px))
    game_surface_ai = pygame.Surface((map_width_px, map_height_px))

    # Tính toán vị trí
    total_content_width = map_width_px * 2 + config.DUAL_CONTROL_PANEL_WIDTH
    start_x = (config.SCREEN_WIDTH - total_content_width) / 2
    player_map_x = start_x
    control_panel_x = player_map_x + map_width_px
    ai_map_x = control_panel_x + config.DUAL_CONTROL_PANEL_WIDTH
    
    # Tải dữ liệu map
    map_data = map_logic.load_map_data(selected_map_name)

    # --- 2. QUẢN LÝ TRẠNG THÁI ---
    player_state = {
        'snake': snake_logic.create_snake_from_map(map_data),
        'food': food_logic.create_food_from_map(map_data),
        'score': 0, 'time': 0.0, 'steps': 0
    }
    ai_state = {
        'snake': snake_logic.create_snake_from_map(map_data),
        'food': food_logic.create_food_from_map(map_data),
        'score': 0, 'time': 0.0, 'steps': 0
    }
    score_to_win = 8
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

    # --- HÀM VẼ PHỤ TRỢ (được định nghĩa bên trong để gọn hơn) ---
    def _draw_game_panel(surface, pos_x, title, title_color, state):
        # 1. Vẽ tiêu đề
        UI_helpers.draw_text(title, title_font, title_color, screen, pos_x + map_width_px / 2, title_y)
        
        # 2. Chuẩn bị bề mặt game
        surface.fill(config.COLORS['bg'])
        UI_helpers.draw_map(surface, map_data)
        snake_logic.draw_snake(surface, state['snake'])
        food_logic.draw_food(surface, state['food'])
        screen.blit(surface, (pos_x, map_y))

        # 3. Vẽ thông tin bên dưới
        score_text = f"Score: {state['score']} / {score_to_win}"
        stats_text = f"Time: {state['time']:.2f}s | Steps: {state['steps']}"
        UI_helpers.draw_text(score_text, info_font, config.COLORS['white'], screen, pos_x + map_width_px / 2, stats_y)
        UI_helpers.draw_text(stats_text, info_font, config.COLORS['white'], screen, pos_x + map_width_px / 2, stats_y + 30)

    # --- 4. VÒNG LẶP CHÍNH ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        # Cập nhật hover
        for btn in buttons.values(): UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(mode_combobox['header'], mouse_pos)
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: UI_helpers.update_button_hover_state(btn, mouse_pos)

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if UI_helpers.handle_button_events(event, buttons['back']): running = False
            
            if UI_helpers.handle_button_events(event, mode_combobox['header']):
                is_mode_combobox_open = not is_mode_combobox_open
            elif is_mode_combobox_open:
                for btn in mode_combobox['options']:
                    if UI_helpers.handle_button_events(event, btn):
                        selected_ai_mode = btn['text']
                        mode_combobox['header']['text'] = f"AI Mode: {selected_ai_mode}"
                        is_mode_combobox_open = False
                        break

        # --- 5. VẼ LÊN MÀN HÌNH ---
        background_effects.draw_background(screen)

        # Định vị các thành phần theo chiều dọc
        title_y = 40
        map_y = 80
        stats_y = map_y + map_height_px + 40

        # Sử dụng hàm vẽ phụ trợ
        _draw_game_panel(game_surface_player, player_map_x, "PLAYER", config.COLORS['highlight'], player_state)
        _draw_game_panel(game_surface_ai, ai_map_x, "AI", config.COLORS['combo'], ai_state)
        
        # Vẽ Cột Giữa (Bảng điều khiển)
        for btn_data in buttons.values():
            UI_helpers.draw_button(screen, btn_data)
        
        UI_helpers.draw_button(screen, mode_combobox['header'])
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: 
                UI_helpers.draw_button(screen, btn)
            
        pygame.display.flip()
        clock.tick(config.FPS)