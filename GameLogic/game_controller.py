"""
    Hàm điều khiển chính
"""
import config
from . import snake_logic, food_logic, map_logic
from Algorithms import algorithm_helpers
class GameController:
    """
    Quản lý trạng thái và logic của một phiên chơi game Snake.
    """
    def __init__(self, map_info):
        # 1. Tải hoặc nhận dữ liệu map
        temp_map_data = None
        if isinstance(map_info, str):
            temp_map_data = map_logic.load_map_data(map_info)
        else: # Là một dictionary
            temp_map_data = map_info

        # 2. Xử lý trường hợp map bị lỗi hoặc không tải được
        if not temp_map_data:
            print("Lỗi GameController: map_info không hợp lệ hoặc không tải được.")
            # Tạo một map_data rỗng để chương trình không bị crash
            self.map_data = {
                'layout': [], 'walls': [], 'snake_start': [], 'food_start': []
            }
            # Thiết lập các thuộc tính ở trạng thái lỗi, nhưng BẮT BUỘC PHẢI TỒN TẠI
            self.snake_data = {'body': [], 'direction': 'RIGHT'}
            self.food_data = []
            self.steps = 0
            self.outcome = "Map Load Error"
            # Không dùng 'return' ở đây để __init__ có thể hoàn thành
        else:
            # 3. Nếu map hợp lệ, tiếp tục như bình thường
            self.map_data = temp_map_data
            
            # Tự động tạo 'layout' nếu không có (trường hợp map từ editor)
            if not self.map_data.get('layout'):
                width = config.AI_MAP_WIDTH_TILES
                height = config.AI_MAP_HEIGHT_TILES
                self.map_data['layout'] = ["." * width for _ in range(height)]
            
            # Gọi reset() để thiết lập trạng thái game ban đầu
            self.reset()

    def reset(self):
        """
            Thiết lập lại game về trạng thái ban đầu với logic thức ăn tuần tự.
        """
        self.snake_data = snake_logic.create_snake_from_map(self.map_data)
        self.steps = 0
        self.outcome = "Playing"

        # --- THAY ĐỔI LOGIC THỨC ĂN ---
        # 1. Lưu lại toàn bộ danh sách tọa độ thức ăn ban đầu.
        self.food_spawn_list = self.map_data.get('food_start', [])
        # 2. Theo dõi vị trí của viên thức ăn tiếp theo.
        self.next_food_index = 0
        # 3. Xóa danh sách thức ăn đang hoạt động.
        self.food_data = []

        # 4. Nếu có thức ăn trong danh sách chờ, thêm viên đầu tiên vào game.
        if self.next_food_index < len(self.food_spawn_list):
            first_food_pos = self.food_spawn_list[self.next_food_index]
            self.food_data.append({'pos': first_food_pos})
            self.next_food_index += 1

    def get_state(self):
        """Lấy trạng thái hiện tại của game để giao diện có thể vẽ."""
        return {'snake': self.snake_data, 'food': self.food_data, 'steps': self.steps, 'outcome': self.outcome}

    # --- HÀM SET_DIRECTION VỚI LOGIC ĐÃ SỬA ---
    def set_direction(self, direction):
        """
        Nhận lệnh đổi hướng từ người chơi và kiểm tra tính hợp lệ.
        Phiên bản này chống lại lỗi bấm phím nhanh gây tự va chạm.
        """
        # Nếu game đã kết thúc hoặc rắn quá ngắn, không làm gì cả
        if self.outcome != "Playing" or len(self.snake_data['body']) < 2:
            return

        # --- LOGIC MỚI: Xác định hướng di chuyển THỰC TẾ ---
        # So sánh vị trí của đầu và cổ để biết rắn đang thực sự đi hướng nào
        head = self.snake_data['body'][0]
        neck = self.snake_data['body'][1]
        
        true_current_dir = None
        if head[1] < neck[1]:
            true_current_dir = 'UP'
        elif head[1] > neck[1]:
            true_current_dir = 'DOWN'
        elif head[0] < neck[0]:
            true_current_dir = 'LEFT'
        elif head[0] > neck[0]:
            true_current_dir = 'RIGHT'
        # ---------------------------------------------------

        # Kiểm tra hướng đi mới với hướng đi THỰC TẾ
        if direction == 'UP' and true_current_dir != 'DOWN':
            self.snake_data['direction'] = 'UP'
        elif direction == 'DOWN' and true_current_dir != 'UP':
            self.snake_data['direction'] = 'DOWN'
        elif direction == 'LEFT' and true_current_dir != 'RIGHT':
            self.snake_data['direction'] = 'LEFT'
        elif direction == 'RIGHT' and true_current_dir != 'LEFT':
            self.snake_data['direction'] = 'RIGHT'
    
    def update(self):
        """
        Cập nhật 1 bước game cho người chơi.
        Thứ tự kiểm tra được tối ưu hóa.
        """
        if self.outcome != "Playing":
            return

        # --- BƯỚC 1: KIỂM TRA TÌNH HUỐNG BỊ KẸT (NÊN KIỂM TRA ĐẦU TIÊN) ---
        head = self.snake_data['body'][0]
        possible_moves = algorithm_helpers.get_valid_neighbors(head, self.map_data, self.snake_data['body'])
        if not possible_moves:
            self.outcome = "Stuck"
            return

        # --- BƯỚC 2: "NHÌN TRƯỚC" HƯỚNG ĐI TIẾP THEO ---
        next_head_pos = snake_logic.get_next_head_position(self.snake_data)

        # --- BƯỚC 3: XỬ LÝ VA CHẠM CHO HƯỚNG ĐI ĐÓ ---
        # 3a. Nếu va chạm với tường -> THUA
        if next_head_pos in self.map_data['walls']:
            self.outcome = "Stuck"
            return

        # 3b. Nếu va chạm với thân -> THUA
        if next_head_pos in self.snake_data['body']:
            self.outcome = "Stuck"
            return
        
        # --- BƯỚC 4: NẾU AN TOÀN, THỰC HIỆN DI CHUYỂN ---
        self.snake_data['body'].insert(0, next_head_pos)
        self.steps += 1
        
        # 5. Kiểm tra ăn mồi
        eaten_food = next((food for food in self.food_data if food['pos'] == next_head_pos), None)
        if eaten_food:
            # Xóa viên thức ăn vừa ăn khỏi danh sách hoạt động.
            self.food_data.remove(eaten_food)

            # Kiểm tra xem còn thức ăn trong danh sách chờ không.
            if self.next_food_index < len(self.food_spawn_list):
                # Nếu còn, lấy tọa độ viên tiếp theo và thêm vào game.
                next_food_pos = self.food_spawn_list[self.next_food_index]
                self.food_data.append({'pos': next_food_pos})
                self.next_food_index += 1
            else:
                # Nếu không còn, người chơi đã thắng.
                self.outcome = "Completed"
        else:
            # Nếu không ăn mồi, xóa đốt đuôi cuối cùng để rắn di chuyển
            self.snake_data['body'].pop()
            
    def update_by_path_step(self, next_pos):
        """Cập nhật 1 bước game cho AI theo path."""
        if self.outcome != "Playing": return
            
        self.snake_data['body'].insert(0, next_pos)
        self.steps += 1
        
        head = self.snake_data['body'][0]
        if snake_logic.check_collision(self.snake_data, self.map_data):
            self.outcome = "Stuck"
            return
            
        eaten_food = next((food for food in self.food_data if food['pos'] == head), None)
        if eaten_food:
            self.food_data.remove(eaten_food)

            # Kiểm tra xem còn thức ăn trong danh sách chờ không.
            if self.next_food_index < len(self.food_spawn_list):
                # Nếu còn, lấy tọa độ viên tiếp theo và thêm vào game.
                next_food_pos = self.food_spawn_list[self.next_food_index]
                self.food_data.append({'pos': next_food_pos})
                self.next_food_index += 1
            else:
                # Nếu không còn, AI đã thắng.
                self.outcome = "Completed"
        else:
            # Nếu không ăn mồi và game vẫn đang tiếp diễn, cắt đuôi
            if self.outcome == "Playing":
                self.snake_data['body'].pop()