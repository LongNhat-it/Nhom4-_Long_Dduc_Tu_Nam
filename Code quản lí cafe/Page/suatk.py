import tkinter as tk
from tkinter import messagebox, ttk
import csv

class SuaTKPage:
    def __init__(self, master, app_manager, username=""):
        self.master = master
        self.app_manager = app_manager
        self.old_user = username

        self.ent_user = None
        self.ent_gmail = None
        self.cb_role = None
        self.ent_pass = None
        self.ent_confirm = None

        self.config()
        self.view()

    def config(self):
        self.master.title("Cập nhật tài khoản")
        self.master.geometry("450x550")

    def view(self):
        header_color = "#6F4E37"
        header = tk.Frame(self.master, bg=header_color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ CHỈNH SỬA TÀI KHOẢN",
                 font=("Arial", 16, "bold"), fg="white", bg=header_color).pack(pady=15)

        self.master.configure(bg="#f5f5f5")

        frame = tk.Frame(self.master, bg="#f5f5f5")
        frame.pack(pady=20, padx=20)

        tk.Label(frame, text=f"Đang sửa: {self.old_user}", fg="#6F4E37",
                 bg="#f5f5f5", font=("Arial", 10, "italic bold")).grid(row=0, columnspan=2, pady=10)

        lbl_style = {"font": ("Arial", 10, "bold"), "bg": "#f5f5f5", "fg": "#333"}

        tk.Label(frame, text="Username mới:", **lbl_style).grid(row=1, column=0, pady=10, sticky="e")
        self.ent_user = tk.Entry(frame, font=("Arial", 11), width=25)
        self.ent_user.insert(0, self.old_user)
        self.ent_user.grid(row=1, column=1, pady=10)

        tk.Label(frame, text="Gmail mới:", **lbl_style).grid(row=2, column=0, pady=10, sticky="e")
        self.ent_gmail = tk.Entry(frame, font=("Arial", 11), width=25)
        self.ent_gmail.grid(row=2, column=1, pady=10)

        tk.Label(frame, text="Chức vụ:", **lbl_style).grid(row=3, column=0, pady=10, sticky="e")
        self.cb_role = ttk.Combobox(frame, values=["Quản lý", "Nhân viên"], state="readonly", font=("Arial", 10),
                                    width=23)
        self.cb_role.set("Nhân viên")
        self.cb_role.grid(row=3, column=1, pady=10)

        tk.Label(frame, text="Mật khẩu mới:", **lbl_style).grid(row=4, column=0, pady=10, sticky="e")
        self.ent_pass = tk.Entry(frame, show="*", font=("Arial", 11), width=25)
        self.ent_pass.grid(row=4, column=1, pady=10)

        tk.Label(frame, text="Xác nhận MK:", **lbl_style).grid(row=5, column=0, pady=10, sticky="e")
        self.ent_confirm = tk.Entry(frame, show="*", font=("Arial", 11), width=25)
        self.ent_confirm.grid(row=5, column=1, pady=10)

        btn_frame = tk.Frame(self.master, bg="#f5f5f5")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Lưu thay đổi", command=self.save,
                  bg="#6F4E37", fg="white", font=("Arial", 10, "bold"),
                  width=15, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

        tk.Button(btn_frame, text="Hủy", command=lambda: self.app_manager.show_quanlytk_page(),
                  bg="#6F4E37", fg="white", font=("Arial", 10, "bold"),
                  width=15, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

    def save(self):
        new_user = self.ent_user.get().strip()
        new_gmail = self.ent_gmail.get().strip()
        new_role = self.cb_role.get()
        new_pass = self.ent_pass.get().strip()
        confirm_pass = self.ent_confirm.get().strip()

        if not new_user or not new_pass or not new_gmail:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        if new_pass != confirm_pass:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        rows = []
        try:
            with open("database/tk.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header: rows.append(header)

                for row in reader:
                    if not row: continue
                    if row[0] == self.old_user:
                        rows.append([new_user, new_pass, new_gmail, new_role])
                    else:
                        rows.append(row)

            with open("database/tk.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)

            messagebox.showinfo("Thành công", "Đã cập nhật dữ liệu tài khoản")
            self.app_manager.show_quanlytk_page()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi lưu file: {e}")