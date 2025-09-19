"""
    Chạy chương trình
"""
import pygame
import config
from UI.MainMenu import main_menu
from UI.AI_screen import run_ai_game 
from UI.AI_vs_human_screen import run_ai_vs_human_screen

def main():
    """Hàm chính để chạy game."""
    pygame.init()
    screen = pygame.display.set_mode((config.S  CREEN_WIDTH, config.SCREEN_HEIGHT))
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
                game_state = "MAIN_MENU"
                run_ai_game(screen, clock, selected_map) 
            
            elif selected_mode == "AI_VS_HUMAN":
                run_ai_vs_human_screen(screen, clock, selected_map)
                game_state = "MAIN_MENU" # Quay về menu sau khi chơi xong
            else: break
            
        clock.tick(config.FPS)
    
    pygame.quit()

if __name__ == '__main__':
    main()