import tkinter as tk
from tkinter import messagebox
import os
import csv


class TaoTKPage:
    def __init__(self, master, app_manager, from_admin=False):
        self.master = master
        self.app_manager = app_manager
        self.from_admin = from_admin


        self.entry_username = None
        self.entry_gmail = None
        self.entry_password = None
        self.entry_confirm = None

        self.master.configure(bg="#f5f5f5")
        self.config()
        self.view()

    def config(self):
        self.master.title("Tạo tài khoản mới")
        self.master.geometry("400x550")

    def view(self):
        header_color = "#6F4E37"
        header = tk.Frame(self.master, bg=header_color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ ĐĂNG KÝ THÀNH VIÊN",
                 font=("Arial", 16, "bold"), fg="white", bg=header_color).pack(pady=15)

        frame = tk.Frame(self.master, bg="#f5f5f5")
        frame.pack(pady=30)

        lbl_style = {"font": ("Arial", 10, "bold"), "bg": "#f5f5f5", "fg": "#333"}

        tk.Label(frame, text="Username:", **lbl_style).grid(row=0, column=0, pady=10, sticky="e")
        self.entry_username = tk.Entry(frame, font=("Arial", 11), width=25)
        self.entry_username.grid(row=0, column=1, pady=10, padx=10)

        tk.Label(frame, text="Gmail:", **lbl_style).grid(row=1, column=0, pady=10, sticky="e")
        self.entry_gmail = tk.Entry(frame, font=("Arial", 11), width=25)
        self.entry_gmail.grid(row=1, column=1, pady=10, padx=10)

        tk.Label(frame, text="Password:", **lbl_style).grid(row=2, column=0, pady=10, sticky="e")
        self.entry_password = tk.Entry(frame, show="*", font=("Arial", 11), width=25)
        self.entry_password.grid(row=2, column=1, pady=10, padx=10)

        tk.Label(frame, text="Xác nhận MK:", **lbl_style).grid(row=3, column=0, pady=10, sticky="e")
        self.entry_confirm = tk.Entry(frame, show="*", font=("Arial", 11), width=25)
        self.entry_confirm.grid(row=3, column=1, pady=10, padx=10)

        btn_frame = tk.Frame(self.master, bg="#f5f5f5")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Xác nhận tạo", command=self.tao_tk,
                  bg="#6F4E37", fg="white", font=("Arial", 10, "bold"),
                  width=15, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

        if self.from_admin:
            cmd_back = self.app_manager.show_quanlytk_page
        else:
            cmd_back = self.app_manager.show_login_page

        tk.Button(btn_frame, text="Quay lại", command=cmd_back,
                  bg="#6F4E37", fg="white", font=("Arial", 10, "bold"),
                  width=15, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

    def tao_tk(self):
        user = self.entry_username.get().strip()
        gmail = self.entry_gmail.get().strip()
        pw = self.entry_password.get().strip()
        confirm = self.entry_confirm.get().strip()

        if not user or not pw or not gmail:
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đủ thông tin")
            return

        if pw != confirm:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        file_path = "database/tk.csv"

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] == user:
                        messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại!")
                        return

        role = "Nhân viên"
        file_exists = os.path.isfile(file_path)

        try:
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists or os.stat(file_path).st_size == 0:
                    writer.writerow(["taikhoan", "matkhau", "gmail", "chucvu"])
                writer.writerow([user, pw, gmail, role])

            messagebox.showinfo("Thành công", f"Đã tạo tài khoản cho {user}")

            if self.from_admin:
                self.app_manager.show_quanlytk_page()
            else:
                self.app_manager.show_login_page()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {e}")