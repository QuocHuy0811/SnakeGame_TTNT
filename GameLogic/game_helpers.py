"""
    Hàm phụ trong GameLogic
"""

# Biến toàn cục để lưu trữ lịch sử trong phiên làm việc hiện tại
session_history = []

def save_game_result(map_name, algorithm, steps, time, total_search_time, outcome, visited_count, generated_count):
    """Lưu kết quả (bao gồm visited và generated) vào danh sách lịch sử của phiên."""
    
    new_result = {
        "map": map_name.replace('.txt', ''),
        "algorithm": algorithm,
        "steps": steps,
        "time": round(time, 4),
        "total_search_time": round(total_search_time, 4),
        "outcome": outcome,
        "visited": visited_count,
        "generated": generated_count
    }

    session_history.append(new_result)
    print(f"Đã lưu kết quả tạm thời: {new_result}")


def load_game_history():
    """Tải lịch sử các lần chạy từ bộ nhớ của phiên hiện tại."""
    # Trả về danh sách đang lưu trong bộ nhớ
    return session_history