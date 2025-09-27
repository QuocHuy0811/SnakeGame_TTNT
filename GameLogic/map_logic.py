"""
    Hàm vẽ map
"""
import os
import config

def load_map_data(map_filename):
    """
    Tải dữ liệu map từ file .txt.
    Hàm này trả về một dictionary chứa layout và vị trí các đối tượng.
    """
    map_data = {
        'layout': [], # <-- THÊM KEY QUAN TRỌNG NÀY
        'walls': [],
        'snake_start': [],
        'food_start': []
    }
    
    full_path = f"Maps/{map_filename}"
    
    if not os.path.exists(full_path):
        print(f"Lỗi: Không tìm thấy file map '{full_path}'")
        return None # Trả về None nếu không tìm thấy file

    with open(full_path, 'r') as f:
        lines = f.readlines()
        if not lines:
            print(f"Lỗi: File map '{full_path}' bị trống.")
            return None # Trả về None nếu file trống

        for y, line in enumerate(lines):
            clean_line = line.strip()
            map_data['layout'].append(clean_line) # <-- LƯU LẠI CẤU TRÚC MAP
            for x, char in enumerate(clean_line):
                if char == '#':
                    map_data['walls'].append((x, y))
                elif char == 'x':
                    map_data['snake_start'].append((x, y))
                elif char == '*':
                    map_data['food_start'].append((x, y))
    
    # Sắp xếp lại vị trí của rắn để đảm bảo đúng thứ tự đầu-thân
    # Cách này giả định đầu rắn là ký tự 'x' ở trên cùng và/hoặc bên trái nhất
    map_data['snake_start'].sort(key=lambda pos: (pos[1], pos[0]))
    
    return map_data