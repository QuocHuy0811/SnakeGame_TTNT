"""
    Giao diện chế độ AI
"""
import pygame
from functools import partial
from Algorithms.algorithm_helpers import manhattan_distance, euclidean_distance
import config
import copy
import time
from UI import UI_helpers
from UI.MainMenu import background_effects
from GameLogic import game_helpers, snake_logic, food_logic
from GameLogic.game_controller import GameController 
from Algorithms import BFS, Astar, UCS, DFS, Greedy, IDS, OnlineSearch, BeamSearch, HillClimbing
from UI import AI_selection_screen, history_screen, map_editor_screen 
    
def find_path_with_algorithm(algorithm_func, start_pos, food_data, map_data, snake_body):
    """
        Chạy thuật toán tìm đường MỘT LẦN DUY NHẤT để có kết quả chính xác.
    """
    food_positions = [food['pos'] for food in food_data]
    if not food_positions:
        return {'path': None, 'visited_nodes': [], 'generated_count': 0, 'visited_count': 0}

    # Đối với A* và Greedy, chúng cần một mục tiêu duy nhất.
    # Ta sẽ chọn mục tiêu gần nhất dựa trên hàm Manhattan.
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
    algorithm_to_run = algorithm_map.get(selected_mode)
    if not algorithm_to_run: 
        return None

    while temp_food:
        search_start_time = time.perf_counter()
        search_result = find_path_with_algorithm(algorithm_to_run, temp_snake_body[0], temp_food, map_data, temp_snake_body)
        path = search_result.get('path')


        total_search_time += (time.perf_counter() - search_start_time)

        total_visited += search_result.get('visited_count', 0)
        total_generated += search_result.get('generated_count', 0)

        if not path or len(path) <= 1:
            return {
                'outcome': 'Stuck', 
                'steps': total_steps, 
                'search_time': total_search_time,
                'snake': {'body': temp_snake_body, 'direction': 'RIGHT'},
                'visited': total_visited, 
                'generated': total_generated    
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

    # Thân rắn cuối cùng là các vị trí cuối cùng trong lịch sử di chuyển
    final_snake_length = initial_length + total_food_eaten
    final_body = path_history[-final_snake_length:]
    return {
        'outcome': 'Completed', 
        'steps': total_steps, 
        'search_time': total_search_time,
        'snake': {'body': final_body, 'direction': 'RIGHT'},
        'visited': total_visited, 
        'generated': total_generated
    }
def _find_safe_survival_move(snake_data, map_data):
    """
    Tìm một nước đi an toàn cho rắn để sinh tồn, tránh tường và thân.
    Ưu tiên hướng đi hiện tại để giữ đà.
    """
    head = snake_data['body'][0]
    current_direction = snake_data['direction']
    
    possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    safe_moves = []

    for move in possible_moves:
        new_head = head
        if move == 'UP': new_head = (head[0], head[1] - 1)
        elif move == 'DOWN': new_head = (head[0], head[1] + 1)
        elif move == 'LEFT': new_head = (head[0] - 1, head[1])
        elif move == 'RIGHT': new_head = (head[0] + 1, head[1])
        
        # Kiểm tra va chạm
        if new_head not in map_data['walls'] and new_head not in snake_data['body']:
            safe_moves.append(move)
            
    if not safe_moves:
        return None # Không còn nước đi an toàn
        
    # Ưu tiên đi thẳng nếu có thể
    if current_direction in safe_moves:
        return current_direction
    else:
        # Nếu không thể đi thẳng, chọn một nước an toàn bất kỳ
        return safe_moves[0]

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

    # BIẾN MỚI: Thêm một bộ đếm cho các map tự tạo
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
    # game_state là biến quan trọng nhất, quyết định xem game đang làm gì.
    # Các trạng thái có thể là:
    # "IDLE": Chờ người dùng nhấn "Solve".
    # "PLAYER_READY": Chế độ người chơi, chờ phím di chuyển đầu tiên.
    # "PLAYER_PLAYING": Người chơi đang điều khiển rắn.
    # "AI_AUTOPLAY": Trạng thái chính của AI, tìm đường đến mồi tiếp theo.
    # "VISUALIZING": Hiển thị các nút đã duyệt và path tìm được trong một khoảng ngắn.
    # "ANIMATING_PATH": Diễn hoạt con rắn di chuyển theo path đã tìm được.
    # "AI_ONLINE_PLAYING": Chế độ cho AI online, ra quyết định theo từng bước.

    game_state = "IDLE"
    selected_mode =  "Player"

    if selected_mode == "Player":
        game_state = "PLAYER_READY"

    # --- NHÓM BIẾN ĐIỀU KHIỂN DIỄN HOẠT (ANIMATION) ---
    # Mục đích: Quản lý việc cho con rắn AI di chuyển theo đường đi đã tìm được.

    # Lưu danh sách các tọa độ (path) mà thuật toán tìm ra.
    ai_path = [] 
    # Biến đếm, cho biết con rắn đang ở bước thứ mấy trong 'ai_path'.
    animation_step = 0 
    # Lưu mốc thời gian (ms) của lần di chuyển gần nhất trong diễn hoạt.
    last_animation_time = 0 
    # Khoảng thời gian (ms) giữa mỗi bước di chuyển của rắn, quyết định tốc độ diễn hoạt.
    animation_interval = 80

    # --- NHÓM BIẾN TRỰC QUAN HÓA (VISUALIZATION) ---
    # Mục đích: Hiển thị quá trình "suy nghĩ" của thuật toán trước khi rắn di chuyển.

    # Lưu danh sách các ô mà thuật toán đã duyệt qua (để vẽ các chấm xám).
    visited_nodes = []
    # Lưu danh sách các ô thuộc đường đi cuối cùng (để vẽ đường đi nổi bật).
    path_nodes_to_draw = []


    # Ghi lại mốc thời gian khi bắt đầu hiển thị quá trình tìm kiếm.
    visualization_timer_start = 0
    # Thời gian (ms) mà quá trình trực quan hóa được hiển thị trước khi rắn bắt đầu chạy.
    VISUALIZATION_DELAY = 500 #ms

    # --- NHÓM BIẾN ĐIỀU KHIỂN TỐC ĐỘ (SPEED CONTROL) ---
    # Mục đích: Quản lý tốc độ di chuyển của rắn trong các chế độ chơi khác nhau.

    # Tốc độ di chuyển của người chơi (ms mỗi bước).
    player_move_interval = 200
    # Lưu mốc thời gian di chuyển cuối cùng của người chơi.
    last_player_move_time = 0


    # Tốc độ của AI Online (ms cho mỗi lần ra quyết định).
    online_ai_move_interval = 200
    # Lưu mốc thời gian di chuyển cuối cùng của AI Online.
    last_online_ai_move_time = 0

    # --- NHÓM BIẾN TRẠNG THÁI & THỐNG KÊ CHUNG ---
    # Mục đích: Theo dõi trạng thái chung của game và các số liệu để báo cáo.

    # Cờ (True/False) xác định xem diễn hoạt có đang bị tạm dừng hay không.
    is_paused = False
    # Lưu tổng thời gian diễn hoạt (Animation Time) đã trôi qua, tính bằng giây.
    current_time = 0.0 
    # Cộng dồn tổng thời gian "suy nghĩ" (Search Time) của thuật toán.
    total_search_time = 0.0
    # Cộng dồn tổng số nút đã được duyệt (Visited) qua tất cả các lần tìm kiếm.
    total_visited_nodes = 0
    # Cộng dồn tổng số nút đã được sinh ra (Generated) qua tất cả các lần tìm kiếm.
    total_generated_nodes = 0

    # --- NHÓM BIẾN CHO HIỆU ỨNG NHẤP NHÁY ---
    # Mục đích: Tạo hiệu ứng nhấp nháy cho viên thức ăn mà AI đang nhắm tới.

    # Lưu tọa độ của viên thức ăn mà AI đang tìm đường đến.
    target_food_pos = None
    # Cờ (True/False) xác định xem viên thức ăn nên được vẽ hay ẩn đi.
    is_blinking_visible = True
    # Lưu mốc thời gian của lần thay đổi trạng thái nhấp nháy gần nhất.
    last_blink_time = 0
    # Tốc độ nháy (ms giữa mỗi lần hiện và ẩn).
    BLINK_INTERVAL = 200 #ms

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
    stop_button = UI_helpers.create_button(middle_area_center_x - 100, 480, 200, 50, "Stop")
    skip_button = UI_helpers.create_button(middle_area_center_x - 100, 550, 200, 50, "Skip")
    
    if selected_mode == "Player":
        buttons['solve']['is_enabled'] = False
        buttons['solve']['text'] = "Start Game"
    
    # --- Bật tắt nút Skip ---
    if controller.map_data.get('food_mode') == 'sequential':
        skip_button['is_enabled'] = False
    else:
        skip_button['is_enabled'] = True

    running = True
    while running:
        # Lấy trạng thái game mới nhất từ controller
        game_data = controller.get_state()
        mouse_pos = pygame.mouse.get_pos()
        current_ticks = pygame.time.get_ticks()
        
        # Cập nhật hover
        for btn in buttons.values(): 
            UI_helpers.update_button_hover_state(btn, mouse_pos)
        UI_helpers.update_button_hover_state(skip_button, mouse_pos)
        if game_state == "ANIMATING_PATH":
            UI_helpers.update_button_hover_state(stop_button, mouse_pos)

        if game_state in ["AI_AUTOPLAY", "VISUALIZING", "ANIMATING_PATH"]:
            UI_helpers.update_button_hover_state(skip_button, mouse_pos)

        # ==================== A. XỬ LÝ SỰ KIỆN ====================
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False

            # Xử lý sự kiện click cho từng nút
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
                    # Khóa Skip
                    skip_button['is_enabled'] = False

            if UI_helpers.handle_button_events(event, buttons['back_to_menu']): 
                running = False

            if UI_helpers.handle_button_events(event, buttons['reset']):
                # Gọi hàm reset của controller để đưa rắn và mồi về vị trí ban đầu.
                controller.reset()
                # Đặt lại toàn bộ các biến trạng thái của màn hình game về giá trị mặc định.
                game_state = "IDLE"
                is_paused = False
                stop_button['text'] = "Stop"
                ai_path = []
                animation_step = 0
                current_time = 0.0
                total_search_time = 0.0
                total_visited_nodes = 0
                total_generated_nodes = 0
                visited_nodes = []
                path_nodes_to_draw = []
                target_food_pos = None
                # Xóa kết quả tính toán trước (nếu có).
                full_playthrough_result = None
                # Đặt lại trạng thái game phù hợp với chế độ đang chọn.
                if selected_mode == "Player":
                    game_state = "PLAYER_READY"
                else: # Các chế độ AI
                    game_state = "IDLE"
                
                # Bật/Tắt Skip
                if controller.map_data.get('food_mode') == 'sequential':
                    # Nếu là map tự tạo, khóa nút Skip
                    skip_button['is_enabled'] = False
                else:
                    # Nếu là map thường, bật lại nút Skip
                    skip_button['is_enabled'] = True

            if UI_helpers.handle_button_events(event, buttons['solve']):
                if game_state == "IDLE" or game_state == "PLAYER_READY":
                    # Reset lại trạng thái của rắn và mồi để bắt đầu một lượt chơi mới.
                    controller.reset()

                    # Reset các biến và kết quả đã lưu
                    total_search_time = 0.0
                    total_visited_nodes = 0
                    total_generated_nodes = 0
                    full_playthrough_result = None 

                     # Dựa vào chế độ đang chọn ('selected_mode') để quyết định trạng thái tiếp theo.
                    if selected_mode == "Player":
                        # Chuyển sang trạng thái người chơi đang điều khiển rắn.
                        game_state = "PLAYER_PLAYING"
                        # Ghi lại mốc thời gian để điều khiển tốc độ di chuyển của người chơi.
                        last_player_move_time = pygame.time.get_ticks()

                    elif selected_mode == "OnlineSearch":
                        # Chuyển sang trạng thái dành riêng cho AI Online.
                        game_state = "AI_ONLINE_PLAYING"
                        # Ghi lại mốc thời gian để điều khiển tốc độ của AI Online.
                        last_online_ai_move_time = pygame.time.get_ticks()
                    else: # Tất cả các thuật toán offline còn lại (BFS, A*, DFS,...)
                        # Chuyển sang trạng thái AI tự động chơi.
                        game_state = "AI_AUTOPLAY"
                        # Gọi hàm _calculate_full_playthrough để tính toán trước toàn bộ kết quả.
                        # Kết quả này sẽ được lưu vào biến 'full_playthrough_result'.
                        initial_snake = snake_logic.create_snake_from_map(controller.map_data)
                        initial_food = []
                        if controller.map_data.get('food_mode') == 'sequential':
                            food_sequence = controller.map_data.get('food_sequence', [])
                            if food_sequence: # Nếu có thức ăn trong chuỗi
                                # Lấy viên đầu tiên làm mục tiêu ban đầu
                                initial_food = [{'pos': food_sequence[0], 'type': 'normal'}]
                        else: # Chế độ all_at_once cho map cũ
                            initial_food = food_logic.create_food_from_map(controller.map_data)
                        full_playthrough_result = _calculate_full_playthrough(initial_snake, initial_food, selected_mode, controller.map_data)

            if UI_helpers.handle_button_events(event, buttons['history']):
                # Tạm dừng màn hình game này và gọi hàm để chạy màn hình Lịch sử.
                history_screen.run_history_screen(screen, clock)

            # Kiểm tra sự kiện click vào nút "Skip".
            # Chỉ hoạt động khi game đang trong các trạng thái của AI (AI_AUTOPLAY, ANIMATING_PATH).
            if UI_helpers.handle_button_events(event, skip_button) and game_state in ["AI_AUTOPLAY", "ANIMATING_PATH"]:
                # Kiểm tra xem đã có kết quả được tính toán trước hay chưa.
                if full_playthrough_result:
                    # Cập nhật controller với trạng thái cuối cùng
                    controller.snake = full_playthrough_result['snake']
                    controller.steps = full_playthrough_result['steps']
                    controller.food = [] 
                    controller.outcome = full_playthrough_result['outcome']

                    # Lưu kết quả CHÍNH XÁC từ full_playthrough_result đã tính toán trước đó
                    game_helpers.save_game_result(
                        selected_map_name, selected_mode, controller.steps, 
                        0.0, # Animation time khi skip là 0
                        full_playthrough_result['search_time'], 
                        controller.outcome,
                        full_playthrough_result['visited'], 
                        full_playthrough_result['generated']
                    )
                    
                    # Đưa game về trạng thái chờ ban đầu.
                    game_state = "IDLE"
                    # Xóa các biến tạm thời
                    ai_path = [] 
                    visited_nodes = [] 
                    path_nodes_to_draw = []
                    target_food_pos = None
            
            if UI_helpers.handle_button_events(event, buttons['change_mode']):
                # Gọi màn hình chọn thuật toán.
                new_mode = AI_selection_screen.run_algorithm_selection(screen)
                # Nếu người dùng chọn một mode mới
                if new_mode is not None: 
                    # Cập nhật chế độ đã chọn
                    selected_mode = new_mode
                    # Cập nhật lại text trên nút bấm
                    buttons['change_mode']['text'] = f"{selected_mode}"
                    
                    # Cập nhật trạng thái nút "Solve" và trạng thái game cho phù hợp với mode mới.
                    if selected_mode == "Player":
                        buttons['solve']['is_enabled'] = False
                        buttons['solve']['text'] = "Start Game"
                        game_state = "PLAYER_READY" # Chuyển sang trạng thái sẵn sàng
                    else:
                        buttons['solve']['is_enabled'] = True
                        buttons['solve']['text'] = "Solve"
                        game_state = "IDLE" # Chuyển về trạng thái chờ cho AI

            # Kiểm tra sự kiện click vào nút "Stop/Resume".
            # Chỉ hoạt động khi rắn đang di chuyển theo path (ANIMATING_PATH).            
            if UI_helpers.handle_button_events(event, stop_button) and game_state == "ANIMATING_PATH":
                # Đảo ngược trạng thái tạm dừng (True -> False, False -> True).
                is_paused = not is_paused
                # Cập nhật text trên nút cho phù hợp.
                if is_paused:
                    stop_button['text'] = "Resume"
                else:
                    stop_button['text'] = "Stop"
            
            # Kiểm tra sự kiện nhấn phím trong chế độ người chơi.
            if selected_mode == "Player" and event.type == pygame.KEYDOWN:
                    # Nếu game đang ở trạng thái sẵn sàng.
                    if game_state == "PLAYER_READY":
                        # Nếu phím được nhấn là một phím di chuyển.
                        if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                            # Bắt đầu game.
                            game_state = "PLAYER_PLAYING"
                            # Ghi lại mốc thời gian
                            last_player_move_time = pygame.time.get_ticks()
                            # Đặt hướng đi ngay lập tức dựa trên phím đã nhấn
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

        # ==================== B. CẬP NHẬT LOGIC GAME ====================
        # --- Trạng thái 1: Người chơi đang chơi ---
        if game_state == "PLAYER_PLAYING":
            # Kiểm tra xem đã đủ thời gian trôi qua để thực hiện bước đi tiếp theo chưa.
            # current_ticks là thời gian hiện tại của hệ thống
            if current_ticks - last_player_move_time > player_move_interval:
                # Nếu đã đủ thời gian, gọi hàm update() của controller để di chuyển rắn 1 bước.
                controller.update() 
                # Cập nhật lại mốc thời gian của lần di chuyển cuối cùng.
                last_player_move_time = current_ticks
            
            # Sau mỗi lần di chuyển, kiểm tra xem game đã kết thúc chưa (thắng/thua).
            if game_data['outcome'] != "Playing":
                game_state = "IDLE"
        
        # --- Trạng thái 2: AI Online đang chơi ---
        elif game_state == "AI_ONLINE_PLAYING":
            # Kiểm tra xem đã đến lúc AI ra quyết định tiếp theo chưa.
            if current_ticks - last_online_ai_move_time > online_ai_move_interval:
                # Lấy trạng thái game mới nhất.
                game_data = controller.get_state()
                # Chỉ thực hiện nếu game vẫn đang tiếp diễn.
                if game_data['outcome'] == "Playing":
                    # Ghi lại thời gian bắt đầu "suy nghĩ".
                    search_start_time = pygame.time.get_ticks()
                    # Gọi hàm Online Search
                    search_result = OnlineSearch.find_best_next_move(game_data['snake'], game_data['food'], controller.map_data)
                    # Cộng dồn thời gian "suy nghĩ" vào biến tổng.
                    total_search_time += (pygame.time.get_ticks() - search_start_time) / 1000.0
                    
                    # Lấy nước đi ('UP', 'DOWN',...) từ kết quả trả về.
                    next_move = next_move = search_result.get('move')
                    # Nếu tìm thấy một nước đi hợp lệ.
                    if next_move:
                        # Ra lệnh cho controller đổi hướng và cập nhật di chuyển.
                        controller.set_direction(next_move)
                        controller.update()
                        # Xóa các visualization cũ (nếu có) sau khi di chuyển.
                        visited_nodes = []
                        path_nodes_to_draw = []
                    else:
                        # Nếu AI không tìm được nước đi (bị kẹt), kết thúc game
                        controller.outcome = "Stuck"
                        # Lưu kết quả thua cuộc vào lịch sử.
                        game_helpers.save_game_result(
                            selected_map_name, selected_mode, game_data['steps'], 0,
                            total_search_time, "Stuck", total_visited_nodes, total_generated_nodes
                        )

                    # Cập nhật lại mốc thời gian của lần ra quyết định cuối cùng.
                    last_online_ai_move_time = current_ticks
                else:
                    # Nếu game đã kết thúc (thắng hoặc thua)
                    if game_data['outcome'] == "Completed":
                        # Lưu kết quả thắng cuộc vào lịch sử.
                        game_helpers.save_game_result(
                            selected_map_name, selected_mode, game_data['steps'], 0,
                            total_search_time, "Completed", total_visited_nodes, total_generated_nodes
                        )
                    # Chuyển về trạng thái chờ.
                    game_state = "IDLE"

        # --- Trạng thái 3: AI Offline đang tự chơi (chưa có đường đi) ---
        # Trạng thái này chỉ được kích hoạt khi AI cần tìm đường đến viên thức ăn tiếp theo.
        elif game_state == "AI_AUTOPLAY":
            # KỊCH BẢN 1: NẾU CÓ THỨC ĂN, TÌM ĐƯỜNG ĐI MỚI
            if game_data['food']:
                if not ai_path:
                    # ... (Phần code tìm đường của bạn ở đây, giữ nguyên không thay đổi)
                    algorithm_map = {
                        "BFS": BFS.find_path_bfs, 
                        "DFS": DFS.find_path_dfs,
                        "IDS": IDS.find_path_ids,  
                        "UCS": UCS.find_path_ucs, 
                        "HillClimbing": HillClimbing.find_path_hill_climbing,
                        "BeamSearch": BeamSearch.find_path_beam_search,
                        "A* (Manhattan)": partial(Astar.find_path_astar, heuristic_func=manhattan_distance),
                        "A* (Euclidean)": partial(Astar.find_path_astar, heuristic_func=euclidean_distance),
                        "Greedy (Manhattan)": partial(Greedy.find_path_greedy, heuristic_func=manhattan_distance),
                        "Greedy (Euclidean)": partial(Greedy.find_path_greedy, heuristic_func=euclidean_distance)
                    }
                    algorithm_to_run = algorithm_map.get(selected_mode)
                    if algorithm_to_run:
                        search_start_time = pygame.time.get_ticks()
                        search_result = find_path_with_algorithm(algorithm_to_run, game_data['snake']['body'][0], game_data['food'], controller.map_data, game_data['snake']['body'])
                        total_search_time += (pygame.time.get_ticks() - search_start_time) / 1000.0
                        total_visited_nodes += search_result.get('visited_count', 0)
                        total_generated_nodes += search_result.get('generated_count', 0)
                        visited_nodes = search_result.get('visited_nodes', [])
                        ai_path = search_result.get('path', None)
                        if ai_path: 
                            path_nodes_to_draw = ai_path
                            target_food_pos = ai_path[-1]
                            game_state = "VISUALIZING"
                            visualization_timer_start = pygame.time.get_ticks()
                        else:
                            controller.outcome = "Stuck"
                            # ... (Phần code lưu game, giữ nguyên không thay đổi)

            # KỊCH BẢN 2: NẾU KHÔNG CÓ THỨC ĂN (KÍCH HOẠT CHẾ ĐỘ SINH TỒN)
            else:
                if current_ticks - last_animation_time > animation_interval:
                    # Tìm một nước đi an toàn thay vì đi thẳng một cách mù quáng
                    safe_move = _find_safe_survival_move(game_data['snake'], controller.map_data)
                    
                    if safe_move:
                        # Nếu tìm thấy nước đi an toàn, di chuyển theo hướng đó
                        controller.set_direction(safe_move)
                        controller.update()
                    else:
                        # Nếu không còn nước đi an toàn nào, rắn đã bị kẹt
                        controller.outcome = "Stuck"
                    
                    last_animation_time = current_ticks
        # --- Trạng thái 4: Đang hiển thị quá trình tìm kiếm ---
        if game_state == "VISUALIZING":
            # Tạo hiệu ứng nhấp nháy cho viên thức ăn mục tiêu.
            if current_ticks - last_blink_time > BLINK_INTERVAL:
                is_blinking_visible = not is_blinking_visible
                last_blink_time = current_ticks

            # Kiểm tra xem đã hết thời gian hiển thị (VISUALIZATION_DELAY) chưa.
            if current_ticks - visualization_timer_start > VISUALIZATION_DELAY:
                # Nếu đã hết, chuyển sang trạng thái diễn hoạt rắn di chuyển.
                game_state = "ANIMATING_PATH"
                # Bắt đầu đếm thời gian cho animation.
                last_animation_time = current_ticks
                # Bắt đầu từ bước đầu tiên của path.
                animation_step = 1

        # --- Trạng thái 5: Đang diễn hoạt rắn di chuyển theo path ---
        elif game_state == "ANIMATING_PATH":
            # Chỉ di chuyển nếu game không bị tạm dừng.
            if not is_paused:
                current_render_time = pygame.time.get_ticks()
                # Kiểm tra xem đã đến lúc di chuyển bước tiếp theo chưa.
                if current_render_time - last_animation_time > animation_interval:
                    # Kiểm tra xem có còn bước đi trong path không
                    if animation_step < len(ai_path):
                        # Di chuyển rắn đến bước tiếp theo trong path.
                        controller.update_by_path_step(ai_path[animation_step])
                        animation_step += 1
                        last_animation_time = current_render_time
                    # Nếu đã đi hết path, animation cho đoạn này kết thúc
                    else: 
                        # Xóa các visualization cũ.
                        visited_nodes, path_nodes_to_draw = [], [] # Xóa các chấm visualize
                        ai_path = [] # Xóa path cũ
                        target_food_pos = None
                        game_state = "AI_AUTOPLAY" # Quay lại tìm đường cho miếng mồi tiếp theo

                # Kiểm tra điều kiện thắng (có thể xảy ra bất cứ lúc nào trong lúc di chuyển)
                if controller.get_state()['outcome'] == "Completed":
                    # Chuyển về trạng thái chờ.
                    game_state = "IDLE"
                    target_food_pos = None
                    # Tính toán tổng thời gian diễn hoạt.
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
                    # Xóa các chấm visualize khi thắng
                    visited_nodes, path_nodes_to_draw = [], [] 
                elif game_state == "AI_AUTOPLAY" and not game_data['food']:
                    # Kiểm tra xem đã đến lúc di chuyển chưa (để rắn không chạy quá nhanh)
                    if current_ticks - last_animation_time > animation_interval:
                        # Ra lệnh cho rắn đi thẳng một bước
                        controller.update()
                        # Cập nhật lại mốc thời gian
                        last_animation_time = current_ticks

        # ==================== C. VẼ LÊN MÀN HÌNH ====================
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
        
        if game_state in ["AI_AUTOPLAY", "ANIMATING_PATH"]and selected_mode != "OnlineSearch":
            UI_helpers.draw_button(screen, skip_button)
        if game_state == "ANIMATING_PATH" and selected_mode != "OnlineSearch":
            UI_helpers.draw_button(screen, stop_button)
        panel_rect = pygame.Rect(panel_x, 0, config.AI_PANEL_WIDTH, config.SCREEN_HEIGHT); 
        pygame.draw.rect(screen, config.COLORS['white_bg'], panel_rect, border_radius=20)
        
        UI_helpers.draw_text("Control Panel", panel_font, config.COLORS['text_dark'], screen, panel_center_x, 50)
        
        for btn_data in buttons.values(): 
            UI_helpers.draw_button(screen, btn_data)
        
        pygame.display.flip(); 
        clock.tick(config.FPS)