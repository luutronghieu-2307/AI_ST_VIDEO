"""
launcher_gui.py - Giao diện Tkinter Dark Glassmorphism cho Aura AI Launcher.
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from services.hardware_service import get_hwid
from services.license_service import verify_license_key_remote, bind_machine, check_activation
from services.shortcut_service import create_desktop_shortcut
from launcher_core.server_runner import wait_for_server, start_uvicorn_thread, open_browser


class AuraLauncherApp:
    def __init__(self, root: tk.Tk, app_dir: str):
        self.root = root
        self.app_dir = app_dir
        self.root.title("AURA AI - Khởi động & Quản lý Bản quyền")
        self.root.geometry("540x580")
        self.root.resizable(False, False)
        self.root.configure(bg="#0b0f19")

        self.server_running = False
        self.hwid = get_hwid()
        self._set_window_icon()
        self._build_ui()
        self._initial_check()

    def _set_window_icon(self):
        ico_path = os.path.join(self.app_dir, "ICON", "LOGO_HAURA.ico")
        png_path = os.path.join(self.app_dir, "ICON", "LOGO_HAURA.png")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass
        elif os.path.exists(png_path):
            try:
                img = tk.PhotoImage(file=png_path)
                self.root.iconphoto(False, img)
            except Exception:
                pass

    def _build_ui(self):
        header_frame = tk.Frame(self.root, bg="#0b0f19")
        header_frame.pack(fill="x", pady=(20, 10))

        tk.Label(header_frame, text="⚡ AURA AI LOGO GENERATOR", font=("Segoe UI", 16, "bold"), fg="#38bdf8", bg="#0b0f19").pack()
        tk.Label(header_frame, text="Hệ thống Khởi động & Quản lý Bản quyền Phần cứng (HWID)", font=("Segoe UI", 9), fg="#94a3b8", bg="#0b0f19").pack(pady=2)

        card = tk.Frame(self.root, bg="#111827", highlightbackground="#1f2937", highlightthickness=1, padx=20, pady=16)
        card.pack(fill="x", padx=24, pady=8)

        tk.Label(card, text="Mã Máy Tính (HWID):", font=("Segoe UI", 9, "bold"), fg="#cbd5e1", bg="#111827").pack(anchor="w")
        hwid_row = tk.Frame(card, bg="#111827")
        hwid_row.pack(fill="x", pady=(4, 12))

        self.hwid_entry = tk.Entry(hwid_row, font=("Consolas", 10), bg="#1e293b", fg="#38bdf8", bd=0, relief="flat", highlightthickness=1, highlightbackground="#334155")
        self.hwid_entry.insert(0, self.hwid)
        self.hwid_entry.config(state="readonly")
        self.hwid_entry.pack(side="left", fill="x", expand=True, ipady=4)

        tk.Button(hwid_row, text="Sao chép", font=("Segoe UI", 8), bg="#334155", fg="#ffffff", bd=0, relief="flat", padx=10, command=self._copy_hwid).pack(side="left", padx=(6, 0))

        tk.Label(card, text="License Key Bản Quyền:", font=("Segoe UI", 9, "bold"), fg="#cbd5e1", bg="#111827").pack(anchor="w")
        self.key_entry = tk.Entry(card, font=("Consolas", 10), bg="#1e293b", fg="#ffffff", bd=0, relief="flat", highlightthickness=1, highlightbackground="#334155")
        self.key_entry.pack(fill="x", pady=(4, 6), ipady=5)
        self.key_entry.bind("<KeyRelease>", lambda e: self._on_key_change())

        self.status_lbl = tk.Label(card, text="⏳ Đang kiểm tra trạng thái...", font=("Segoe UI", 9), fg="#94a3b8", bg="#111827")
        self.status_lbl.pack(anchor="w", pady=(2, 0))

        self.prog_bar = ttk.Progressbar(self.root, mode="determinate")
        self.prog_bar.pack(fill="x", padx=24, pady=(6, 2))
        self.prog_lbl = tk.Label(self.root, text="", font=("Segoe UI", 8), fg="#64748b", bg="#0b0f19")
        self.prog_lbl.pack()

        btn_frame = tk.Frame(self.root, bg="#0b0f19")
        btn_frame.pack(fill="x", padx=24, pady=(12, 10))

        self.launch_btn = tk.Button(btn_frame, text="🚀 Khởi Động Ứng Dụng", font=("Segoe UI", 12, "bold"), bg="#0284c7", fg="#ffffff", bd=0, relief="flat", padx=20, pady=10, state="disabled", command=self._on_launch_clicked)
        self.launch_btn.pack(fill="x")

        self.web_btn = tk.Button(btn_frame, text="🌐 Mở Trình Duyệt (Web)", font=("Segoe UI", 9), bg="#1e293b", fg="#38bdf8", bd=0, relief="flat", pady=6, state="disabled", command=lambda: open_browser("http://127.0.0.1:8000"))
        self.web_btn.pack(fill="x", pady=(8, 0))

    def _copy_hwid(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.hwid)
        messagebox.showinfo("Đã sao chép", "Đã sao chép mã máy HWID vào bộ nhớ tạm!")

    def _on_key_change(self):
        key = self.key_entry.get().strip()
        if not key:
            self.status_lbl.config(text="Vui lòng nhập License Key để tiếp tục.", fg="#94a3b8")
            self.launch_btn.config(state="disabled", bg="#334155")
            return

        self.status_lbl.config(text="⏳ Đang xác thực với máy chủ...", fg="#38bdf8")
        self.root.update_idletasks()

        is_valid, message = verify_license_key_remote(key)
        if is_valid:
            self.status_lbl.config(text=f"✅ {message}", fg="#4ade80")
            self.launch_btn.config(state="normal", bg="#0284c7")
        else:
            self.status_lbl.config(text=f"❌ {message}", fg="#f87171")
            self.launch_btn.config(state="disabled", bg="#334155")

    def _initial_check(self):
        is_active, msg = check_activation()
        if is_active:
            self.status_lbl.config(text="✅ Bản quyền đã kích hoạt trên máy này!", fg="#4ade80")
            self.key_entry.insert(0, "●●●●●●●●●●●● (Đã kích hoạt)")
            self.key_entry.config(state="disabled")
            self.launch_btn.config(state="normal", bg="#0284c7")
        else:
            self.status_lbl.config(text="⚠️ " + msg + " Nhập License Key để xác thực với máy chủ.", fg="#fbbf24")

        exe_target = sys.executable if getattr(sys, 'frozen', False) else os.path.join(self.app_dir, "AURA_Launcher.exe")
        ico_path = os.path.join(self.app_dir, "ICON", "LOGO_HAURA.ico")
        create_desktop_shortcut(exe_target, ico_path)

    def _on_launch_clicked(self):
        self.launch_btn.config(state="disabled", text="⏳ Đang khởi động máy chủ...")
        threading.Thread(target=self._launch_worker, daemon=True).start()

    def _launch_worker(self):
        is_active, _ = check_activation()
        if not is_active:
            key = self.key_entry.get().strip()
            ok, bind_msg = bind_machine(key)
            if not ok:
                self.root.after(0, lambda: messagebox.showerror("Lỗi bản quyền", bind_msg))
                self.root.after(0, lambda: self.launch_btn.config(state="normal", text="🚀 Khởi Động Ứng Dụng"))
                return

        self._update_progress("Đang khởi động Server FastAPI...", 0.6)
        if not self.server_running:
            start_uvicorn_thread(self.app_dir)
            self.server_running = True

        self._update_progress("Đang kiểm tra kết nối cổng 8000...", 0.8)
        ready = wait_for_server("127.0.0.1", 8000, timeout=20)

        if ready:
            self._update_progress("Server đang chạy tại http://127.0.0.1:8000", 1.0)
            open_browser("http://127.0.0.1:8000")
            self.root.after(0, lambda: self.launch_btn.config(text="✅ Đang Chạy Server", bg="#16a34a", state="disabled"))
            self.root.after(0, lambda: self.web_btn.config(state="normal", bg="#0284c7", fg="#ffffff"))
        else:
            self.server_running = False
            self._update_progress("Không thể kết nối tới server cục bộ.", 0.0)
            self.root.after(0, lambda: messagebox.showerror("Lỗi kết nối", "Không thể khởi động cổng 8000."))
            self.root.after(0, lambda: self.launch_btn.config(state="normal", text="🚀 Thử lại", bg="#0284c7"))

    def _update_progress(self, msg: str, val: float):
        self.root.after(0, lambda: self.prog_lbl.config(text=msg))
        self.root.after(0, lambda: self.prog_bar.config(value=int(val * 100)))
