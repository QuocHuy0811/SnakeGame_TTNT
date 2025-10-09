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
        # Hàm khởi tạo, được gọi khi một đối tượng GameController mới được tạo.
        
        # 1. Tải dữ liệu map
        # Kiểm tra xem map_info là tên file (string) hay là dữ liệu map (dictionary)
        temp_map_data = None
        if isinstance(map_info, str):
            # Nếu là tên file, gọi hàm để tải từ file .txt
            temp_map_data = map_logic.load_map_data(map_info)
        else:
            # Nếu đã là dictionary (ví dụ từ map editor), sử dụng trực tiếp
            temp_map_data = map_info

        # 2. Xử lý trường hợp không tải được map
        if not temp_map_data:
            print("Lỗi GameController: map_info không hợp lệ hoặc không tải được.")
            # Tạo một map_data rỗng để chương trình không bị crash
            self.map_data = {'layout': [], 'walls': [], 'snake_start': [], 'food_start': []}
            # Thiết lập các thuộc tính ở trạng thái lỗi, nhưng BẮT BUỘC PHẢI TỒN TẠI
            self.snake_data = {'body': [], 'direction': 'RIGHT'}
            self.food_data = []
            self.steps = 0
            self.outcome = "Map Load Error"
        else:
            # 3. Nếu map hợp lệ, tiếp tục như bình thường
            self.map_data = temp_map_data
            
            # Tự động tạo 'layout' nếu map được tạo từ editor (chưa có layout)
            if not self.map_data.get('layout'):
                width = config.AI_MAP_WIDTH_TILES
                height = config.AI_MAP_HEIGHT_TILES
                self.map_data['layout'] = ["." * width for _ in range(height)]
            
            # Gọi reset() để thiết lập trạng thái game ban đầu
            self.reset()

    def reset(self):
        """
            Thiết lập lại game về trạng thái ban đầu.
        """
        self.snake_data = snake_logic.create_snake_from_map(self.map_data)
        self.food_data = food_logic.create_food_from_map(self.map_data)
        self.steps = 0
        self.outcome = "Playing"    # Trạng thái game đang diễn ra

    def get_state(self):
        """Lấy trạng thái hiện tại của game để giao diện có thể vẽ."""
        return {
            'snake': self.snake_data, 
            'food': self.food_data, 
            'steps': self.steps, 
            'outcome': self.outcome
        }

    def set_direction(self, direction):
        """
        Nhận lệnh đổi hướng từ người chơi và kiểm tra tính hợp lệ chống đi lùi.
        """
        # Nếu game đã kết thúc hoặc rắn quá ngắn, không làm gì cả
        if self.outcome != "Playing" or len(self.snake_data['body']) < 2:
            return

        # Xác định hướng di chuyển thực tế của rắn bằng cách so sánh vị trí đầu và cổ
        head = self.snake_data['body'][0]
        neck = self.snake_data['body'][1]
        
        true_current_dir = None
        if head[1] < neck[1]: true_current_dir = 'UP'
        elif head[1] > neck[1]: true_current_dir = 'DOWN'
        elif head[0] < neck[0]: true_current_dir = 'LEFT'
        elif head[0] > neck[0]: true_current_dir = 'RIGHT'

        # Chỉ cập nhật hướng mới nếu nó không phải là hướng ngược lại của hướng đi thực tế
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
            Cập nhật một bước game (dành cho người chơi hoặc AI online).
            Hàm này mô phỏng một lần di chuyển của rắn.
        """
        # Nếu game không còn trong trạng thái "Playing", không làm gì cả
        if self.outcome != "Playing":
            return

        # --- BƯỚC 1: KIỂM TRA TÌNH HUỐNG BỊ KẸT ---
        head = self.snake_data['body'][0]
        possible_moves = algorithm_helpers.get_valid_neighbors(head, self.map_data, self.snake_data['body'])
        if not possible_moves:
            # Nếu không có nước đi nào, rắn bị kẹt hoàn toàn.
            self.outcome = "Stuck"
            return

        # --- BƯỚC 2: TÍNH TOÁN VỊ TRÍ TIẾP THEO ---
        # Dựa trên hướng đi hiện tại của rắn.
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
        
        # --- BƯỚC 4: THỰC HIỆN DI CHUYỂN ---
        # Thêm đầu mới vào danh sách thân rắn
        self.snake_data['body'].insert(0, next_head_pos)
        self.steps += 1
        
        # --- BƯỚC 5: KIỂM TRA ĂN MỒI ---
        # Tìm xem có thức ăn nào ở vị trí đầu mới không
        # Bắt đầu bằng cách giả định rằng không ăn được mồi
        eaten_food = None

        # Lặp qua từng viên thức ăn trong danh sách self.food_data
        for food in self.food_data:
            # Kiểm tra xem vị trí của viên thức ăn có trùng với vị trí đầu mới của rắn không
            if food['pos'] == next_head_pos:
                # Nếu có, gán viên thức ăn đó cho biến eaten_food
                eaten_food = food
                # Dừng vòng lặp ngay lập tức vì đã tìm thấy mồi rồi, không cần tìm nữa
                break

        if eaten_food:
            # Nếu có, xóa thức ăn đó khỏi danh sách
            self.food_data.remove(eaten_food)
            if not self.food_data:
                # Kiểm tra xem đã ăn hết thức ăn chưa (điều kiện thắng)
                self.outcome = "Completed"
        else:
            # Nếu không ăn mồi, xóa đốt đuôi cuối cùng để rắn di chuyển
            self.snake_data['body'].pop()
            
    def update_by_path_step(self, next_pos):
        """
            Cập nhật một bước game cho AI theo một tọa độ cho trước trong 'path'.
            Hàm này đơn giản hơn `update` vì hướng đi đã được quyết định sẵn.
        """
        if self.outcome != "Playing": return
        
        # 1. Di chuyển rắn đến vị trí tiếp theo
        self.snake_data['body'].insert(0, next_pos)
        self.steps += 1
        
        # 2. Kiểm tra va chạm (dù path đã tính là an toàn, vẫn kiểm tra lại cho chắc)
        head = self.snake_data['body'][0]
        if snake_logic.check_collision(self.snake_data, self.map_data):
            self.outcome = "Stuck"
            return
        
        # 3. Kiểm tra ăn mồi
        eaten_food = next((food for food in self.food_data if food['pos'] == head), None)
        if eaten_food:
            self.food_data.remove(eaten_food)
            if not self.food_data:
                self.outcome = "Completed"
        else:
            # Nếu không ăn mồi và game vẫn đang tiếp diễn, cắt đuôi
            if self.outcome == "Playing":
                self.snake_data['body'].pop()