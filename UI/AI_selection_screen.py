"""
    Cửa sổ chọn thuật toán
"""
import pygame
import config
from UI import UI_helpers

def run_algorithm_selection(screen):
    """
    Hàm này chạy một vòng lặp riêng để hiển thị cửa sổ chọn thuật toán.
    Nó sẽ trả về tên thuật toán được chọn, hoặc None nếu người dùng đóng.
    """
    # --- 1. KHỞI TẠO ---
    title_font = pygame.font.Font(config.FONT_PATH, 32)
    clock = pygame.time.Clock()
    algorithms = ["Player", "BFS", "DFS", "A*", "UCS", "Greedy", "IDS", "OnlineSearch"]
    
    # Kích thước và vị trí của cửa sổ pop-up
    popup_width, popup_height = 400, 500
    popup_x = (config.SCREEN_WIDTH - popup_width) / 2
    popup_y = (config.SCREEN_HEIGHT - popup_height) / 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    
    # Tạo các nút cho từng thuật toán
    scroll_y = 0
    scroll_speed = 30
    buttons = []
    button_width, button_height = 300, 50
    button_padding = 15
    content_height = len(algorithms) * (button_height + button_padding)
    
    for i, algo in enumerate(algorithms):
        btn_x = (popup_width - button_width) / 2
        btn_y = button_padding + i * (button_height + button_padding)
        buttons.append(UI_helpers.create_button(btn_x, btn_y, button_width, button_height, algo))
        
    close_button = UI_helpers.create_button(popup_x + popup_width - 50, popup_y + 10, 40, 40, "X")

    # Khu vực có thể cuộn bên trong pop-up
    scroll_area_y = popup_y + 90
    scroll_area_height = popup_height - 120
    scroll_area_rect = pygame.Rect(popup_x, scroll_area_y, popup_width, scroll_area_height)
    
    # --- 2. VÒNG LẶP CỦA POP-UP ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        mouse_in_scroll_area = scroll_area_rect.collidepoint(mouse_pos)
        adjusted_mouse_pos = (mouse_pos[0] - popup_x, mouse_pos[1] - scroll_area_y + scroll_y)

        if mouse_in_scroll_area:
            for btn in buttons: 
                UI_helpers.update_button_hover_state(btn, adjusted_mouse_pos)
        else:
            for btn in buttons: 
                btn['is_hovered'] = False

        UI_helpers.update_button_hover_state(close_button, mouse_pos)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Xử lý cuộn chuột
            if event.type == pygame.MOUSEWHEEL and mouse_in_scroll_area:
                scroll_y -= event.y * scroll_speed
                # Giới hạn cuộn để không cuộn ra ngoài nội dung
                max_scroll = content_height - scroll_area_height
                if max_scroll < 0: max_scroll = 0 # Nếu nội dung ngắn hơn view
                scroll_y = max(0, min(scroll_y, max_scroll))
            
            # Xử lý click chuột
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_button['rect'].collidepoint(mouse_pos):
                    return None # Đóng cửa sổ
                
                # Chỉ xử lý click các nút thuật toán nếu click trong vùng cuộn
                if mouse_in_scroll_area:
                    for btn in buttons:
                        # Điều chỉnh tọa độ nút tạm thời để kiểm tra va chạm
                        btn['rect'].top -= scroll_y
                        if btn['rect'].collidepoint(adjusted_mouse_pos):
                             btn['rect'].top += scroll_y # Trả lại vị trí
                             return btn['text'] # Trả về tên thuật toán
                        btn['rect'].top += scroll_y # Trả lại vị trí
            
            # Nếu nhấn nút X, đóng pop-up và không trả về gì
            if UI_helpers.handle_button_events(event, close_button):
                return None 

            # Kiểm tra xem có nút thuật toán nào được nhấn không
            for btn in buttons:
                if UI_helpers.handle_button_events(event, btn):
                    return btn['text'] # Trả về tên thuật toán

        # --- 3. VẼ LÊN MÀN HÌNH ---
        # Vẽ một lớp nền mờ che màn hình chính
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        # overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        
        # Vẽ nền của cửa sổ pop-up
        pygame.draw.rect(screen, config.COLORS['white_bg'], popup_rect, border_radius=20)
        
        # Vẽ tiêu đề và các nút
        UI_helpers.draw_text("Select Mode", title_font, config.COLORS['text_dark'], screen, popup_rect.centerx, popup_y + 50)
        UI_helpers.draw_button(screen, close_button)

        # Tạo một bề mặt tạm để cắt (clip) những gì nằm ngoài vùng cuộn
        scroll_surface = screen.subsurface(scroll_area_rect)
        scroll_surface.fill(config.COLORS['white_bg']) # Nền cho vùng cuộn
        
        for btn in buttons:
            # Dịch vị trí của nút theo offset cuộn
            btn['rect'].topleft = (btn['rect'].left, btn['rect'].top - scroll_y)
            UI_helpers.draw_button(scroll_surface, btn)
            # Trả lại vị trí ban đầu cho lần tính toán tiếp theo
            btn['rect'].topleft = (btn['rect'].left, btn['rect'].top + scroll_y)

        pygame.display.flip()
        clock.tick(config.FPS)