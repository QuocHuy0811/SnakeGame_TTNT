import pygame
import config
from UI import UI_helpers

def run_algorithm_selection(screen):
    # --- 1. KHỞI TẠO ---
    title_font = pygame.font.Font(config.FONT_PATH, 32)
    clock = pygame.time.Clock()

    algorithms = [
        "Player", "BFS", "DFS", "IDS", "UCS", 
        "A* (Manhattan)", "A* (Euclidean)", 
        "Greedy (Manhattan)", "Greedy (Euclidean)", 
        "HillClimbing", "BeamSearch", "OnlineSearch"
    ]
    
    popup_width, popup_height = 400, 500
    popup_x = (config.SCREEN_WIDTH - popup_width) / 2
    popup_y = (config.SCREEN_HEIGHT - popup_height) / 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
    
    buttons = []
    button_width, button_height = 300, 50
    button_padding = 15
    content_height = len(algorithms) * (button_height + button_padding)
    
    for i, algo in enumerate(algorithms):
        btn_x = popup_x + (popup_width - button_width) / 2
        # Tọa độ Y ban đầu của nút so với toàn màn hình
        btn_y_initial = popup_y + 90 + button_padding + i * (button_height + button_padding)
        buttons.append(UI_helpers.create_button(btn_x, btn_y_initial, button_width, button_height, algo))
        
    close_button = UI_helpers.create_button(popup_x + popup_width - 50, popup_y + 10, 40, 40, "X")

    scroll_y = 0
    scroll_speed = 30
    scroll_area_y = popup_y + 90
    scroll_area_height = popup_height - 120
    scroll_area_rect = pygame.Rect(popup_x, scroll_area_y, popup_width, scroll_area_height)
    
    # --- 2. VÒNG LẶP CỦA POP-UP ---
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_in_scroll_area = scroll_area_rect.collidepoint(mouse_pos)

        # Cập nhật trạng thái hover
        UI_helpers.update_button_hover_state(close_button, mouse_pos)
        for btn in buttons:
            # Tạo rect tạm thời để kiểm tra hover, đã tính đến cuộn
            temp_btn_rect = pygame.Rect(btn['rect'].x, btn['rect'].y - scroll_y, btn['rect'].width, btn['rect'].height)
            if mouse_in_scroll_area and temp_btn_rect.collidepoint(mouse_pos):
                btn['is_hovered'] = True
            else:
                btn['is_hovered'] = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.MOUSEWHEEL and mouse_in_scroll_area:
                scroll_y -= event.y * scroll_speed
                max_scroll = max(0, content_height - scroll_area_height)
                scroll_y = max(0, min(scroll_y, max_scroll))
            
            # --- SỬA LỖI: GỘP TOÀN BỘ LOGIC CLICK VÀO MỘT CHỖ ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_button['rect'].collidepoint(mouse_pos):
                    return None 
                
                if mouse_in_scroll_area:
                    for btn in buttons:
                        # Tạo rect tạm thời để kiểm tra click, đã tính đến cuộn
                        temp_btn_rect = pygame.Rect(btn['rect'].x, btn['rect'].y - scroll_y, btn['rect'].width, btn['rect'].height)
                        if temp_btn_rect.collidepoint(mouse_pos):
                            return btn['text'] # Trả về đúng tên thuật toán

        # --- 3. VẼ LÊN MÀN HÌNH ---
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        screen.blit(overlay, (0,0))
        
        pygame.draw.rect(screen, config.COLORS['white_bg'], popup_rect, border_radius=20)
        UI_helpers.draw_text("Select Mode", title_font, config.COLORS['text_dark'], screen, popup_rect.centerx, popup_y + 50)
        UI_helpers.draw_button(screen, close_button)

        # Vẽ các nút trong vùng có thể cuộn
        scroll_surface = screen.subsurface(scroll_area_rect.copy())
        scroll_surface.fill(config.COLORS['white_bg'])
        
        for btn in buttons:
            # Tạo một rect tạm thời để vẽ, không thay đổi rect gốc của nút
            draw_rect = btn['rect'].copy()
            # Dịch chuyển vị trí vẽ dựa trên tọa độ của scroll_surface và scroll_y
            draw_rect.x -= scroll_area_rect.x
            draw_rect.y -= (scroll_area_rect.y + scroll_y)
            
            # Tạo một bản sao của nút để vẽ
            temp_btn_to_draw = btn.copy()
            temp_btn_to_draw['rect'] = draw_rect
            UI_helpers.draw_button(scroll_surface, temp_btn_to_draw)

        pygame.display.flip()
        clock.tick(config.FPS)