import copy
import config
from . import snake_logic, food_logic, map_logic
from Algorithms import algorithm_helpers

class GameController:
    """
    Quản lý trạng thái và logic của một phiên chơi game Snake.
    """
    def __init__(self, map_info):
        # Nạp dữ liệu map từ tên file hoặc từ dictionary có sẵn
        if isinstance(map_info, str):
            temp_map_data = map_logic.load_map_data(map_info)
        elif isinstance(map_info, dict):
            temp_map_data = map_info
        else:
            temp_map_data = None

        if not temp_map_data:
            print("Lỗi GameController: map_info không hợp lệ hoặc không tải được.")
            self.outcome = "Map Load Error"
            self.snake = {'body': [], 'direction': 'RIGHT'}
            self.food = []
            self.steps = 0
            self.map_data = {}
            return 
        
        self.map_data = temp_map_data
        
        if not self.map_data.get('layout'):
            width = config.AI_MAP_WIDTH_TILES
            height = config.AI_MAP_HEIGHT_TILES
            self.map_data['layout'] = ["." * width for _ in range(height)]
            
        # Xác định chế độ thức ăn từ dữ liệu map
        self.food_mode = self.map_data.get('food_mode', 'all_at_once')
        
        # Nếu là chế độ tuần tự, chuẩn bị chuỗi thức ăn và chỉ số
        if self.food_mode == 'sequential':
            self.food_sequence = copy.deepcopy(self.map_data.get('food_sequence', []))
            self.current_food_index = 0
            
        self.snake = None 
        self.food = []   
        self.outcome = "Playing"
        self.steps = 0
        
        self.reset()

    def _attempt_to_spawn_sequential_food(self):
        """
        Hàm QUAN TRỌNG: Cố gắng sinh ra thức ăn tuần tự.
        Nó chỉ sinh ra khi vị trí đó không bị rắn chiếm đóng.
        """
        # Chỉ hoạt động ở chế độ tuần tự, khi không có thức ăn nào trên bản đồ, và vẫn còn thức ăn trong chuỗi
        if self.food_mode == 'sequential' and not self.food and self.current_food_index < len(self.food_sequence):
            next_food_pos = self.food_sequence[self.current_food_index]
            
            # KIỂM TRA xem có phần nào của rắn đang ở trên vị trí mồi tiếp theo không
            is_occupied = any(segment == next_food_pos for segment in self.snake['body'])
            
            # NẾU KHÔNG BỊ CHIẾM, thì mới sinh ra mồi. Nếu không, hàm sẽ kết thúc và chờ lượt sau.
            if not is_occupied:
                self.food.append({'pos': next_food_pos, 'type': 'normal'})

    def reset(self):
        """Reset lại trạng thái game về ban đầu."""
        self.snake = snake_logic.create_snake_from_map(self.map_data)
        self.outcome = "Playing"
        self.steps = 0
        
        # Xử lý việc sinh thức ăn ban đầu cho từng chế độ
        if self.food_mode == 'sequential':
            self.current_food_index = 0
            self.food = [] # Bắt đầu với không có thức ăn
            self._attempt_to_spawn_sequential_food() # Cố gắng sinh ra viên đầu tiên
        else:
            self.food = food_logic.create_food_from_map(self.map_data)
        
    def get_state(self):
        """Lấy trạng thái hiện tại của game."""
        return {'snake': self.snake, 'food': self.food, 'steps': self.steps, 'outcome': self.outcome}

    def set_direction(self, direction):
        """Đặt hướng đi cho rắn, có chống đi lùi."""
        if self.outcome != "Playing" or len(self.snake['body']) < 2: return
        head, neck = self.snake['body'][0], self.snake['body'][1]
        
        true_current_dir = 'RIGHT' # Hướng mặc định
        if head[1] < neck[1]: true_current_dir = 'UP'
        elif head[1] > neck[1]: true_current_dir = 'DOWN'
        elif head[0] < neck[0]: true_current_dir = 'LEFT'
        elif head[0] > neck[0]: true_current_dir = 'RIGHT'

        if direction == 'UP' and true_current_dir != 'DOWN': self.snake['direction'] = 'UP'
        elif direction == 'DOWN' and true_current_dir != 'UP': self.snake['direction'] = 'DOWN'
        elif direction == 'LEFT' and true_current_dir != 'RIGHT': self.snake['direction'] = 'LEFT'
        elif direction == 'RIGHT' and true_current_dir != 'LEFT': self.snake['direction'] = 'RIGHT'
    
    def update(self):
        """Cập nhật trạng thái game sau mỗi bước đi (dành cho người chơi)."""
        if self.outcome != "Playing": return

        next_head_pos = snake_logic.get_next_head_position(self.snake)
        self.snake['body'].insert(0, next_head_pos)
        
        if snake_logic.check_collision(self.snake, self.map_data):
            self.outcome = "Stuck"
            return
        
        self.steps += 1
        
        eaten_food = None
        # Kiểm tra xem rắn có ăn mồi không
        if self.food and self.food[0]['pos'] == next_head_pos:
            eaten_food = self.food[0]

        # Nếu không ăn, cắt đuôi để rắn di chuyển
        if not eaten_food:
            self.snake['body'].pop()

        # Nếu ăn mồi, xử lý cho từng chế độ
        if eaten_food:
            if self.food_mode == 'sequential':
                self.current_food_index += 1
                self.food = [] # Mồi được ăn, "biến mất"
            else:
                self.food.remove(eaten_food)
                new_food = food_logic.spawn_random_food(self.map_data, self.snake)
                if new_food: self.food.append(new_food)
                else: self.outcome = "Completed"
        
        # Luôn cố gắng sinh mồi tuần tự ở cuối mỗi lượt cập nhật
        self._attempt_to_spawn_sequential_food()
        
        # Kiểm tra điều kiện thắng cho chế độ tuần tự
        if self.food_mode == 'sequential' and not self.food and self.current_food_index >= len(self.food_sequence):
            self.outcome = "Completed"
            
    def update_by_path_step(self, next_pos):
        """Cập nhật trạng thái game theo từng bước trong path (dành cho AI)."""
        if self.outcome != "Playing": return
        
        # --- BỔ SUNG QUAN TRỌNG: CẬP NHẬT LẠI HƯỚNG ĐI CỦA RẮN ---
        # Dựa vào vị trí hiện tại và vị trí tiếp theo để xác định hướng đi
        current_head = self.snake['body'][0]
        dx = next_pos[0] - current_head[0]
        dy = next_pos[1] - current_head[1]

        # Cập nhật lại thuộc tính 'direction' của rắn
        if dx == 1: self.snake['direction'] = 'RIGHT'
        elif dx == -1: self.snake['direction'] = 'LEFT'
        elif dy == 1: self.snake['direction'] = 'DOWN'
        elif dy == -1: self.snake['direction'] = 'UP'
        # --- KẾT THÚC PHẦN BỔ SUNG ---

        self.snake['body'].insert(0, next_pos)
        if snake_logic.check_collision(self.snake, self.map_data):
            self.outcome = "Stuck"
            return
            
        self.steps += 1
        
        eaten_food = None
        if self.food and self.food[0]['pos'] == next_pos:
            eaten_food = self.food[0]

        if not eaten_food:
            self.snake['body'].pop()
        
        if eaten_food:
            if self.food_mode == 'sequential':
                self.current_food_index += 1
                self.food = []
            else:
                self.food.remove(eaten_food)
                new_food = food_logic.spawn_random_food(self.map_data, self.snake)
                if new_food: self.food.append(new_food)
                else: self.outcome = "Completed"
                
        # Luôn cố gắng sinh mồi tuần tự ở cuối mỗi lượt cập nhật
        self._attempt_to_spawn_sequential_food()
        
        # Kiểm tra điều kiện thắng
        if self.food_mode == 'sequential' and not self.food and self.current_food_index >= len(self.food_sequence):
            self.outcome = "Completed"