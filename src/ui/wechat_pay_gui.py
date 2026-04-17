import tkinter as tk
from tkinter import messagebox
import qrcode
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ui.wechat_pay import (
    is_configured, generate_order_id, create_native_order, 
    query_order_status, create_demo_order
)


class WeChatPayWindow:
    AMOUNTS = [500, 800, 1500, 2000]

    def __init__(self, parent, on_success=None):
        self.on_success = on_success
        self.order = None
        self._poll_count = 0

        self.win = tk.Toplevel(parent)
        self.win.title("微信支付充值")
        self.win.geometry("380x520")
        self.win.resizable(False, False)
        self._setup_ui()

    def _setup_ui(self):
        frame = tk.Frame(self.win, padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="微信支付充值", font=("Arial", 14, "bold")).pack(pady=(0, 5))

        if not is_configured():
            tk.Label(frame, text="[演示模式] 请配置微信支付参数", fg="orange", font=("Arial", 10)).pack(pady=5)

        tk.Label(frame, text="选择充值金额:", font=("Arial", 11)).pack(pady=10)

        self.amount_var = tk.StringVar(value="500")
        for amt in self.AMOUNTS:
            tk.Radiobutton(frame, text=f"{amt} 元", value=str(amt), variable=self.amount_var,
                          font=("Arial", 12)).pack()

        tk.Button(frame, text="生成支付二维码", command=self._generate_qr,
                 bg="#07C160", fg="white", font=("Arial", 11, "bold"),
                 width=18, height=2).pack(pady=15)

        self.qr_label = tk.Label(frame)
        self.qr_label.pack(pady=10)

        self.status = tk.Label(frame, text="", font=("Arial", 11))
        self.status.pack(pady=5)

        self.progress = tk.Label(frame, text="", font=("Arial", 10), fg="gray")
        self.progress.pack()

        tk.Button(frame, text="关闭", command=self.win.destroy, width=10).pack(pady=10)

    def _generate_qr(self):
        try:
            amount = float(self.amount_var.get())
            order_id = generate_order_id()
            self.order = {"id": order_id, "amount": amount}
            self._poll_count = 0

            if is_configured():
                code_url = create_native_order(amount, order_id)
                self.status.config(text="请使用微信扫码支付", fg="blue")
            else:
                demo = create_demo_order(amount, order_id)
                code_url = demo["qr_content"]
                self.status.config(text="演示模式：5秒后自动确认", fg="orange")
                self._demo_wait(amount)
                messagebox.showinfo("演示模式", "演示模式：5秒后自动确认支付")

            self._display_qr(code_url)
            self._start_poll(amount)

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _display_qr(self, code_url):
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(code_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save("/tmp/wxpay_qr.png")
            self.qr_label.config(image=tk.PhotoImage(file="/tmp/wxpay_qr.png"))
        except Exception:
            self.qr_label.config(text=f"二维码内容:\n{code_url[:60]}...")

    def _demo_wait(self, amount):
        def check():
            self.status.config(text="✓ 演示模式：支付已确认", fg="green")
            messagebox.showinfo("支付成功", f"演示模式：充值 {amount} 元成功！")
            if self.on_success:
                self.on_success(amount)
        self.win.after(5000, check)

    def _start_poll(self, amount):
        self.progress.config(text="等待支付中...", fg="blue")
        self._poll_step(amount)

    def _poll_step(self, amount):
        if not self.order:
            return

        result = query_order_status(self.order["id"])
        if result.get("success"):
            self.progress.config(text="")
            self.status.config(text=f"✓ 支付成功！充值 {amount} 元", fg="green")
            messagebox.showinfo("支付成功", f"充值 {amount} 元已完成！")
            if self.on_success:
                self.on_success(amount)
            return

        self._poll_count += 1
        if self._poll_count >= 30:
            self.progress.config(text="")
            self.status.config(text="✗ 支付超时", fg="red")
            return

        self.win.after(2000, lambda: self._poll_step(amount))


def open_wechat_pay(parent, on_success=None):
    WeChatPayWindow(parent, on_success)
