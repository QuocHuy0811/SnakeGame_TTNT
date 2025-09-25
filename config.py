"""
    Các biến dùng chung
"""
# --- Kích thước & Cài đặt màn hình ---
TILE_SIZE = 20  # Kích thước mỗi ô vuông trong map (QUAN TRỌNG)
FPS = 60
GAME_TITLE = "Nhóm 15: 23110103 _ Đoàn Quốc Huy && 23110124 _ Đoàn Ngọc Mạnh --- Rắn Săn Mồi ---"    
# --- Đường dẫn ---
MAPS_DIR = "Maps"
FONT_PATH = "Assets/Fonts/Tomorrow-Regular.ttf"

# MAP_WIDTH_TILES = 40
# MAP_HEIGHT_TILES = 30


# PANEL_WIDTH = 300

# # Tự động tính toán kích thước màn hình
# SCREEN_WIDTH = MAP_WIDTH_TILES * TILE_SIZE + PANEL_WIDTH + 200
# SCREEN_HEIGHT = MAP_HEIGHT_TILES * TILE_SIZE + 60

# ======================================================================
# --- CÀI ĐẶT CHO MÀN HÌNH AI (1 MAP) ---
# ======================================================================
AI_MAP_WIDTH_TILES = 40
AI_MAP_HEIGHT_TILES = 30
AI_PANEL_WIDTH = 300
# Chiều rộng màn hình AI = Rộng Map + Rộng Panel + Khoảng đệm
AI_SCREEN_WIDTH = (AI_MAP_WIDTH_TILES * TILE_SIZE) + AI_PANEL_WIDTH + 200
# Chiều cao màn hình AI = Cao Map + Khoảng đệm
AI_SCREEN_HEIGHT = (AI_MAP_HEIGHT_TILES * TILE_SIZE) + 60

# ======================================================================
# --- CÀI ĐẶT CHO MÀN HÌNH AI vs HUMAN (2 MAP) ---
# ======================================================================
DUAL_MAP_WIDTH_TILES = 30
DUAL_MAP_HEIGHT_TILES = 30
DUAL_CONTROL_PANEL_WIDTH = 250
# Chiều rộng màn hình 1v1 = Map Trái + Panel Giữa + Map Phải
DUAL_SCREEN_WIDTH = (DUAL_MAP_WIDTH_TILES * TILE_SIZE) * 2 + DUAL_CONTROL_PANEL_WIDTH
# Chiều cao màn hình 1v1 = Cao Map + Khu vực thông tin
DUAL_SCREEN_HEIGHT = (DUAL_MAP_HEIGHT_TILES * TILE_SIZE) + 200

# ======================================================================
# --- KÍCH THƯỚC CỬA SỔ GAME CHÍNH ---
# ======================================================================
# Lấy kích thước lớn nhất để cửa sổ game không cần thay đổi kích thước
SCREEN_WIDTH = max(AI_SCREEN_WIDTH, DUAL_SCREEN_WIDTH)
SCREEN_HEIGHT = max(AI_SCREEN_HEIGHT, DUAL_SCREEN_HEIGHT)



# --- Màu sắc ---
COLORS = {
    'bg': (60, 65, 80),             # Màu nền chính
    'btn': (3, 169, 244),           # Màu nút bấm
    'btn_hover': (2, 136, 209),     # Màu nút khi di chuột qua (tôi đã thêm vào)
    'btn_disabled': (85, 90, 105),
    'combo': (0, 200, 83),
    'depth_bg': (0, 150, 136),
    'box': (75, 80, 95),
    'white': (240, 240, 240),       # Màu văn bản chính
    'white_bg': (255, 255, 255),
    'text_dark': (40, 42, 54),
    'black': (30, 30, 30),
    'border': (100, 105, 120),
    'line': (200, 200, 200),
    'title': (0, 255, 255),         # Màu tiêu đề game
    'highlight': (0, 255, 0),
    'food': (255, 215, 0),
}

# --- Cài đặt Font ---
TITLE_FONT_SIZE = 60
BUTTON_FONT_SIZE = 30
LABEL_FONT_SIZE = 35