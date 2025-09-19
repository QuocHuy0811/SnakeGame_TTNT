import os
import config

def load_map_data(map_filename):
    """
    Tải dữ liệu map từ một file .txt.
    Hàm này sẽ đọc file và trả về một dictionary chứa vị trí của các đối tượng.
    """
    map_data = {
        'walls': [],
        'snake_start': [],
        'food_start': []
    }
    
    # Tạo đường dẫn đầy đủ đến file map
    full_path = os.path.join(config.MAPS_DIR, map_filename)
    
    if not os.path.exists(full_path):
        print(f"Lỗi: Không tìm thấy file map '{full_path}'")
        return map_data # Trả về dữ liệu rỗng

    with open(full_path, 'r') as f:
        for y, line in enumerate(f):
            for x, char in enumerate(line.strip()):
                if char == '#':
                    map_data['walls'].append((x, y))
                elif char == 'x':
                    map_data['snake_start'].append((x, y))
                elif char == '*':
                    map_data['food_start'].append((x, y))
    
    # Sắp xếp lại vị trí của rắn để đảm bảo đúng thứ tự đầu-thân
    map_data['snake_start'].sort()
    
    return map_data