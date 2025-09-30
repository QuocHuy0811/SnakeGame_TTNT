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

# ======================================================================
# --- CÀI ĐẶT CHO MÀN HÌNH AI (1 MAP) ---
# ======================================================================
AI_MAP_WIDTH_TILES = 30
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
# --- CÀI ĐẶT CHO MAP EDITOR ---
# ======================================================================
EDITOR_MAP_WIDTH_TILES = 30  # Chiều rộng map trong editor
EDITOR_MAP_HEIGHT_TILES = 30 # Chiều cao map trong editor
EDITOR_PANEL_WIDTH = 250     # Chiều rộng panel điều khiển của editor

# Công thức tính kích thước cửa sổ cho editor
EDITOR_SCREEN_WIDTH = EDITOR_PANEL_WIDTH + (EDITOR_MAP_WIDTH_TILES * TILE_SIZE) + 100
EDITOR_SCREEN_HEIGHT = (EDITOR_MAP_HEIGHT_TILES * TILE_SIZE) + 100

# ======================================================================
# --- KÍCH THƯỚC CỬA SỔ GAME CHÍNH ---
# ======================================================================
# Lấy kích thước lớn nhất để cửa sổ game không cần thay đổi kích thước
SCREEN_WIDTH = max(AI_SCREEN_WIDTH, DUAL_SCREEN_WIDTH)
SCREEN_HEIGHT = max(AI_SCREEN_HEIGHT, DUAL_SCREEN_HEIGHT)

# ======================================================================
# --- CÀI ĐẶT CHO HÌNH NỀN ĐỘNG --- (Thêm vào)
# ======================================================================
PARTICLE_COUNT = 50           # Số lượng hạt
PARTICLE_MAX_VELOCITY = 0.5   # Tốc độ di chuyển tối đa của hạt
PARTICLE_RADIUS = 3           # Kích thước hạt
CONNECT_DISTANCE = 120        # Khoảng cách tối đa giữa 2 hạt để nối đường


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

    # --- Màu cho hình nền động --- (Thêm vào)
    'particle_color': (150, 150, 255), # Màu của hạt
    'line_color': (100, 100, 200),     # Màu của đường nối
    'bg_dark_blue': (15, 15, 40),      # Màu nền xanh đậm
}

# --- Cài đặt Font ---
TITLE_FONT_SIZE = 60
BUTTON_FONT_SIZE = 30
LABEL_FONT_SIZE = 35