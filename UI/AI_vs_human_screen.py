import time 
from functools import partial
import pygame
from Algorithms.algorithm_helpers import manhattan_distance, euclidean_distance
import config
from UI import UI_helpers, AI_selection_screen
from UI.MainMenu import background_effects
from GameLogic.game_controller import GameController
from Algorithms import BFS, Astar, UCS, DFS, Greedy, IDS, OnlineSearch, BeamSearch, HillClimbing

def find_path_for_ai(controller, selected_mode):
    """Hàm tìm đường đi cho AI, trả về toàn bộ kết quả tìm kiếm."""
    game_data = controller.get_state()
    if not game_data['snake']['body']: return {}
    
    if selected_mode == "OnlineSearch":
        return {'move': OnlineSearch.find_best_next_move(game_data['snake'], game_data['food'], controller.map_data).get('move')}
    
    start_pos = game_data['snake']['body'][0]
    food_positions = [food['pos'] for food in game_data['food']]
    
    algorithm_map = {
        "BFS": BFS.find_path_bfs, "DFS": DFS.find_path_dfs, "IDS": IDS.find_path_ids, "UCS": UCS.find_path_ucs,
        "HillClimbing": HillClimbing.find_path_hill_climbing, "BeamSearch": BeamSearch.find_path_beam_search,
        "A* (Manhattan)": partial(Astar.find_path_astar, heuristic_func=manhattan_distance),
        "A* (Euclidean)": partial(Astar.find_path_astar, heuristic_func=euclidean_distance),
        "Greedy (Manhattan)": partial(Greedy.find_path_greedy, heuristic_func=manhattan_distance),
        "Greedy (Euclidean)": partial(Greedy.find_path_greedy, heuristic_func=euclidean_distance)
    }
    algorithm_to_run = algorithm_map.get(selected_mode)
    return algorithm_to_run(start_pos, food_positions, controller.map_data, game_data['snake']['body']) if algorithm_to_run else {}

