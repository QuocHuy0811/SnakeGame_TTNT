"""
    Quản lý vị trí thức ăn, tạo vị trí mới, vẽ thức ăn
"""
import random
import config
import pygame

# Biến global để lưu trữ sprite thức ăn, tránh tải lại ảnh
_food_sprite = None

def load_food_sprite():
    """
    Hàm helper để tải, thay đổi kích thước và lưu trữ sprite thức ăn.
    Nó chỉ thực hiện tải ảnh một lần duy nhất.
    """
    global _food_sprite
    if _food_sprite is None: # Chỉ tải nếu chưa được tải
        try:
            # Tải ảnh gốc
            original_image = pygame.image.load('Assets/Images/Food/apple.png').convert_alpha()
            # Thay đổi kích thước ảnh cho vừa với TILE_SIZE và lưu lại
            _food_sprite = pygame.transform.scale(original_image, (config.TILE_SIZE, config.TILE_SIZE))
            print("Tải sprite thức ăn thành công.")
        except pygame.error as e:
            print(f"LỖI: Không thể tải sprite thức ăn. Sẽ vẽ hình vuông thay thế. Lỗi: {e}")
            _food_sprite = "error" # Đánh dấu là đã cố tải nhưng bị lỗi
    return _food_sprite

def create_food_from_map(map_data):
    """
    Tạo ra một danh sách các dictionary thức ăn dựa trên thông tin từ map_data.
    """
    # map_data['food_start'] là một list các tọa độ (x, y)
    # Tạo một danh sách rỗng để chứa kết quả cuối cùng
    food_list = []

    # Lấy danh sách các tọa độ thức ăn ban đầu từ map_data
    # Nếu key 'food_start' không tồn tại, nó sẽ dùng một danh sách rỗng để không bị lỗi
    start_positions = map_data.get('food_start', [])

    # Lặp qua từng tọa độ (ví dụ: pos = (10, 5)) trong danh sách tọa độ ban đầu
    for pos in start_positions:
        # Với mỗi tọa độ, tạo một dictionary mới có dạng {'pos': (10, 5)}
        new_food_item = {'pos': pos}
        
        # Thêm dictionary vừa tạo vào danh sách kết quả
        food_list.append(new_food_item)

    # Trả về danh sách thức ăn đã được định dạng lại
    return food_list

def spawn_random_food(map_data, snake_data):
    """
    Tạo ra một viên thức ăn ở một vị trí ngẫu nhiên hợp lệ.
    Vị trí hợp lệ là ô không phải tường và không bị thân rắn chiếm đóng.
    """
    # 1. Lấy tất cả các vị trí có thể có trên map
    width = len(map_data['layout'][0])
    height = len(map_data['layout'])
    all_positions = set((x, y) for x in range(width) for y in range(height))
    
    # 2. Lấy tất cả các vị trí đã bị chiếm
    wall_positions = set(map_data.get('walls', []))
    snake_positions = set(tuple(segment) for segment in snake_data.get('body', []))
    occupied_positions = wall_positions.union(snake_positions)
    
    # 3. Tìm các vị trí còn trống
    available_positions = list(all_positions - occupied_positions)
    
    # 4. Chọn một vị trí ngẫu nhiên từ các ô còn trống
    if available_positions:
        chosen_pos = random.choice(available_positions)
        return {'pos': chosen_pos, 'type': 'normal'}
    
    # Nếu không còn chỗ trống, trả về None (báo hiệu chiến thắng)
    return None