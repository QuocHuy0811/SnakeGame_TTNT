"""
    Giao diện lịch sử 
"""
import pygame
import config
from UI import UI_helpers
from GameLogic import game_helpers

def run_history_screen(screen, clock):
    running = True
    title_font = pygame.font.Font(config.FONT_PATH, 48)
    header_font = pygame.font.Font(config.FONT_PATH, 24)
    item_font = pygame.font.Font(config.FONT_PATH, 20)
    
    back_button = UI_helpers.create_button(config.SCREEN_WIDTH/2 - 100, config.SCREEN_HEIGHT - 80, 200, 50, "Back")
    history_data = game_helpers.load_game_history()
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        UI_helpers.update_button_hover_state(back_button, mouse_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); exit()
            if UI_helpers.handle_button_events(event, back_button): running = False

        screen.fill(config.COLORS['bg'])
        UI_helpers.draw_text("Game History", title_font, config.COLORS['title'], screen, config.SCREEN_WIDTH/2, 60)

        table_start_y = 140
        col_map_x = config.SCREEN_WIDTH * 0.12
        col_algo_x = config.SCREEN_WIDTH * 0.28
        col_steps_x = config.SCREEN_WIDTH * 0.43
        col_time_x = config.SCREEN_WIDTH * 0.58
        col_search_x = config.SCREEN_WIDTH * 0.75
        col_outcome_x = config.SCREEN_WIDTH * 0.90

        header_color = config.COLORS['highlight']
        UI_helpers.draw_text("Map", header_font, header_color, screen, col_map_x, table_start_y)
        UI_helpers.draw_text("Algorithm", header_font, header_color, screen, col_algo_x, table_start_y)
        UI_helpers.draw_text("Steps", header_font, header_color, screen, col_steps_x, table_start_y)
        UI_helpers.draw_text("Ani. Time", header_font, header_color, screen, col_time_x, table_start_y) # Đổi tên cho rõ
        # <-- CẬP NHẬT: Đổi tên cột cho rõ nghĩa
        UI_helpers.draw_text("Total Search", header_font, header_color, screen, col_search_x, table_start_y)
        UI_helpers.draw_text("Outcome", header_font, header_color, screen, col_outcome_x, table_start_y)

        if not history_data:
            UI_helpers.draw_text("No history yet.", item_font, config.COLORS['white'], screen, config.SCREEN_WIDTH/2, 300)
        else:
            for i, record in enumerate(history_data[-15:]):
                item_y = table_start_y + (i + 1) * 35
                UI_helpers.draw_text(str(record['map']), item_font, config.COLORS['white'], screen, col_map_x, item_y)
                UI_helpers.draw_text(str(record['algorithm']), item_font, config.COLORS['white'], screen, col_algo_x, item_y)
                UI_helpers.draw_text(str(record['steps']), item_font, config.COLORS['white'], screen, col_steps_x, item_y)
                UI_helpers.draw_text(str(record['time']), item_font, config.COLORS['white'], screen, col_time_x, item_y)
                
                search_time = record.get('total_search_time', 'N/A')
                UI_helpers.draw_text(str(search_time), item_font, config.COLORS['white'], screen, col_search_x, item_y)
                
                outcome = record.get('outcome', 'N/A')
                outcome_color = config.COLORS['highlight'] if outcome == "Completed" else (255, 100, 100)
                UI_helpers.draw_text(str(outcome), item_font, outcome_color, screen, col_outcome_x, item_y)

        UI_helpers.draw_button(screen, back_button)
        pygame.display.flip()
        clock.tick(config.FPS)