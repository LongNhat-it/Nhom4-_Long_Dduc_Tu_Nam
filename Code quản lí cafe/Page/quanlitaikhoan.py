import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from common.button import CustomButton


class QuanLyTKPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager

        # Khai báo các thuộc tính trước để tránh cảnh báo IDE
        self.search_var = None
        self.ent_search = None
        self.tree = None

        self.config()
        self.view()
        self.load_accounts()

    def config(self):
        self.master.title("Quản lý nhân sự kho")
        self.master.geometry("1200x550")

    def view(self):
        tk.Label(self.master, text="👥 DANH SÁCH TÀI KHOẢN NHÂN VIÊN", font=("Arial", 18, "bold")).pack(pady=10)

        tool_frame = tk.Frame(self.master)
        tool_frame.pack(pady=10, fill="x", padx=20)

        CustomButton(tool_frame, text="🔄 Làm mới", command=self.load_accounts, style_type="info").pack(side="left",
                                                                                                       padx=5)

        CustomButton(tool_frame, text="➕ Thêm", command=lambda: self.app_manager.show_taotk_page(from_admin=True),
                     style_type="success").pack(side="left", padx=5)

        CustomButton(tool_frame, text="✏️ Sửa", command=self.edit_account, style_type="warning").pack(side="left",
                                                                                                      padx=5)
        CustomButton(tool_frame, text="🗑️ Xóa", command=self.delete_account, style_type="danger").pack(side="left",
                                                                                                       padx=5)
        CustomButton(tool_frame, text="📜 Lịch sử", command=self.app_manager.show_history_page,
                     style_type="primary").pack(side="right", padx=5)
        CustomButton(tool_frame, text="🔙 Về Menu", command=lambda: self.app_manager.show_manager_menu(),
                     style_type="secondary").pack(side="right", padx=5)


        CustomButton(tool_frame, text="🔍", command=self.search_account, style_type="primary").pack(side="right", padx=2)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda n, i, m: self.load_accounts(self.search_var.get().strip().lower()))

        self.ent_search = tk.Entry(tool_frame, font=("Arial", 11), width=35, textvariable=self.search_var)
        self.ent_search.pack(side="right", padx=5)
        tk.Label(tool_frame, text="Tìm kiếm:", font=("Arial", 10)).pack(side="right", padx=5)

        """Bảng dữ liệu"""
        columns = ("stt", "user", "pass", "gmail", "role")
        self.tree = ttk.Treeview(self.master, columns=columns, show="headings", height=15)
        self.tree.heading("stt", text="STT")
        self.tree.heading("user", text="Tên đăng nhập")
        self.tree.heading("pass", text="Mật khẩu")
        self.tree.heading("gmail", text="Gmail")
        self.tree.heading("role", text="Chức vụ")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("user", width=150)
        self.tree.column("pass", width=120)
        self.tree.column("gmail", width=200)
        self.tree.column("role", width=120, anchor="center")
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

    def search_account(self):
        """Hàm bổ trợ khi nhấn vào nút kính lúp"""
        query = self.ent_search.get().strip().lower()
        self.load_accounts(query)

    def load_accounts(self, search_query=""):
        """Đọc file CSV và hiển thị, có hỗ trợ lọc theo tìm kiếm"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not os.path.exists("database/tk.csv"):
            return

        try:
            with open("database/tk.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Bỏ qua tiêu đề
                idx_counter = 1
                for row in reader:
                    if not row or len(row) < 2: continue

                    user = row[0]
                    gmail = row[2] if len(row) > 2 else ""
                    role = row[3] if len(row) > 3 else "Nhân viên"

                    # Kiểm tra điều kiện tìm kiếm (User hoặc Gmail)
                    if search_query in user.lower() or search_query in gmail.lower():
                        # Hiển thị mật khẩu dạng ẩn để bảo mật
                        display_pass = "*" * len(row[1])
                        self.tree.insert("", "end", values=(idx_counter, user, display_pass, gmail, role))
                        idx_counter += 1
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách: {e}")

    def delete_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Hãy chọn tài khoản muốn xóa")
            return

        user_to_del = self.tree.item(selected[0])['values'][1]
        if messagebox.askyesno("Xác nhận", f"Xóa tài khoản {user_to_del}?"):
            rows = []
            try:
                with open("database/tk.csv", "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    rows = [header] + [row for row in reader if row and row[0] != user_to_del]

                with open("database/tk.csv", "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
                self.load_accounts()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {e}")

    def edit_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Chọn tài khoản để sửa")
            return
        user = self.tree.item(selected[0])['values'][1]
        self.app_manager.show_suatk_page(user)