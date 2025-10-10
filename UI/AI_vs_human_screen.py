"""
    Giao diện chế độ Người với AI
"""
from functools import partial
import pygame
from Algorithms.algorithm_helpers import manhattan_distance, euclidean_distance
import config
from UI import UI_helpers, AI_selection_screen
from UI.MainMenu import background_effects
from GameLogic.game_controller import GameController
from Algorithms import BFS, Astar, UCS, DFS, Greedy, IDS, OnlineSearch, BeamSearch, HillClimbing# (Giả định AI cũng dùng các thuật toán này)

def find_path_for_ai(controller, selected_mode):
    """
        Hàm tìm đường đi cho AI dựa vào thuật toán được chọn.
    """
    # Lấy trạng thái game hiện tại từ controller của AI.
    game_data = controller.get_state()
    # Nếu rắn không tồn tại, không thể tìm đường.
    if not game_data['snake']['body']: 
        return None
    
    if selected_mode == "OnlineSearch":
        # Gọi hàm riêng của OnlineSearch để tìm ra nước đi TỐT NHẤT tiếp theo.
        result = OnlineSearch.find_best_next_move(
            game_data['snake'], 
            game_data['food'], 
            controller.map_data
        )
        # Trả về hướng đi ('UP', 'DOWN',...) thay vì path
        return result.get('move') 
    
    # Lấy các thông tin cần thiết để chạy thuật toán.
    start_pos = game_data['snake']['body'][0]
    food_positions = [food['pos'] for food in game_data['food']]
    
    # Map để tra cứu hàm thuật toán tương ứng
    algorithm_map = {
        "BFS": BFS.find_path_bfs, 
        "DFS": DFS.find_path_dfs,
        "IDS": IDS.find_path_ids,  
        "UCS": UCS.find_path_ucs, 
        "HillClimbing": HillClimbing.find_path_hill_climbing,
        "BeamSearch": BeamSearch.find_path_beam_search,

        # Sử dụng partial để tạo các phiên bản khác nhau của A* và Greedy
        "A* (Manhattan)": partial(Astar.find_path_astar, heuristic_func=manhattan_distance),
        "A* (Euclidean)": partial(Astar.find_path_astar, heuristic_func=euclidean_distance),
        "Greedy (Manhattan)": partial(Greedy.find_path_greedy, heuristic_func=manhattan_distance),
        "Greedy (Euclidean)": partial(Greedy.find_path_greedy, heuristic_func=euclidean_distance)
    }
    # Lấy hàm thuật toán tương ứng với mode đã chọn.
    algorithm_to_run = algorithm_map.get(selected_mode)
    if not algorithm_to_run:
        return None # Nếu không tìm thấy thuật toán, trả về None

    # Gọi hàm thuật toán đã chọn.
    result = algorithm_to_run(start_pos, food_positions, controller.map_data, game_data['snake']['body'])
    return result.get('path')