def run_ai_vs_human_screen(screen, clock, selected_map_name):
    """Hàm chính để chạy màn hình game AI vs Human."""
    # --- KHỞI TẠO ---
    title_font = pygame.font.Font(config.FONT_PATH, 32)
    info_font = pygame.font.Font(config.FONT_PATH, 22)
    end_font = pygame.font.Font(config.FONT_PATH, 60)
    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 1000)

    player1_controller = GameController(selected_map_name)
    player2_controller = GameController(selected_map_name)
    
    map_width_px = config.DUAL_MAP_WIDTH_TILES * config.TILE_SIZE
    map_height_px = config.DUAL_MAP_HEIGHT_TILES * config.TILE_SIZE
    game_surface_player = pygame.Surface((map_width_px, map_height_px))
    game_surface_ai = pygame.Surface((map_width_px, map_height_px))

    # --- QUẢN LÝ TRẠNG THÁI ---
    game_status, player1_time, player2_time, last_move_time = "IDLE", 0.0, 0.0, 0
    move_interval = 200
    player1_mode, player2_mode = "Player", "BFS"
    p1_ai_path, p2_ai_path, p1_visited_nodes, p2_visited_nodes = [], [], [], []
    p1_final_results, p2_final_results = None, None
    is_ai_vs_ai_race, show_comparison_panel = False, False
    
    # Biến tích lũy thông số
    p1_total_search, p2_total_search = 0.0, 0.0
    p1_total_visited, p2_total_visited = 0, 0
    p1_total_generated, p2_total_generated = 0, 0

    # --- GIAO DIỆN ---
    total_content_width = map_width_px * 2 + config.DUAL_CONTROL_PANEL_WIDTH
    start_x = (config.SCREEN_WIDTH - total_content_width) / 2
    player_map_x, control_panel_x = start_x, start_x + map_width_px
    ai_map_x, panel_center_x = control_panel_x + config.DUAL_CONTROL_PANEL_WIDTH, control_panel_x + config.DUAL_CONTROL_PANEL_WIDTH / 2
    
    buttons = { 'start': UI_helpers.create_button(panel_center_x - 110, 150, 220, 50, "Start Race"),
                'reset': UI_helpers.create_button(panel_center_x - 110, 220, 220, 50, "Reset"),
                'back': UI_helpers.create_button(panel_center_x - 110, 290, 220, 50, "Back to Menu"),
                'change_mode_p1': UI_helpers.create_button(panel_center_x - 110, 400, 220, 40, f"P1: {player1_mode}"),
                'change_mode_p2': UI_helpers.create_button(panel_center_x - 110, 450, 220, 40, f"P2: {player2_mode}") }
    
    # Tạo nút X cho bảng so sánh (sẽ được định vị lại sau)
    close_button = UI_helpers.create_button(0, 0, 40, 40, "X")

    # --- HÀM VẼ ---
    def _draw_game_panel(surface, pos_x, title, title_color, controller, time, visited_nodes, path_nodes):
        # ... (Nội dung hàm này giữ nguyên như cũ)
        game_data = controller.get_state()
        UI_helpers.draw_text(title, title_font, title_color, screen, pos_x + map_width_px / 2, 40)
        surface.fill(config.COLORS['bg'])
        UI_helpers.draw_map(surface, controller.map_data)
        if visited_nodes: UI_helpers.draw_search_visualization(surface, visited_nodes, path_nodes)
        UI_helpers.draw_snake(surface, game_data['snake'], game_data['food'])
        UI_helpers.draw_food(surface, game_data['food'])
        if game_data['outcome'] != "Playing":
            overlay = pygame.Surface((map_width_px, map_height_px), pygame.SRCALPHA)
            text, color = ("COMPLETED", (0, 80, 150, 180)) if game_data['outcome'] == "Completed" else ("STUCK", (50, 50, 50, 180))
            overlay.fill(color); surface.blit(overlay, (0, 0))
            UI_helpers.draw_text(text, end_font, config.COLORS['white'], surface, map_width_px/2, map_height_px/2)
        screen.blit(surface, (pos_x, 80))
        total_food = len(controller.map_data.get('food_sequence', []))
        score = controller.current_food_index
        stats_y = 80 + map_height_px + 40
        UI_helpers.draw_text(f"Score: {score}/{total_food}", info_font, config.COLORS['white'], screen, pos_x + map_width_px/2, stats_y)
        UI_helpers.draw_text(f"Time: {time:.2f}s | Steps: {game_data['steps']}", info_font, config.COLORS['white'], screen, pos_x + map_width_px/2, stats_y + 30)

    def _draw_comparison_panel(p1_res, p2_res):
        popup_width, popup_height = 600, 480 # Tăng kích thước
        popup_x, popup_y = (config.SCREEN_WIDTH - popup_width) / 2, (config.SCREEN_HEIGHT - popup_height) / 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, config.COLORS['white_bg'], popup_rect, border_radius=20)
        
        # Cập nhật vị trí nút X và vẽ nó
        close_button['rect'].topright = (popup_rect.right - 10, popup_rect.top + 10)
        UI_helpers.draw_button(screen, close_button)

        UI_helpers.draw_text("Race Results", title_font, config.COLORS['text_dark'], screen, popup_rect.centerx, popup_y + 40)
        
        col_stats_x, col_p1_x, col_p2_x = popup_rect.centerx, popup_x + popup_width * 0.28, popup_x + popup_width * 0.72
        header_font = pygame.font.Font(config.FONT_PATH, 24)
        UI_helpers.draw_text(f"P1: {p1_res['mode']}", header_font, config.COLORS['highlight'], screen, col_p1_x, popup_y + 90)
        UI_helpers.draw_text(f"P2: {p2_res['mode']}", header_font, config.COLORS['combo'], screen, col_p2_x, popup_y + 90)
        
        # Thêm các thông số mới
        stats = ["Outcome", "Steps", "Ani. Time (s)", "Search Time (s)", "Visited", "Generated"]
        p1_data = [p1_res['outcome'], p1_res['steps'], f"{p1_res['time']:.2f}", f"{p1_res['search_time']:.4f}", p1_res['visited'], p1_res['generated']]
        p2_data = [p2_res['outcome'], p2_res['steps'], f"{p2_res['time']:.2f}", f"{p2_res['search_time']:.4f}", p2_res['visited'], p2_res['generated']]
        
        item_font = pygame.font.Font(config.FONT_PATH, 22)
        for i, stat_name in enumerate(stats):
            y_pos = popup_y + 150 + i * 50
            UI_helpers.draw_text(stat_name, item_font, config.COLORS['text_dark'], screen, col_stats_x, y_pos)
            UI_helpers.draw_text(str(p1_data[i]), item_font, config.COLORS['text_dark'], screen, col_p1_x, y_pos)
            UI_helpers.draw_text(str(p2_data[i]), item_font, config.COLORS['text_dark'], screen, col_p2_x, y_pos)

    # --- VÒNG LẶP CHÍNH ---
    running = True
    start_time = 0
    p1_animation_step, p2_animation_step = 1, 1

    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_ticks = pygame.time.get_ticks()
        
        for btn in buttons.values(): UI_helpers.update_button_hover_state(btn, mouse_pos)
        if show_comparison_panel: UI_helpers.update_button_hover_state(close_button, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if UI_helpers.handle_button_events(event, buttons['back']): running = False

            if UI_helpers.handle_button_events(event, buttons['change_mode_p1']): #... (giữ nguyên)
                new_mode = AI_selection_screen.run_algorithm_selection(screen)
                if new_mode is not None: player1_mode = new_mode; buttons['change_mode_p1']['text'] = f"P1: {player1_mode}"
            if UI_helpers.handle_button_events(event, buttons['change_mode_p2']): #... (giữ nguyên)
                new_mode = AI_selection_screen.run_algorithm_selection(screen)
                if new_mode is not None: player2_mode = new_mode; buttons['change_mode_p2']['text'] = f"P2: {player2_mode}"

            if UI_helpers.handle_button_events(event, buttons['start']) and game_status == "IDLE":
                game_status, start_time, last_move_time = "playing", current_ticks, current_ticks
                is_ai_vs_ai_race = (player1_mode != "Player" and player2_mode != "Player")

            if UI_helpers.handle_button_events(event, buttons['reset']):
                player1_controller.reset(); player2_controller.reset()
                game_status, player1_time, player2_time = "IDLE", 0.0, 0.0
                p1_ai_path, p2_ai_path, p1_visited_nodes, p2_visited_nodes = [], [], [], []
                p1_final_results, p2_final_results, is_ai_vs_ai_race, show_comparison_panel = None, None, False, False
                p1_total_search, p2_total_search, p1_total_visited, p2_total_visited, p1_total_generated, p2_total_generated = 0.0, 0.0, 0, 0, 0, 0

            if UI_helpers.handle_button_events(event, close_button) and show_comparison_panel:
                show_comparison_panel = False # Đóng bảng so sánh

            if event.type == pygame.KEYDOWN and game_status == "playing": #... (giữ nguyên)
                if player1_mode == "Player":
                    if event.key == pygame.K_w: player1_controller.set_direction('UP')
                    elif event.key == pygame.K_s: player1_controller.set_direction('DOWN')
                    elif event.key == pygame.K_a: player1_controller.set_direction('LEFT')
                    elif event.key == pygame.K_d: player1_controller.set_direction('RIGHT')
                if player2_mode == "Player":
                    if event.key == pygame.K_UP: player2_controller.set_direction('UP')
                    elif event.key == pygame.K_DOWN: player2_controller.set_direction('DOWN')
                    elif event.key == pygame.K_LEFT: player2_controller.set_direction('LEFT')
                    elif event.key == pygame.K_RIGHT: player2_controller.set_direction('RIGHT')
        
        # --- CẬP NHẬT LOGIC GAME ---
        if game_status == "playing":
            if player1_controller.get_state()['outcome'] == "Playing": player1_time = (current_ticks - start_time) / 1000.0
            if player2_controller.get_state()['outcome'] == "Playing": player2_time = (current_ticks - start_time) / 1000.0

            if current_ticks - last_move_time > move_interval:
                if player1_controller.get_state()['outcome'] == "Playing":
                    if player1_mode == "Player": 
                        player1_controller.update()
                    # --- START CORRECTION FOR PLAYER 1 ---
                    elif player1_mode == "OnlineSearch":
                        search_start = time.perf_counter()
                        search_result = find_path_for_ai(player1_controller, player1_mode)
                        p1_total_search += time.perf_counter() - search_start
                        
                        next_move = search_result.get('move')
                        if next_move:
                            player1_controller.set_direction(next_move)
                            player1_controller.update()
                        else:
                            player1_controller.outcome = "Stuck"
                    else: # Logic for all other path-based algorithms
                        if not p1_ai_path:
                            search_start = time.perf_counter(); search_result = find_path_for_ai(player1_controller, player1_mode); p1_total_search += time.perf_counter() - search_start
                            p1_ai_path, p1_visited_nodes = search_result.get('path'), search_result.get('visited_nodes', [])
                            p1_total_visited += search_result.get('visited_count', 0); p1_total_generated += search_result.get('generated_count', 0)
                            p1_animation_step = 1
                        if p1_ai_path and p1_animation_step < len(p1_ai_path): player1_controller.update_by_path_step(p1_ai_path[p1_animation_step]); p1_animation_step += 1
                        if p1_ai_path and p1_animation_step >= len(p1_ai_path): p1_ai_path, p1_visited_nodes = [], []
                    # --- END CORRECTION FOR PLAYER 1 ---
                
                if player2_controller.get_state()['outcome'] == "Playing":
                    if player2_mode == "Player": 
                        player2_controller.update()
                    # --- START CORRECTION FOR PLAYER 2 ---
                    elif player2_mode == "OnlineSearch":
                        search_start = time.perf_counter()
                        search_result = find_path_for_ai(player2_controller, player2_mode)
                        p2_total_search += time.perf_counter() - search_start
                        
                        next_move = search_result.get('move')
                        if next_move:
                            player2_controller.set_direction(next_move)
                            player2_controller.update()
                        else:
                            player2_controller.outcome = "Stuck"
                    else: # Logic for all other path-based algorithms
                        if not p2_ai_path:
                            search_start = time.perf_counter(); search_result = find_path_for_ai(player2_controller, player2_mode); p2_total_search += time.perf_counter() - search_start
                            p2_ai_path, p2_visited_nodes = search_result.get('path'), search_result.get('visited_nodes', [])
                            p2_total_visited += search_result.get('visited_count', 0); p2_total_generated += search_result.get('generated_count', 0)
                            p2_animation_step = 1
                        if p2_ai_path and p2_animation_step < len(p2_ai_path): player2_controller.update_by_path_step(p2_ai_path[p2_animation_step]); p2_animation_step += 1
                        if p2_ai_path and p2_animation_step >= len(p2_ai_path): p2_ai_path, p2_visited_nodes = [], []
                    # --- END CORRECTION FOR PLAYER 2 ---
                last_move_time = current_ticks

            # --- LOGIC KẾT THÚC GAME ---
            p1_state, p2_state = player1_controller.get_state(), player2_controller.get_state()
            if p1_state['outcome'] != "Playing" and p1_final_results is None:
                p1_final_results = {'outcome': p1_state['outcome'], 'steps': p1_state['steps'], 'time': player1_time, 'mode': player1_mode,
                                    'search_time': p1_total_search, 'visited': p1_total_visited, 'generated': p1_total_generated}
            if p2_state['outcome'] != "Playing" and p2_final_results is None:
                p2_final_results = {'outcome': p2_state['outcome'], 'steps': p2_state['steps'], 'time': player2_time, 'mode': player2_mode,
                                    'search_time': p2_total_search, 'visited': p2_total_visited, 'generated': p2_total_generated}
            if not is_ai_vs_ai_race and (p1_final_results or p2_final_results): game_status = "game_over"
            elif is_ai_vs_ai_race and p1_final_results and p2_final_results and game_status != "game_over":
                game_status = "game_over"; show_comparison_panel = True

        # --- VẼ LÊN MÀN HÌNH ---
        background_effects.draw_background(screen)
        _draw_game_panel(game_surface_player, player_map_x, f"P1 ({player1_mode})", config.COLORS['highlight'], player1_controller, player1_time, p1_visited_nodes, p1_ai_path)
        _draw_game_panel(game_surface_ai, ai_map_x, f"P2 ({player2_mode})", config.COLORS['combo'], player2_controller, player2_time, p2_visited_nodes, p2_ai_path)
        for btn_data in buttons.values(): UI_helpers.draw_button(screen, btn_data)
        
        if show_comparison_panel:
            _draw_comparison_panel(p1_final_results, p2_final_results)

        pygame.display.flip()
        clock.tick(config.FPS)