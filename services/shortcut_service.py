import os
import platform
import subprocess
from typing import Tuple

def create_desktop_shortcut(
    target_path: str,
    icon_path: str,
    app_name: str = "AURA AI Logo Generator",
    description: str = "AURA AI Logo & Visual Generator"
) -> Tuple[bool, str]:
    """
    Tự động tạo Desktop Shortcut kèm Icon ngoài màn hình chính (Desktop).
    Hỗ trợ cả Windows (.lnk) và Linux (.desktop).
    """
    sys_name = platform.system()
    abs_target = os.path.abspath(target_path)
    abs_icon = os.path.abspath(icon_path) if icon_path else ""
    working_dir = os.path.dirname(abs_target)

    if sys_name == "Windows":
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop_path, f"{app_name}.lnk")
            
            # Sử dụng PowerShell tạo shortcut WScript.Shell
            ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{abs_target}'
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.Description = '{description}'
if ('{abs_icon}' -and (Test-Path '{abs_icon}')) {{
    $Shortcut.IconLocation = '{abs_icon}'
}}
$Shortcut.Save()
"""
            cmd = ["powershell", "-NoProfile", "-Command", ps_script]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and os.path.exists(shortcut_path):
                return True, f"Đã tạo shortcut thành công tại: {shortcut_path}"
            return False, f"Lỗi tạo shortcut Windows: {res.stderr}"
        except Exception as e:
            return False, f"Lỗi ngoại lệ tạo shortcut Windows: {str(e)}"

    elif sys_name == "Linux":
        try:
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            os.makedirs(desktop_dir, exist_ok=True)
            desktop_file = os.path.join(desktop_dir, f"{app_name.lower().replace(' ', '_')}.desktop")

            content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Comment={description}
Exec="{abs_target}"
Icon={abs_icon}
Path={working_dir}
Terminal=false
StartupNotify=true
Categories=Graphics;Utility;
"""
            with open(desktop_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Cấp quyền thực thi
            os.chmod(desktop_file, 0o755)
            return True, f"Đã tạo shortcut Linux tại: {desktop_file}"
        except Exception as e:
            return False, f"Lỗi tạo shortcut Linux: {str(e)}"

    return False, f"Hệ điều hành {sys_name} chưa được hỗ trợ tạo shortcut tự động."
