"""
    Các biến dùng chung
"""
# --- CÀI ĐẶT CHUNG ---
TILE_SIZE = 20      # Kích thước (pixel) của mỗi ô vuông trong game
FPS = 60            # Số khung hình trên giây, quyết định độ mượt của game
GAME_TITLE = "Nhóm 15: 23110103 _ Đoàn Quốc Huy && 23110124 _ Đoàn Ngọc Mạnh --- Rắn Săn Mồi ---"

# --- ĐƯỜNG DẪN ---
MAPS_DIR = "Maps"
FONT_PATH = "Assets/Fonts/Tomorrow-Regular.ttf"

# ======================================================================
# --- CÀI ĐẶT KÍCH THƯỚC CHO TỪNG MÀN HÌNH ---
# ======================================================================

# --- Màn hình AI (1 map) ---
AI_MAP_WIDTH_TILES = 30
AI_MAP_HEIGHT_TILES = 30
AI_PANEL_WIDTH = 300
# Chiều rộng màn hình AI = Rộng Map (pixel) + Rộng Panel điều khiển + Khoảng đệm 2 bên
AI_SCREEN_WIDTH = (AI_MAP_WIDTH_TILES * TILE_SIZE) + AI_PANEL_WIDTH + 200
# Chiều cao màn hình AI = Cao Map (pixel) + Khoảng đệm trên dưới
AI_SCREEN_HEIGHT = (AI_MAP_HEIGHT_TILES * TILE_SIZE) + 60

# --- Màn hình AI vs Human (2 map) ---
DUAL_MAP_WIDTH_TILES = 30
DUAL_MAP_HEIGHT_TILES = 30
DUAL_CONTROL_PANEL_WIDTH = 250
# Chiều rộng = Map Trái + Panel Giữa + Map Phải
DUAL_SCREEN_WIDTH = (DUAL_MAP_WIDTH_TILES * TILE_SIZE) * 2 + DUAL_CONTROL_PANEL_WIDTH
# Chiều cao màn hình 1v1 = Cao Map + Khu vực thông tin
DUAL_SCREEN_HEIGHT = (DUAL_MAP_HEIGHT_TILES * TILE_SIZE) + 200

# --- Màn hình Map Editor ---
EDITOR_MAP_WIDTH_TILES = 40       # Chiều rộng map trong editor (số ô)
EDITOR_MAP_HEIGHT_TILES = 30      # Chiều cao map trong editor (số ô)
EDITOR_PANEL_WIDTH = 250          # Chiều rộng panel điều khiển bên trái
EDITOR_INSTRUCTIONS_WIDTH = 250   # Chiều rộng panel hướng dẫn bên phải
PADDING = 50                      # Khoảng cách giữa các cột
# Chiều rộng = Panel Trái + Map + Panel Phải + 2 lần đệm
EDITOR_SCREEN_WIDTH = EDITOR_PANEL_WIDTH + (EDITOR_MAP_WIDTH_TILES * TILE_SIZE) + EDITOR_INSTRUCTIONS_WIDTH + (PADDING * 2)
EDITOR_SCREEN_HEIGHT = (EDITOR_MAP_HEIGHT_TILES * TILE_SIZE) + 100

# ======================================================================
# --- KÍCH THƯỚC CỬA SỔ GAME CHÍNH ---
# ======================================================================
# Lấy kích thước lớn nhất để cửa sổ game không cần thay đổi kích thước
SCREEN_WIDTH = max(AI_SCREEN_WIDTH, DUAL_SCREEN_WIDTH)
SCREEN_HEIGHT = max(AI_SCREEN_HEIGHT, DUAL_SCREEN_HEIGHT)

# ======================================================================
# --- CÀI ĐẶT MÀU SẮC ---
# ======================================================================
COLORS = {
    'bg': (60, 65, 80),             # Màu nền chính
    'btn': (3, 169, 244),           # Màu nút bấm mặc định
    'btn_hover': (2, 136, 209),     # Màu nút khi di chuột qua
    'btn_disabled': (85, 90, 105),  # Màu nút khi bị vô hiệu hóa
    'combo': (0, 200, 83),          # Màu cho combobox
    'box': (75, 80, 95),            # Màu của các ô box
    'white': (240, 240, 240),       # Màu văn bản chính (trắng ngà)
    'white_bg': (255, 255, 255),    # Màu nền trắng (cho panel)
    'text_dark': (40, 42, 54),      # Màu văn bản tối trên nền sáng
    'black': (30, 30, 30),          # Màu nền đen (cho map editor)
    'border': (100, 105, 120),      # Màu đường kẻ lưới
    'line': (200, 200, 200),        # Màu đường kẻ
    'title': (0, 255, 255),         # Màu tiêu đề game (cyan)
    'highlight': (0, 255, 0),       # Màu nhấn mạnh (xanh lá)
    'food': (255, 215, 0),          # Màu thức ăn (vàng)
}

# ======================================================================
# --- CÀI ĐẶT FONT CHỮ ---
# ======================================================================
TITLE_FONT_SIZE = 60
BUTTON_FONT_SIZE = 30
LABEL_FONT_SIZE = 35