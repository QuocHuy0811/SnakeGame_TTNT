import pygame
import sys
import config
from UI import UI_helpers
from UI.MainMenu import background_effects
from GameLogic import map_logic, snake_logic, food_logic

def run_ai_game(screen, clock, selected_map_name):
    """Hàm chính để chạy màn hình game AI."""

    # --- 1. KHỞI TẠO ---
    panel_font = pygame.font.Font(config.FONT_PATH, 24)
    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 200)

    # Tạo bề mặt (surface) riêng cho khu vực game
    game_area_width = config.MAP_WIDTH_TILES * config.TILE_SIZE
    game_area_height = config.MAP_HEIGHT_TILES * config.TILE_SIZE
    game_surface = pygame.Surface((game_area_width, game_area_height))

    # TÍNH TOÁN VỊ TRÍ CĂN GIỮA CHO KHU VỰC GAME
    game_area_container_width = config.SCREEN_WIDTH - config.PANEL_WIDTH
    game_area_x = (game_area_container_width - game_area_width) / 2
    game_area_y = (config.SCREEN_HEIGHT - game_area_height) / 2

    # Tải dữ liệu map và tạo các đối tượng game
    map_data = map_logic.load_map_data(selected_map_name)
    snake_data = snake_logic.create_snake_from_map(map_data)
    food_data = food_logic.create_food_from_map(map_data)

    # --- 2. QUẢN LÝ TRẠNG THÁI ---
    game_state = "IDLE"
    selected_mode = "BFS"
    is_mode_combobox_open = False
    ai_path = []
    ai_stats = {}
    animation_step = 0
    
    # --- 3. TẠO CÁC THÀNH PHẦN GIAO DIỆN (UI) ---
    panel_x = config.SCREEN_WIDTH - config.PANEL_WIDTH
    panel_center_x = panel_x + config.PANEL_WIDTH / 2
    buttons = {
        'load_snake': UI_helpers.create_button(panel_center_x - 125, 100, 250, 40, "Load Snake"),
        'solve': UI_helpers.create_button(panel_center_x - 125, 150, 250, 40, "Solve"),
        'reset': UI_helpers.create_button(panel_center_x - 125, 200, 250, 40, "Reset"),
        'history': UI_helpers.create_button(panel_center_x - 125, 250, 250, 40, "History"),
        'back_to_menu': UI_helpers.create_button(panel_center_x - 125, 300, 250, 40, "Back to Menu"),
        'skip': UI_helpers.create_button(panel_center_x - 125, 350, 250, 40, "Skip Animation")
    }
    mode_combobox = {
        'header': UI_helpers.create_button(panel_center_x - 125, 400, 250, 40, f"Mode: {selected_mode}"),
        'options': [UI_helpers.create_button(panel_center_x - 125, 440 + i*45, 250, 45, mode) for i, mode in enumerate(["Player", "BFS", "DFS", "A*", "UCS", "Greedy"])]
    }

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
            if event.type == pygame.QUIT:
                running = False
            
            if UI_helpers.handle_button_events(event, buttons['back_to_menu']):
                running = False

            if UI_helpers.handle_button_events(event, buttons['reset']):
                snake_data = snake_logic.create_snake_from_map(map_data)
                food_data = food_logic.create_food_from_map(map_data)
                game_state = "IDLE"
                ai_path = []
                ai_stats = {}
                animation_step = 0
            
            if UI_helpers.handle_button_events(event, buttons['solve']) and selected_mode != "Player":
                game_state = "SOLVING"

            if UI_helpers.handle_button_events(event, mode_combobox['header']):
                is_mode_combobox_open = not is_mode_combobox_open
            elif is_mode_combobox_open:
                for btn in mode_combobox['options']:
                    if UI_helpers.handle_button_events(event, btn):
                        selected_mode = btn['text']
                        mode_combobox['header']['text'] = f"Mode: {selected_mode}"
                        is_mode_combobox_open = False
                        break
        
        # --- 5. VẼ LÊN MÀN HÌNH ---
        background_effects.draw_background(screen)

        # Vẽ các thành phần của game (map, rắn, thức ăn) LÊN BỀ MẶT RIÊNG
        game_surface.fill(config.COLORS['bg']) 
        UI_helpers.draw_map(game_surface, map_data)
        snake_logic.draw_snake(game_surface, snake_data)
        food_logic.draw_food(game_surface, food_data)
        
        # Đặt bề mặt game vào vị trí đã được tính toán để CĂN GIỮA
        screen.blit(game_surface, (game_area_x, game_area_y))
        
        # Vẽ bảng điều khiển
        panel_rect = pygame.Rect(panel_x, 0, config.PANEL_WIDTH, config.SCREEN_HEIGHT)
        pygame.draw.rect(screen, config.COLORS['white_bg'], panel_rect, border_radius=20)
        
        # Vẽ các nút và văn bản lên trên
        UI_helpers.draw_text("Control Panel", panel_font, config.COLORS['text_dark'], screen, panel_center_x, 50)
        UI_helpers.draw_button(screen, buttons['load_snake'])
        UI_helpers.draw_button(screen, buttons['solve'])
        UI_helpers.draw_button(screen, buttons['reset'])
        UI_helpers.draw_button(screen, buttons['history'])
        UI_helpers.draw_button(screen, buttons['back_to_menu'])
        
        UI_helpers.draw_button(screen, mode_combobox['header'])
        if is_mode_combobox_open:
            for btn in mode_combobox['options']: 
                UI_helpers.draw_button(screen, btn)

        pygame.display.flip()
        clock.tick(config.FPS)