import hashlib
import os
import platform
import subprocess
import uuid

def _get_raw_machine_id() -> str:
    """Thu thập thông tin định danh phần cứng máy tính đa nền tảng."""
    sys_name = platform.system()
    raw_id = ""

    if sys_name == "Windows":
        try:
            import winreg
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Cryptography")
            raw_id, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
        except Exception:
            pass

        if not raw_id:
            try:
                cmd = "powershell -Command (Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"
                out = subprocess.check_output(cmd, shell=True, text=True).strip()
                if out:
                    raw_id = out
            except Exception:
                pass

    elif sys_name == "Linux":
        for path in ["/etc/machine-id", "/var/lib/dbus/machine-id"]:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            raw_id = content
                            break
                except Exception:
                    pass

    if not raw_id:
        # Fallback dựa trên MAC node và tên thiết bị
        node = uuid.getnode()
        raw_id = f"{node}-{platform.node()}-{platform.processor()}"

    return raw_id


def get_hwid() -> str:
    """
    Tạo mã phần cứng chuẩn hóa (Hardware ID / HWID).
    Định dạng: AURA-XXXX-XXXX-XXXX (16 ký tự)
    """
    raw = _get_raw_machine_id()
    salt = "AURA_AI_HWID_SALT_2026"
    digest = hashlib.sha256(f"{raw}:{salt}".encode("utf-8")).hexdigest().upper()
    part1 = digest[0:4]
    part2 = digest[4:8]
    part3 = digest[8:12]
    part4 = digest[12:16]
    return f"AURA-{part1}-{part2}-{part3}-{part4}"
