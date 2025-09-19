"""
    Chạy chương trình
"""
import pygame
import config
from UI.MainMenu import main_menu
from UI.AI_screen import run_ai_game 

def main():
    """Hàm chính để chạy game."""
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.GAME_TITLE)
    clock = pygame.time.Clock()

    game_state = "MAIN_MENU"    
    
    while True:
        if game_state == "MAIN_MENU":
            selected_mode, selected_map = main_menu.run_main_menu(screen)
            print(f"Bắt đầu game với: Chế độ={selected_mode}, Map={selected_map}")
            
            # TODO: Dựa vào lựa chọn để chuyển sang màn hình game
            # Ví dụ:
            if selected_mode == "AI":
                game_state = "AI_GAME"
                run_ai_game(screen, clock, selected_map) 
            
            # Tạm thời thoát game sau khi chọn để bạn kiểm tra
            break 
        
        # Sau này bạn có thể thêm các trạng thái khác
        # elif game_state == "GAME_OVER":
        #     run_game_over_screen(screen)
        #     game_state = "MAIN_MENU" # Quay về menu
            
        clock.tick(config.FPS)
    
    pygame.quit()

if __name__ == '__main__':
    main()