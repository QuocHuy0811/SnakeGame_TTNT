"""
    Các biến dùng chung
"""
# --- Kích thước & Cài đặt màn hình ---
TILE_SIZE = 20  # Kích thước mỗi ô vuông trong map (QUAN TRỌNG)
MAP_WIDTH_TILES = 40
MAP_HEIGHT_TILES = 30

# Thêm một panel bên phải để hiển thị thông tin
PANEL_WIDTH = 300 

# Tự động tính toán kích thước màn hình
SCREEN_WIDTH = MAP_WIDTH_TILES * TILE_SIZE + PANEL_WIDTH 
SCREEN_HEIGHT = MAP_HEIGHT_TILES * TILE_SIZE  + 50           

FPS = 60
GAME_TITLE = "23110103 _ Đoàn Quốc Huy && 23110124 _ Đoàn Ngọc Mạnh --- Rắn Săn Mồi ---"

# --- Đường dẫn ---
MAPS_DIR = "Maps"
FONT_PATH = "Assets/Fonts/Tomorrow-Regular.ttf"

# --- Màu sắc ---
COLORS = {
    'bg': (60, 65, 80),          # Màu nền chính
    'btn': (3, 169, 244),         # Màu nút bấm
    'btn_hover': (2, 136, 209),     # Màu nút khi di chuột qua (tôi đã thêm vào)
    'btn_disabled': (85, 90, 105),
    'combo': (0, 200, 83),
    'depth_bg': (0, 150, 136),
    'box': (75, 80, 95),
    'white': (240, 240, 240),      # Màu văn bản chính
    'white_bg': (255, 255, 255),
    'text_dark': (40, 42, 54),
    'black': (30, 30, 30),
    'border': (100, 105, 120),
    'line': (200, 200, 200),
    'title': (0, 255, 255),        # Màu tiêu đề game
    'highlight': (0, 255, 0),
}

# --- Cài đặt Font ---
TITLE_FONT_SIZE = 60
BUTTON_FONT_SIZE = 30
LABEL_FONT_SIZE = 35