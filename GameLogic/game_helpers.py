# GameLogic/game_helpers.py
import json
import os

HISTORY_FILE = "game_history.json"

def save_game_result(map_name, algorithm, steps, time, total_search_time, outcome):
    """Lưu kết quả của một lần chạy vào file history."""
    
    new_result = {
        "map": map_name.replace('.txt', ''),
        "algorithm": algorithm,
        "steps": steps,
        "time": round(time, 4),
        "total_search_time": round(total_search_time, 4), # Dữ liệu về tổng thời gian tìm kiếm
        "outcome": outcome
    }

    history = load_game_history()
    history.append(new_result)

    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        print(f"Đã lưu kết quả: {new_result}")
    except IOError as e:
        print(f"Lỗi khi ghi file lịch sử: {e}")

def load_game_history():
    """Tải lịch sử các lần chạy từ file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            if os.path.getsize(HISTORY_FILE) == 0:
                return []
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Lỗi khi đọc file lịch sử: {e}")
        return []