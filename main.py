"""
    Chạy chương trình
"""
import pygame
import config
from UI.MainMenu import main_menu
from UI import AI_screen, AI_vs_human_screen # Import gọn gàng hơn

def main():
    """Hàm chính để chạy game."""
    pygame.init()
    
    # THÊM NHẠC NỀN: Khởi tạo mixer
    pygame.mixer.init()

    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.GAME_TITLE)
    clock = pygame.time.Clock()

    try:
        # THÊM NHẠC NỀN: Tải file nhạc
        pygame.mixer.music.load("Assets/Music/NhacGame.mp3")

        # THÊM NHẠC NỀN: Cài đặt âm lượng (từ 0.0 đến 1.0)
        pygame.mixer.music.set_volume(0.5) # 50% âm lượng

        # THÊM NHẠC NỀN: Bật nhạc, lặp lại vô tận (loops=-1)
        pygame.mixer.music.play(loops=-1)

    except pygame.error as e:
        print(f"Lỗi không thể tải hoặc phát file nhạc: {e}")
        # Nếu không có file nhạc, game vẫn chạy bình thường
    
    while True:
        # Luôn bắt đầu hoặc quay về từ Main Menu
        selected_mode, selected_map = main_menu.run_main_menu(screen)
        
        # Nếu người dùng đóng cửa sổ ở Main Menu, selected_mode có thể là None
        if selected_mode is None:
            break # Thoát khỏi vòng lặp chính và kết thúc game

        print(f"Bắt đầu game với: Chế độ={selected_mode}, Map={selected_map}")
        
        if selected_mode == "AI":
            # Chạy màn hình AI, sau khi màn hình này kết thúc, vòng lặp while sẽ
            # tự động chạy lại và hiển thị lại main menu.
            AI_screen.run_ai_game(screen, clock, selected_map)
        
        elif selected_mode == "AI_VS_HUMAN":
            # Tương tự với màn hình AI vs Human
            AI_vs_human_screen.run_ai_vs_human_screen(screen, clock, selected_map)

    pygame.quit()

if __name__ == '__main__':
    main()