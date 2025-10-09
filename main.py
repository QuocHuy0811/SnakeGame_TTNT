"""
    Chạy chương trình
"""
import pygame
import config
from UI.MainMenu import main_menu
from UI import AI_screen, AI_vs_human_screen

def main():
    """
        Hàm chính để chạy game.
    """
    # Khởi tạo tất cả các module của Pygame
    pygame.init()
    # Khởi tạo module âm thanh
    pygame.mixer.init()

    # Tạo cửa sổ game với kích thước đã được tính toán trong config
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    # Đặt tiêu đề cho cửa sổ game
    pygame.display.set_caption(config.GAME_TITLE)
    # Tạo một đối tượng Clock để kiểm soát FPS
    clock = pygame.time.Clock()

    try:
        #Tải file nhạc
        pygame.mixer.music.load("Assets/Sounds/NhacGame.mp3")
        # Đặt âm lượng (giá trị từ 0.0 đến 1.0)
        pygame.mixer.music.set_volume(0.5) # 50% âm lượng
        # Bật nhạc, lặp lại vô tận (loops=-1)
        pygame.mixer.music.play(loops=-1)

    except pygame.error as e:
        print(f"Lỗi không thể tải hoặc phát file nhạc: {e}")
    
    while True:
        # 1. Luôn bắt đầu bằng cách gọi màn hình Main Menu
        # Hàm này sẽ chạy và chỉ trả về kết quả khi người dùng chọn một chế độ
        selected_mode, selected_map = main_menu.run_main_menu(screen)
        
        # Nếu người dùng đóng cửa sổ ở Main Menu, chương trình sẽ kết thúc
        if selected_mode is None:
            break

        print(f"Bắt đầu game với: Chế độ={selected_mode}, Map={selected_map}")
        
        # 2. Dựa vào lựa chọn của người dùng, gọi màn hình game tương ứng
        if selected_mode == "AI":
            # Chạy màn hình AI. Sau khi màn hình này kết thúc (người dùng bấm "Back"),
            # vòng lặp 'while True' sẽ lặp lại và hiển thị lại Main Menu.
            AI_screen.run_ai_game(screen, clock, selected_map)
        
        elif selected_mode == "AI_VS_HUMAN":
            # Tương tự với màn hình AI vs Human
            AI_vs_human_screen.run_ai_vs_human_screen(screen, clock, selected_map)
    
    # Thoát khỏi Pygame một cách an toàn khi vòng lặp chính kết thúc
    pygame.quit()

if __name__ == '__main__':
    main()