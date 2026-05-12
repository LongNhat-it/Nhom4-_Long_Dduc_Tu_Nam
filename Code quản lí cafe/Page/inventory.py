import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from common.button import CustomButton


class InventoryPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.file_path = "database/nguyenlieu.csv"
        self.fields = ["Mã", "Tên", "Loại", "Tồn", "Đơn vị", "Giá"]

        if not os.path.exists("database"):
            os.makedirs("database")

        self.view()
        self.refresh_data()

    def clean_number(self, value):
        """Hỗ trợ xử lý số an toàn cho tính toán"""
        try:
            return int(str(value).replace(',', '').replace('.', '').strip())
        except:
            return 0

    def view(self):
        header_bg = "#6F4E37"
        header = tk.Frame(self.master, bg=header_bg, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ QUẢN LÝ KHO & BÁO CÁO TỔNG QUAN", font=("Arial", 20, "bold"),
                 fg="white", bg=header_bg).pack(side="left", padx=20)

        text_btn = "ĐĂNG XUẤT"
        cmd_btn = self.app_manager.show_login_page
        if self.app_manager.current_role == "Quản lý":
            text_btn = "🔙 VỀ MENU"
            cmd_btn = self.app_manager.show_manager_menu

        btn_back = tk.Button(header, text=text_btn, bg="#c0392b", fg="white",
                             font=("Arial", 10, "bold"), bd=0, padx=15, cursor="hand2",
                             command=cmd_btn)
        btn_back.pack(side="right", padx=20, pady=15)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab1 = tk.Frame(self.notebook, bg="white")
        self.tab2 = tk.Frame(self.notebook, bg="white")
        self.tab3 = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab1, text=" 1. Quản lý kho ")
        self.notebook.add(self.tab2, text=" 2. Thống kê chi phí nhập ")
        self.notebook.add(self.tab3, text=" 3. Báo cáo hàng hóa ")

        self.setup_tab_inventory()
        self.setup_tab_stats()
        self.setup_tab_report()

    def setup_tab_inventory(self):
        toolbar = tk.Frame(self.tab1, bg="white", pady=10)
        toolbar.pack(fill="x")

        CustomButton(toolbar, text="🔄 Làm mới", command=self.clear_search_and_refresh, style_type="info").pack(
            side="left", padx=5)
        CustomButton(toolbar, text="➕ Nhập hàng", command=lambda: self.open_form("NHẬP HÀNG MỚI"),
                     style_type="success").pack(side="left", padx=5)
        CustomButton(toolbar, text="📝 Sửa", command=self.edit_item, style_type="warning").pack(side="left", padx=5)
        CustomButton(toolbar, text="🗑️ Xóa", command=self.delete_item, style_type="danger").pack(side="left", padx=5)

        CustomButton(toolbar, text="🔍", command=self.refresh_data, style_type="primary").pack(side="right", padx=2)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_data())
        self.ent_search = tk.Entry(toolbar, font=("Arial", 11), width=55, textvariable=self.search_var)
        self.ent_search.pack(side="right", padx=5)
        tk.Label(toolbar, text="Tìm kiếm:", bg="white").pack(side="right", padx=5)

        self.cols = ("stt", "ma", "ten", "loai", "ton", "donvi", "gia")
        self.tree = ttk.Treeview(self.tab1, columns=self.cols, show="headings")
        for c, t in zip(self.cols, ["STT", "Mã", "Tên", "Loại", "Tồn", "ĐVT", "Giá Nhập"]):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.tag_configure('low', background='#ffcccc')

    def setup_tab_stats(self):
        """Bảng thống kê thành tiền đơn giản"""
        tk.Label(self.tab2, text="📊 CHI TIẾT GIÁ TRỊ VỐN NHẬP KHO", font=("Arial", 14, "bold"), bg="white",
                 fg="#6F4E37").pack(pady=10)
        cols_stats = ("ten", "ton", "gia", "tong")
        self.tree_stats = ttk.Treeview(self.tab2, columns=cols_stats, show="headings")
        self.tree_stats.heading("ten", text="Nguyên Liệu")
        self.tree_stats.heading("ton", text="Số lượng tồn")
        self.tree_stats.heading("gia", text="Đơn giá nhập")
        self.tree_stats.heading("tong", text="Tổng giá trị vốn")
        for c in cols_stats: self.tree_stats.column(c, anchor="center")
        self.tree_stats.pack(fill="both", expand=True, padx=20, pady=10)

    def setup_tab_report(self):
        """Khung báo cáo dạng văn bản (Real-time)"""
        frame_report = tk.Frame(self.tab3, bg="white", padx=20, pady=20)
        frame_report.pack(fill="both", expand=True)
        tk.Label(frame_report, text="📄 PHIẾU BÁO CÁO TỔNG QUAN", font=("Arial", 15, "bold"), bg="white").pack()
        self.txt_report = tk.Text(frame_report, font=("Courier New", 12), bg="#FDFEFE", bd=2, relief="groove")
        self.txt_report.pack(fill="both", expand=True, pady=10)

    def refresh_data(self):
        """Hàm đồng bộ dữ liệu cho tất cả các Tab"""
        query = self.ent_search.get().strip().lower()
        for i in self.tree.get_children(): self.tree.delete(i)
        for i in self.tree_stats.get_children(): self.tree_stats.delete(i)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.fields + ["Ngày", "Trạng thái"])
            return

        low_stock_list = []
        total_cost = 0
        total_items = 0
        categories = {}
        idx_counter = 1

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for r in reader:
                    if not r or len(r) < 6: continue
                    ma, ten, cat = r[0], r[1], r[2]

                    if query in ma.lower() or query in ten.lower() or query in cat.lower():
                        ton = self.clean_number(r[3])
                        gia = self.clean_number(r[5])
                        thanh_tien = ton * gia
                        total_cost += thanh_tien
                        total_items += 1
                        categories[cat] = categories.get(cat, 0) + 1

                        tag = 'low' if ton < 10 else ''
                        if ton < 10: low_stock_list.append(ten)

                        self.tree.insert("", "end", values=(idx_counter, ma, ten, cat, ton, r[4], f"{gia:,}"),
                                         tags=(tag,))
                        self.tree_stats.insert("", "end", values=(ten, ton, f"{gia:,}", f"{thanh_tien:,} VNĐ"))
                        idx_counter += 1

            self.generate_report(total_items, total_cost, low_stock_list, categories)
        except Exception as e:
            print(f"Lỗi: {e}")

    def generate_report(self, items, cost, lows, cats):
        self.txt_report.delete("1.0", "end")
        report_content = f"""
==================================================
        BÁO CÁO KHO HÀNG ĐÃ ĐỒNG BỘ
        Ngày lập: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
==================================================

1. THỐNG KÊ TỔNG QUAN:
   - Tổng số mặt hàng: {items} loại.
   - Tổng giá trị vốn nhập kho: {cost:,} VNĐ.

2. CHI TIẾT NHÓM HÀNG:
"""
        for c, count in cats.items():
            report_content += f"   + {c}: {count} mặt hàng\n"

        report_content += f"""
3. TÌNH TRẠNG CẢNH BÁO:
   - Số lượng hàng cần nhập thêm: {len(lows)} mặt hàng.
   - Danh sách: {', '.join(lows) if lows else "An toàn"}

4. KẾT LUẬN:
   - Trạng thái hệ thống: {'⚠️ CẦN NHẬP HÀNG' if lows else '✅ ỔN ĐỊNH'}
==================================================
"""
        self.txt_report.insert("1.0", report_content)

    def clear_search_and_refresh(self):
        self.ent_search.delete(0, tk.END)
        self.refresh_data()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected: return messagebox.showwarning("Chú ý", "Vui lòng chọn hàng!")
        data = self.tree.item(selected[0])['values'][1:]
        self.open_form("CẬP NHẬT NGUYÊN LIỆU", data)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected or not messagebox.askyesno("Xác nhận", "Xóa mặt hàng này?"): return
        ma_xoa = self.tree.item(selected[0])['values'][1]
        rows = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [header] + [r for r in reader if r and r[0] != str(ma_xoa)]
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        self.refresh_data()

    def open_form(self, title, edit_data=None):
        win = tk.Toplevel(self.master)
        win.title(title)
        win.geometry("400x600")
        win.grab_set()
        tk.Label(win, text=title, font=("Arial", 14, "bold")).pack(pady=20)
        ents = {}
        for i, field_name in enumerate(self.fields):
            tk.Label(win, text=f"{field_name}:").pack()
            e = tk.Entry(win, width=30)
            e.pack(pady=5)
            if edit_data:
                e.insert(0, edit_data[i])
                if i == 0: e.config(state="readonly")
            ents[field_name] = e

        def save():
            new_row = [ents[f].get() for f in self.fields]
            if not new_row[0] or not new_row[1]: return messagebox.showerror("Lỗi", "Không để trống Mã/Tên")
            all_data = []
            with open(self.file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                all_data.append(header)
                for r in reader:
                    if r and r[0] == new_row[0]: continue
                    all_data.append(r)
            all_data.append(new_row + [datetime.now().strftime("%d/%m/%Y"), "Sẵn sàng"])
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(all_data)
            self.refresh_data()
            win.destroy()

        tk.Button(win, text="XÁC NHẬN", bg="#8B4513", fg="white", font=("Arial", 10, "bold"),
                  command=save, width=15, height=2).pack(pady=20)