# GameLogic/game_controller.py
from . import snake_logic, food_logic, map_logic

class GameController:
    """
    Quản lý trạng thái và logic của một phiên chơi game Snake.
    """
    def __init__(self, map_name):
        self.map_data = map_logic.load_map_data(map_name)
        self.reset()

    def reset(self):
        """Thiết lập lại game về trạng thái ban đầu."""
        self.snake_data = snake_logic.create_snake_from_map(self.map_data)
        self.food_data = food_logic.create_food_from_map(self.map_data)
        self.steps = 0
        self.outcome = "Playing" # Các trạng thái: Playing, Completed, Stuck

    def get_state(self):
        """Lấy trạng thái hiện tại của game để giao diện có thể vẽ."""
        return {'snake': self.snake_data, 'food': self.food_data, 'steps': self.steps, 'outcome': self.outcome}

    def set_direction(self, direction):
        """Nhận lệnh đổi hướng từ người chơi."""
        current_dir = self.snake_data['direction']
        if direction == 'UP' and current_dir != 'DOWN': self.snake_data['direction'] = 'UP'
        elif direction == 'DOWN' and current_dir != 'UP': self.snake_data['direction'] = 'DOWN'
        elif direction == 'LEFT' and current_dir != 'RIGHT': self.snake_data['direction'] = 'LEFT'
        elif direction == 'RIGHT' and current_dir != 'LEFT': self.snake_data['direction'] = 'RIGHT'
    
    def _handle_movement_and_collision(self, is_grow):
        """Hàm nội bộ xử lý logic ăn mồi và va chạm."""
        head = self.snake_data['body'][0]
        # 1. Kiểm tra va chạm với tường hoặc thân
        if snake_logic.check_collision(self.snake_data, self.map_data):
            self.outcome = "Stuck"
            return
        # 2. Kiểm tra ăn mồi
        eaten_food = next((food for food in self.food_data if food['pos'] == head), None)
        if eaten_food:
            self.food_data.remove(eaten_food)
            if not self.food_data: self.outcome = "Completed"
            return True # Trả về True nếu ăn mồi
        # 3. Nếu không ăn, cắt đuôi
        if not is_grow:
            self.snake_data['body'].pop()
        return False

    def update(self):
        """Cập nhật 1 bước game cho người chơi."""
        if self.outcome != "Playing": return
        # Di chuyển rắn theo hướng hiện tại
        snake_logic.move_snake(self.snake_data)
        self.steps += 1
        self._handle_movement_and_collision(is_grow=False)

    def update_by_path_step(self, next_pos):
        """Cập nhật 1 bước game cho AI theo path."""
        if self.outcome != "Playing": return
        # Di chuyển rắn đến vị trí tiếp theo
        self.snake_data['body'].insert(0, next_pos)
        self.steps += 1
        # AI sẽ tự xử lý việc dài ra (không cắt đuôi) nếu ăn mồi
        ate_food = self._handle_movement_and_collision(is_grow=True)
        if not ate_food:
             self.snake_data['body'].pop()