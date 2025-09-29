"""
    Giao diện chính
"""
import pygame
import sys
import os
import config
from UI import UI_helpers
from UI.MainMenu import background_effects


def run_main_menu(screen):
    """
        Chạy màn hình main menu và trả về lựa chọn của người dùng.
        Sử dụng combobox và định vị tương đối để giao diện gọn gàng, cân đối.
    """
    
    # --- 1. KHỞI TẠO ---
    # Khởi tạo các đối tượng font chữ.
    title_font = pygame.font.Font(config.FONT_PATH, config.TITLE_FONT_SIZE)
    label_font = pygame.font.Font(config.FONT_PATH, config.LABEL_FONT_SIZE)
    
    # Tải danh sách các file map từ thư mục.
    map_files = []
    if os.path.exists(config.MAPS_DIR):
        map_files = sorted([f for f in os.listdir(config.MAPS_DIR) if f.endswith('.txt')])
    
    # Khởi tạo hiệu ứng nền
    background_effects.init_background(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, 1000)
    
    # --- 2. QUẢN LÝ TRẠNG THÁI ---
    # Lưu map đang được chọn, mặc định là map đầu tiên.
    selected_map_name = map_files[0] if map_files else "No Maps Found"
    # Trạng thái mở/đóng của combobox.
    is_combobox_open = False

    # --- 3. TÍNH TOÁN VỊ TRÍ TƯƠNG ĐỐI ---
    button_width = 250
    button_height = 60
    
    # Xác định tọa độ X cho cột trái (Mode) và cột phải (Map).
    left_column_x = config.SCREEN_WIDTH / 4
    right_column_x = config.SCREEN_WIDTH * 3 / 4

    # Xác định tọa độ Y chung cho các thành phần.
    labels_y = config.SCREEN_HEIGHT / 3.5
    buttons_start_y = config.SCREEN_HEIGHT / 2.5
    
    # --- 4. TẠO CÁC NÚT BẤM ---
    # Tạo các nút chọn chế độ ở cột trái.
    mode_buttons = [
        UI_helpers.create_button(left_column_x - button_width / 2, buttons_start_y, button_width, button_height, "AI"),
        UI_helpers.create_button(left_column_x - button_width / 2, buttons_start_y + 80, button_width, button_height, "AI vs Human")
    ]
    
    # Tạo nút header cho combobox ở cột phải.
    combobox_header_button = UI_helpers.create_button(right_column_x - button_width / 2, buttons_start_y, button_width, button_height, f"Map: {selected_map_name}")
    
    # Tạo các nút lựa chọn map (chỉ hiện khi combobox mở).
    map_option_buttons = []
    if map_files:
        for i, map_name in enumerate(map_files):
            option_y = combobox_header_button['rect'].bottom + i * 50
            map_option_buttons.append(UI_helpers.create_button(right_column_x - button_width / 2, option_y, 250, 50, map_name))

    # --- 5. VÒNG LẶP CHÍNH ---
    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Cập nhật trạng thái hover.
        for btn_data in mode_buttons:
            UI_helpers.update_button_hover_state(btn_data, mouse_pos)
        UI_helpers.update_button_hover_state(combobox_header_button, mouse_pos)
        if is_combobox_open:
            for btn_data in map_option_buttons:
                UI_helpers.update_button_hover_state(btn_data, mouse_pos)
        
        # Xử lý sự kiện.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Ưu tiên xử lý combobox nếu nó đang mở
                if is_combobox_open:
                    # Kiểm tra xem có click vào header để đóng không
                    if combobox_header_button['rect'].collidepoint(mouse_pos):
                        is_combobox_open = False
                    else: # Nếu không, kiểm tra các option
                        for btn in map_option_buttons:
                            if btn['rect'].collidepoint(mouse_pos):
                                selected_map_name = btn['text'] + '.txt' # Thêm lại .txt
                                combobox_header_button['text'] = f"Map: {btn['text']}"
                                is_combobox_open = False
                                break
                else: # Nếu combobox đang đóng
                    if combobox_header_button['rect'].collidepoint(mouse_pos):
                        is_combobox_open = True
                    
                    # Kiểm tra các nút chọn chế độ
                    for btn in mode_buttons:
                        if btn['rect'].collidepoint(mouse_pos):
                            if btn['text'] == "AI":
                                return "AI", selected_map_name
                            elif btn['text'] == "AI vs Human":
                                return "AI_VS_HUMAN", selected_map_name
            
        # --- 6. VẼ LÊN MÀN HÌNH ---
        background_effects.draw_background(screen)
        
        # Vẽ các tiêu đề và nhãn.
        title_y = config.SCREEN_HEIGHT / 8
        UI_helpers.draw_text("Snake Game", title_font, config.COLORS['title'], screen, config.SCREEN_WIDTH / 2, title_y)
        UI_helpers.draw_text("Play Mode:", label_font, config.COLORS['white'], screen, left_column_x, labels_y)
        UI_helpers.draw_text("Map:", label_font, config.COLORS['white'], screen, right_column_x, labels_y)
        
        # Vẽ các nút chọn chế độ.
        for btn_data in mode_buttons:
            UI_helpers.draw_button(screen, btn_data)

        # Vẽ combobox.
        UI_helpers.draw_button(screen, combobox_header_button)
        if is_combobox_open:
            for btn_data in map_option_buttons:
                UI_helpers.draw_button(screen, btn_data)

        # Cập nhật màn hình.
        pygame.display.flip()