import os
from PIL import Image

def convert_png_to_ico(png_path: str, ico_path: str) -> bool:
    """Chuyển đổi file PNG thành file ICO đa kích thước cho Windows."""
    if not os.path.exists(png_path):
        print(f"❌ Không tìm thấy file: {png_path}")
        return False
    
    img = Image.open(png_path)
    # Các kích thước icon chuẩn của Windows
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    print(f"✅ Đã tạo thành công icon ICO tại: {ico_path}")
    return True

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    png = os.path.join(base_dir, "ICON", "LOGO_HAURA.png")
    ico = os.path.join(base_dir, "ICON", "LOGO_HAURA.ico")
    convert_png_to_ico(png, ico)
