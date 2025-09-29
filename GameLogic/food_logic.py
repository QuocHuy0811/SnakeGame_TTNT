"""
    Quản lý vị trí thức ăn, tạo vị trí mới, vẽ thức ăn
"""
import config
import pygame

# Biến toàn cục để lưu trữ sprite thức ăn đã được tải và thay đổi kích thước
# Giúp chúng ta không phải tải lại ảnh từ ổ cứng ở mỗi frame.
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
    return [{'pos': pos} for pos in map_data.get('food_start', [])]
