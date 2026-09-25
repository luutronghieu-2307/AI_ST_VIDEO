"""
build_bootstrap_exe.py – Đóng gói EXE Launcher với token GitHub đã obfuscate.

Quy trình:
1. Đọc GITHUB_TOKEN từ .env
2. Sinh file services/_embedded_token.py chứa token đã obfuscate
3. Chạy PyInstaller đóng gói (KHÔNG kèm license.key nữa)
4. Dọn dẹp file _embedded_token.py sau khi build
"""
import os
import subprocess
import sys

EMBEDDED_TOKEN_FILE = os.path.join("services", "_embedded_token.py")


def _read_env_token() -> str:
    """Đọc GITHUB_TOKEN từ file .env hoặc biến môi trường."""
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        return token

    env_path = ".env"
    if not os.path.exists(env_path):
        return ""
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return ""


def generate_embedded_token() -> bool:
    """Sinh file services/_embedded_token.py chứa token đã obfuscate."""
    token = _read_env_token()
    if not token:
        print("⚠️ Không tìm thấy GITHUB_TOKEN trong .env hoặc biến môi trường.")
        print("   EXE sẽ yêu cầu token qua .env khi chạy (không khuyến nghị khi phân phối).")
        return False

    from services.token_obfuscator import obfuscate_token

    obfuscated = obfuscate_token(token)
    content = (
        '"""File tự sinh bởi build_bootstrap_exe.py – KHÔNG chỉnh sửa thủ công."""\n'
        f'OBFUSCATED_TOKEN = "{obfuscated}"\n'
    )
    with open(EMBEDDED_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Đã sinh token obfuscated tại {EMBEDDED_TOKEN_FILE}")
    return True


def cleanup_embedded_token() -> None:
    """Xóa file token tạm sau khi build xong."""
    if os.path.exists(EMBEDDED_TOKEN_FILE):
        os.remove(EMBEDDED_TOKEN_FILE)
        print(f"🧹 Đã dọn dẹp {EMBEDDED_TOKEN_FILE}")


def build_exe() -> None:
    """Đóng gói file EXE siêu nhẹ bằng PyInstaller với Icon H-AURA."""
    print("=" * 60)
    print("⚡ BẮT ĐẦU ĐÓNG GÓI BOOTSTRAP LAUNCHER CHO AURA AI")
    print("=" * 60)

    # Đảm bảo đã có file ICON/LOGO_HAURA.ico
    ico_path = os.path.join("ICON", "LOGO_HAURA.ico")
    if not os.path.exists(ico_path):
        from scripts.convert_icon import convert_png_to_ico
        convert_png_to_ico(os.path.join("ICON", "LOGO_HAURA.png"), ico_path)

    # Cài đặt pyinstaller nếu chưa có
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("📦 Đang cài đặt PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Sinh token obfuscated trước khi build
    has_token = generate_embedded_token()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--icon={ico_path}",
        "--name=AURA_Launcher",
        "--add-data=templates:templates",
        "--add-data=ICON:ICON",
        "--add-data=data:data",
        "--add-data=core:core",
        "--add-data=models:models",
        "--add-data=routers:routers",
        "--add-data=services:services",
        "--add-data=main.py:.",
        "--add-data=requirements.txt:.",
        "launcher.py",
    ]

    print(f"🚀 Đang chạy lệnh đóng gói: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    finally:
        # Luôn dọn dẹp file token tạm dù build thành công hay thất bại
        if has_token:
            cleanup_embedded_token()

    print("=" * 60)
    print("✅ ĐÓNG GÓI THÀNH CÔNG! Thư mục phân phối nằm tại: dist/AURA_Launcher")
    print("=" * 60)


if __name__ == "__main__":
    build_exe()