def run_ai_vs_human_screen(screen, clock, selected_map_name):
    """Hàm chính để chạy màn hình game AI vs Human."""
    # --- 1. KHỞI TẠO ---
    title_font = pygame.font.Font(config.FONT_PATH, 32)
    info_font = pygame.font.Font(config.FONT_PATH, 22)
    end_font = pygame.font.Font(config.FONT_PATH, 60)
    instruction_font = pygame.font.Font(config.FONT_PATH, 18)
    
    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 1000)

    # Tạo 2 controller riêng biệt cho Player và AI
    player1_controller = GameController(selected_map_name)
    player2_controller = GameController(selected_map_name)
    
    map_width_px = config.DUAL_MAP_WIDTH_TILES * config.TILE_SIZE
    map_height_px = config.DUAL_MAP_HEIGHT_TILES * config.TILE_SIZE
    game_surface_player = pygame.Surface((map_width_px, map_height_px))
    game_surface_ai = pygame.Surface((map_width_px, map_height_px))

    # --- 2. QUẢN LÝ TRẠNG THÁI GIAO DIỆN ---
    game_status = "IDLE"  # "IDLE": Chờ bắt đầu, "playing": Đang chạy, "game_over": Đã kết thúc.
    player1_time = 0.0      # Thời gian thi đấu của người chơi 1.
    player2_time = 0.0      # Thời gian thi đấu của người chơi 2.
    # ai_path = []          # Lưu trữ lộ trình cho các AI offline.
    last_move_time = 0    # Mốc thời gian di chuyển cuối cùng, dùng để điều khiển tốc độ game.
    move_interval = 200   # Khoảng thời gian (ms) giữa mỗi bước di chuyển.
    # selected_ai_mode = "BFS" # Chế độ mặc định của AI
    player1_mode = "Player" # Player 1 mặc định là người
    player2_mode = "BFS"    # Player 2 mặc định là AI BFS
    p1_ai_path = []         # Thêm biến để lưu đường đi cho AI của Player 1
    p2_ai_path = []         # Lưu trữ lộ trình cho AI của Player 2.     

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
        # 'change_mode': UI_helpers.create_button(panel_center_x - 110, 400, 220, 40, f"Mode: {selected_ai_mode}")
        'change_mode_p1': UI_helpers.create_button(panel_center_x - 110, 400, 220, 40, f"P1 Mode: {player1_mode}"),
        'change_mode_p2': UI_helpers.create_button(panel_center_x - 110, 450, 220, 40, f"P2 Mode: {player2_mode}")
    }
    
    def _draw_game_panel(surface, pos_x, title, title_color, controller, time):
        """Hàm vẽ một khu vực chơi game, sử dụng controller."""
        game_data = controller.get_state()
        UI_helpers.draw_text(title, title_font, title_color, screen, pos_x + map_width_px / 2, 40)
        surface.fill(config.COLORS['bg'])
        UI_helpers.draw_map(surface, controller.map_data)
        UI_helpers.draw_snake(surface, game_data['snake'], game_data['food'])
        UI_helpers.draw_food(surface, game_data['food'])
    
        if game_data['outcome'] != "Playing":
            overlay = pygame.Surface((map_width_px, map_height_px), pygame.SRCALPHA)
        
            # Thêm điều kiện kiểm tra trạng thái "Draw"
            if game_data['outcome'] == "Draw":
                text_to_show = "DRAW"
                overlay.fill((100, 100, 100, 180)) # Màu xám trung tính cho trận hòa
            elif game_data['outcome'] == "Stuck":
                text_to_show = "YOU DIED"
                overlay.fill((50, 50, 50, 180))
            else: # "Completed"
                text_to_show = "YOU WIN"
                overlay.fill((0, 80, 150, 180))

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
    p1_animation_step = 0
    p2_animation_step = 0

    while running:
        mouse_pos = pygame.mouse.get_pos()
        current_ticks = pygame.time.get_ticks()
        
        for btn in buttons.values(): 
            UI_helpers.update_button_hover_state(btn, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                exit()
                
            if UI_helpers.handle_button_events(event, buttons['back']): 
                running = False

            if UI_helpers.handle_button_events(event, buttons['change_mode_p1']):
                new_mode = AI_selection_screen.run_algorithm_selection(screen)
                if new_mode is not None:
                    player1_mode = new_mode
                    buttons['change_mode_p1']['text'] = f"{player1_mode}"
            
            if UI_helpers.handle_button_events(event, buttons['change_mode_p2']):
                new_mode = AI_selection_screen.run_algorithm_selection(screen)
                if new_mode is not None:
                    player2_mode = new_mode
                    buttons['change_mode_p2']['text'] = f"{player2_mode}"

            if UI_helpers.handle_button_events(event, buttons['start']) and game_status == "IDLE":
                game_status = "playing"
                start_time = current_ticks
                last_move_time = current_ticks
                p1_ai_path = []
                p2_ai_path = []
                p1_animation_step = 1
                p2_animation_step = 1

            if UI_helpers.handle_button_events(event, buttons['reset']):
                player1_controller.reset()
                player2_controller.reset()
                game_status = "IDLE"
                player1_time = 0.0
                player2_time = 0.0
                p1_ai_path = []
                p2_ai_path = []

            # Xử lý input cho người chơi
            if event.type == pygame.KEYDOWN and game_status == "playing":
                # XỬ LÝ DI CHUYỂN CHO PLAYER 1 (WASD)
                if player1_mode == "Player":
                    if event.key == pygame.K_w: player1_controller.set_direction('UP')
                    elif event.key == pygame.K_s: player1_controller.set_direction('DOWN')
                    elif event.key == pygame.K_a: player1_controller.set_direction('LEFT')
                    elif event.key == pygame.K_d: player1_controller.set_direction('RIGHT')

                # XỬ LÝ DI CHUYỂN CHO PLAYER 2 (MŨI TÊN)
                if player2_mode == "Player":
                    if event.key == pygame.K_UP: player2_controller.set_direction('UP')
                    elif event.key == pygame.K_DOWN: player2_controller.set_direction('DOWN')
                    elif event.key == pygame.K_LEFT: player2_controller.set_direction('LEFT')
                    elif event.key == pygame.K_RIGHT: player2_controller.set_direction('RIGHT')
        
        # --- CẬP NHẬT LOGIC GAME ---
        if game_status == "playing":
            # Cập nhật thời gian cho cả hai
            if player1_controller.get_state()['outcome'] == "Playing": 
                player1_time = (current_ticks - start_time) / 1000.0
            if player2_controller.get_state()['outcome'] == "Playing": 
                player2_time = (current_ticks - start_time) / 1000.0

            # Kiểm tra xem đã đến lúc di chuyển chưa
            if current_ticks - last_move_time > move_interval:
                # --- Logic Player 1 ---
                if player1_mode == "Player":
                    # Nếu là người chơi, cập nhật di chuyển bình thường
                    player1_controller.update()
                elif player1_mode == "OnlineSearch":
                    # Với OnlineSearch, ta phải hỏi nó nước đi ở MỖI BƯỚC
                    next_move = find_path_for_ai(player1_controller, player1_mode)
                    if next_move:
                        player1_controller.set_direction(next_move)
                        player1_controller.update()
                    else:
                        # Nếu không tìm được nước đi -> bị kẹt
                        player1_controller.outcome = "Stuck"
                else:
                    # Nếu là AI, làm theo logic đơn giản hơn:
                    # 1. Nếu AI không có đường đi, tìm một đường đi mới.
                    if not p1_ai_path:
                        p1_ai_path = find_path_for_ai(player1_controller, player1_mode)
                        p1_animation_step = 1 # Reset để bắt đầu từ bước đầu tiên

                    # 2. Nếu AI có đường đi, đi bước tiếp theo.
                    if p1_ai_path and p1_animation_step < len(p1_ai_path):
                        next_pos = p1_ai_path[p1_animation_step]
                        player1_controller.update_by_path_step(next_pos)
                        p1_animation_step += 1
                    
                    # 3. Nếu AI đã đi hết đường, xóa đường đi để lượt sau tìm đường mới.
                    if p1_ai_path and p1_animation_step >= len(p1_ai_path):
                        p1_ai_path = [] 
                    
                # --- Logic Player 2 ---
                if player2_mode == "Player":
                    # Nếu là người chơi, cập nhật di chuyển bình thường
                    player2_controller.update()
                elif player2_mode == "OnlineSearch":
                    # Với OnlineSearch, ta phải hỏi nó nước đi ở MỖI BƯỚC
                    next_move = find_path_for_ai(player2_controller, player2_mode)
                    if next_move:
                        player2_controller.set_direction(next_move)
                        player2_controller.update()
                    else:
                        # Nếu không tìm được nước đi -> bị kẹt
                        player2_controller.outcome = "Stuck"
                else:
                    # Nếu là AI, làm theo logic đơn giản hơn:
                    # 1. Nếu AI không có đường đi, tìm một đường đi mới.
                    if not p2_ai_path:
                        p2_ai_path = find_path_for_ai(player2_controller, player2_mode)
                        p2_animation_step = 1 # Reset để bắt đầu từ bước đầu tiên

                    # 2. Nếu AI có đường đi, đi bước tiếp theo.
                    if p2_ai_path and p2_animation_step < len(p2_ai_path):
                        next_pos = p2_ai_path[p2_animation_step]
                        player2_controller.update_by_path_step(next_pos)
                        p2_animation_step += 1
                    
                    # 3. Nếu AI đã đi hết đường, xóa đường đi để lượt sau tìm đường mới.
                    if p2_ai_path and p2_animation_step >= len(p2_ai_path):
                        p2_ai_path = [] 

                last_move_time = current_ticks
            
            player1_outcome = player1_controller.get_state()['outcome']
            player2_outcome = player2_controller.get_state()['outcome']

            # Nếu một trong hai người chơi đã có kết quả (không còn là "Playing")
            if game_status == "playing" and (player1_outcome != "Playing" or player2_outcome != "Playing"):
                game_status = "game_over" # Dừng game ngay lập tức

                p1_is_playing = (player1_outcome == "Playing")
                p2_is_playing = (player2_outcome == "Playing")

                if not p1_is_playing and not p2_is_playing:
                    player1_controller.outcome = "Draw"
                    player2_controller.outcome = "Draw"

                # Xác định người thắng cuộc
                elif player1_outcome == "Stuck" and p2_is_playing:
                    player2_controller.outcome = "Completed"
                
                elif player2_outcome == "Stuck" and p1_is_playing:
                    player1_controller.outcome = "Completed"

                elif player1_outcome == "Completed" and p2_is_playing:
                    player2_controller.outcome = "Stuck"

                elif player2_outcome == "Completed" and p1_is_playing:
                    player1_controller.outcome = "Stuck"

        # --- 5. VẼ LÊN MÀN HÌNH ---
        background_effects.draw_background(screen)

        # Vẽ panel cho Player 1
        p1_title = "PLAYER 1" if player1_mode == "Player" else f"Player 1 ({player1_mode})"
        _draw_game_panel(game_surface_player, player_map_x, p1_title, config.COLORS['highlight'], player1_controller, player1_time)
        
        # Vẽ panel cho Player 2
        p2_title = "PLAYER 2" if player2_mode == "Player" else f"Player 2 ({player2_mode})"
        _draw_game_panel(game_surface_ai, ai_map_x, p2_title, config.COLORS['combo'], player2_controller, player2_time)
        
        # --- THÊM PHẦN VẼ HƯỚNG DẪN ---
        # Tính toán vị trí Y chung cho các dòng hướng dẫn
        instruction_y = 80 + map_height_px + 40 + 60 # Dưới dòng stats

        if player1_mode == "Player":
            UI_helpers.draw_text("P1: Di chuyển bằng WASD", instruction_font, config.COLORS['white'], screen, player_map_x + map_width_px / 2, instruction_y)
        if player2_mode == "Player":
            UI_helpers.draw_text("P2: Di chuyển bằng Mũi Tên", instruction_font, config.COLORS['white'], screen, ai_map_x + map_width_px / 2, instruction_y)
        
        for btn_data in buttons.values(): 
            UI_helpers.draw_button(screen, btn_data)
        
        pygame.display.flip()
        clock.tick(config.FPS)