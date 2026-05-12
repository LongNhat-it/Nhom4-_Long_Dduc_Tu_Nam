import tkinter as tk

class ManagerMenu:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.master.configure(bg="#f5f5f5")
        self.view()

    def view(self):
        header_bg = "#6F4E37"
        header = tk.Frame(self.master, bg=header_bg, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ HỆ THỐNG QUẢN TRỊ", font=("Arial", 20, "bold"),
                 fg="white", bg=header_bg).pack(pady=15)

        main_container = tk.Frame(self.master, bg="#f5f5f5")
        main_container.pack(expand=True)

        tk.Label(main_container, text="Vui lòng chọn chức năng quản lý",
                 font=("Arial", 13, "italic"), bg="#f5f5f5", fg="#555").pack(pady=(0, 30))

        style_btn = {
            "font": ("Arial", 12, "bold"),
            "bg": "#6F4E37",
            "fg": "white",
            "activebackground": "#8B5A2B",
            "activeforeground": "white",
            "bd": 0,
            "width": 30,
            "pady": 15,
            "cursor": "hand2"
        }

        btn_kho = tk.Button(main_container, text="📦 QUẢN LÝ KHO NGUYÊN LIỆU",
                             command=self.app_manager.show_inventory_page,
                             **style_btn)
        btn_kho.pack(pady=10)

        btn_user = tk.Button(main_container, text="👥 QUẢN LÝ NHÂN SỰ & TK",
                              command=self.app_manager.show_quanlytk_page,
                              **style_btn)
        btn_user.pack(pady=10)


        footer_frame = tk.Frame(self.master, bg="#f5f5f5")
        footer_frame.pack(side="bottom", pady=40)

        tk.Button(footer_frame,
                  text=" ĐĂNG XUẤT HỆ THỐNG",
                  font=("Arial", 10, "bold"),
                  fg="white", bg="#c0392b",
                  activebackground="#a93226",
                  activeforeground="white",
                  bd=0, padx=25, pady=10,
                  cursor="hand2",
                  command=self.app_manager.show_login_page).pack()
