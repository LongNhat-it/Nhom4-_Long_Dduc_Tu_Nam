import tkinter as tk
from tkinter import ttk
import csv
import os
from common.button import CustomButton


class HistoryPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.view()
        self.load_history()

    def view(self):
        tk.Label(self.master, text="LỊCH SỬ ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 18, "bold"), fg="#2c3e50").pack(pady=20)

        tool_frame = tk.Frame(self.master)
        tool_frame.pack(pady=10, fill="x", padx=20)

        CustomButton(tool_frame, text="🔙 Quay lại",
                     command=self.app_manager.show_quanlytk_page,
                     style_type="secondary").pack(side="left")

        columns = ("stt", "user", "role", "time")
        self.tree = ttk.Treeview(self.master, columns=columns, show="headings")

        self.tree.heading("stt", text="STT")
        self.tree.heading("user", text="Người dùng")
        self.tree.heading("role", text="Chức vụ")
        self.tree.heading("time", text="Thời gian đăng nhập")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("user", width=150)
        self.tree.column("role", width=120, anchor="center")
        self.tree.column("time", width=250, anchor="center")

        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

    def load_history(self):
        if not os.path.exists("database/history.csv"): return

        try:
            with open("database/history.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                data = list(reader)
                for idx, row in enumerate(reversed(data), 1):
                    if len(row) >= 3:
                        self.tree.insert("", "end", values=(idx, row[0], row[1], row[2]))
        except:
            pass