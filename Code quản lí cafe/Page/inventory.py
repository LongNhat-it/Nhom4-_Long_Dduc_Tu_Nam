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
        self.fields = ["Nguyên liệu", "Loại", "Số lượng", "Giá/kg", "Ngày nhập"]

        if not os.path.exists("database"):
            os.makedirs("database")

        self.view()
        self.refresh_data()

    def clean_number(self, value):
        """Hỗ trợ xử lý số an toàn cho tính toán"""
        try:
            v = str(value).replace(',', '').replace('.', '').replace(' VNĐ', '').strip()
            return int(v) if v else 0
        except:
            return 0

    def view(self):
        header_bg = "#6F4E37"
        header = tk.Frame(self.master, bg=header_bg, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ QUẢN LÝ KHO & BÁO CÁO", font=("Arial", 20, "bold"),
                 fg="white", bg=header_bg).pack(side="left", padx=20)

        btn_back = tk.Button(header, text="🔙 VỀ MENU" if self.app_manager.current_role == "Quản lý" else "ĐĂNG XUẤT",
                             bg="#c0392b", fg="white", font=("Arial", 10, "bold"), bd=0, padx=15, cursor="hand2",
                             command=self.app_manager.show_manager_menu if self.app_manager.current_role == "Quản lý" else self.app_manager.show_login_page)
        btn_back.pack(side="right", padx=20, pady=15)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab1 = tk.Frame(self.notebook, bg="white")
        self.tab2 = tk.Frame(self.notebook, bg="white")
        self.tab3 = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab1, text=" 1. Quản lý kho ")
        self.notebook.add(self.tab2, text=" 2. Thống kê chi phí ")
        self.notebook.add(self.tab3, text=" 3. Phiếu báo cáo tổng quan ")

        self.setup_tab_inventory()
        self.setup_tab_stats()
        self.setup_tab_report_text()

    def setup_tab_inventory(self):
        toolbar = tk.Frame(self.tab1, bg="white", pady=10)
        toolbar.pack(fill="x")

        CustomButton(toolbar, text="🔄 Làm mới", command=self.clear_search_and_refresh, style_type="info").pack(
            side="left", padx=5)
        CustomButton(toolbar, text="➕ Nhập hàng", command=lambda: self.open_form("NHẬP HÀNG MỚI"),
                     style_type="success").pack(side="left", padx=5)
        CustomButton(toolbar, text="📝 Sửa", command=self.edit_item, style_type="warning").pack(side="left", padx=5)
        CustomButton(toolbar, text="🗑️ Xóa", command=self.delete_item, style_type="danger").pack(side="left", padx=5)

        # Tìm kiếm bên phải
        CustomButton(toolbar, text="🔍", command=self.refresh_data, style_type="primary").pack(side="right", padx=2)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_data())
        self.ent_search = tk.Entry(toolbar, font=("Arial", 11), width=40, textvariable=self.search_var)
        self.ent_search.pack(side="right", padx=5)
        tk.Label(toolbar, text="Tìm kiếm:", bg="white").pack(side="right", padx=5)

        self.tree = ttk.Treeview(self.tab1, columns=("stt", "ten", "loai", "sl", "gia", "ngay", "tong"),
                                 show="headings")
        titles = ["STT", "Nguyên liệu", "Loại", "Số lượng", "Giá/kg", "Ngày nhập", "Thành tiền"]
        for c, t in zip(self.tree["columns"], titles):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_tab_stats(self):
        tk.Label(self.tab2, text="📊 CHI PHÍ PHÁT SINH", font=("Arial", 16, "bold"), bg="white", fg="#6F4E37").pack(
            pady=10)
        self.tree_stats = ttk.Treeview(self.tab2, columns=("ten", "sl", "ngay", "gia", "tong"), show="headings")
        titles = ["Nguyên liệu", "Số lượng", "Ngày nhập", "Đơn giá", "Thành tiền"]
        for c, t in zip(self.tree_stats["columns"], titles):
            self.tree_stats.heading(c, text=t)
            self.tree_stats.column(c, anchor="center")
        self.tree_stats.pack(fill="both", expand=True, padx=20, pady=10)

        bottom_frame = tk.Frame(self.tab2, bg="white")
        bottom_frame.pack(fill="x", padx=20, pady=10)
        tk.Button(bottom_frame, text="💰 TÍNH TỔNG THANH TOÁN", command=self.sum_all_stats, bg="#27AE60", fg="white",
                  font=("Arial", 11, "bold"), padx=20, pady=5).pack(side="left")
        self.lbl_total_payment = tk.Label(bottom_frame, text="KẾT QUẢ: 0 VNĐ", font=("Arial", 14, "bold"), fg="#C0392B",
                                          bg="white")
        self.lbl_total_payment.pack(side="right")

    def setup_tab_report_text(self):
        """Khung báo cáo dạng văn bản (Real-time)"""
        frame_report = tk.Frame(self.tab3, bg="white", padx=20, pady=20)
        frame_report.pack(fill="both", expand=True)
        self.txt_report = tk.Text(frame_report, font=("Courier New", 12), bg="#FDFEFE", bd=2, relief="groove")
        self.txt_report.pack(fill="both", expand=True, pady=10)

    def refresh_data(self):
        query = self.ent_search.get().strip().lower()
        for i in self.tree.get_children(): self.tree.delete(i)
        for i in self.tree_stats.get_children(): self.tree_stats.delete(i)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.fields)
            return

        grand_total = 0
        total_items = 0
        list_for_report = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                idx = 1
                for r in reader:
                    if not r or len(r) < 5: continue
                    ten, loai, sl_val, gia_val, ngay = r[0], r[1], r[2], r[3], r[4]
                    sl = self.clean_number(sl_val)
                    gia = self.clean_number(gia_val)
                    thanh_tien = sl * gia

                    if query in ten.lower() or query in loai.lower() or query in ngay.lower():
                        grand_total += thanh_tien
                        total_items += 1
                        list_for_report.append(r)


                        self.tree.insert("", "end", values=(idx, ten, loai, sl, f"{gia:,}", ngay, f"{thanh_tien:,}"))

                        self.tree_stats.insert("", "end", values=(ten, sl, ngay, f"{gia:,}", f"{thanh_tien:,}"))
                        idx += 1

            self.generate_custom_report(grand_total, list_for_report)
        except Exception as e:
            print(f"Lỗi: {e}")

    def generate_custom_report(self, total_money, data_list):
        """Hàm tạo nội dung phiếu báo cáo theo đúng yêu cầu của bro"""
        self.txt_report.delete("1.0", "end")
        curr_month = datetime.now().strftime('%m/%Y')

        report_content = f"""
==================================================
              BÁO CÁO THÁNG {curr_month}
==================================================

PHẦN 1: THỐNG KÊ TÀI CHÍNH
   - Tổng số mặt hàng: {len(data_list)} loại
   - Tổng chi phí thanh toán: {total_money:,} VNĐ

PHẦN 2: CHI TIẾT HÀNG HÓA NHẬP KHO
"""
        # Duyệt qua danh sách để ghi rõ Loại ... Tên hàng
        for item in data_list:
            ten = item[0]
            loai = item[1]
            report_content += f"   + Loại {loai.lower()} ... {ten}\n"

        report_content += f"""
--------------------------------------------------
Hệ thống tự động đồng bộ dữ liệu lúc: {datetime.now().strftime('%H:%M:%S')}
==================================================
"""
        self.txt_report.insert("1.0", report_content)

    def sum_all_stats(self):
        total = 0
        for item in self.tree_stats.get_children():
            total += self.clean_number(self.tree_stats.item(item)['values'][4])
        self.lbl_total_payment.config(text=f"KẾT QUẢ: {total:,} VNĐ")

    def clear_search_and_refresh(self):
        self.ent_search.delete(0, tk.END)
        self.refresh_data()

    def edit_item(self):
        sel = self.tree.selection()
        if sel: self.open_form("CẬP NHẬT", self.tree.item(sel[0])['values'][1:6])

    def delete_item(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Xác nhận", "Xóa?"):
            ten = self.tree.item(sel[0])['values'][1]
            rows = []
            with open(self.file_path, "r", encoding="utf-8") as f:
                r = csv.reader(f)
                h = next(r)
                rows = [h] + [line for line in r if line and line[0] != ten]
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            self.refresh_data()

    def open_form(self, title, edit_data=None):
        win = tk.Toplevel(self.master)
        win.title(title)
        win.geometry("400x550")
        win.grab_set()
        tk.Label(win, text=title, font=("Arial", 14, "bold")).pack(pady=20)
        ents = {}
        for i, f in enumerate(self.fields):
            tk.Label(win, text=f"{f}:").pack()
            e = tk.Entry(win, width=30)
            e.pack(pady=5)
            if f == "Ngày nhập" and not edit_data: e.insert(0, datetime.now().strftime("%d/%m/%Y"))
            if edit_data:
                e.insert(0, edit_data[i])
                if i == 0: e.config(state="readonly")
            ents[f] = e

        def save():
            new_r = [ents[f].get() for f in self.fields]
            if not new_r[0] or not new_r[1]: return messagebox.showerror("Lỗi", "Thiếu thông tin!")
            all_d = []
            with open(self.file_path, "r", encoding="utf-8") as f:
                r = csv.reader(f)
                h = next(r, None)
                if h: all_d.append(h)
                for line in r:
                    if line and line[0] != new_r[0]: all_d.append(line)
            all_d.append(new_r)
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(all_d)
            self.refresh_data()
            win.destroy()

        tk.Button(win, text="XÁC NHẬN", bg="#8B4513", fg="white", command=save, width=15).pack(pady=20)