import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wechat_pay

try:
    import qrcode
except ImportError:
    qrcode = None


class WeChatPayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("微信支付充值 - 配置工具")
        self.root.geometry("500x400")
        self.current_order = None
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="微信支付充值系统", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(main_frame, text="请选择充值金额", font=("Arial", 12)).pack(pady=10)

        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(pady=10)
        
        self.amount_var = tk.StringVar(value="500")
        amounts = [("500元", "500"), ("800元", "800"), ("1500元", "1500"), ("2000元", "2000")]
        
        for text, value in amounts:
            ttk.Radiobutton(amount_frame, text=text, value=value, variable=self.amount_var).pack(side=tk.LEFT, padx=10)

        ttk.Button(main_frame, text="生成支付二维码", command=self.generate_qr).pack(pady=20)

        self.qr_label = ttk.Label(main_frame, text="")
        self.qr_label.pack(pady=10)

        self.status_label = ttk.Label(main_frame, text="状态: 等待操作", foreground="gray")
        self.status_label.pack(pady=10)

        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        config_frame = ttk.LabelFrame(main_frame, text="配置说明", padding="10")
        config_frame.pack(fill=tk.X)
        
        config_text = """
请编辑 wechat_pay.py 文件配置微信支付参数:
• APPID - 微信公众号APPID
• MCHID - 商户号
• API_KEY - API密钥
• 证书路径 - 商户证书文件位置
        """
        ttk.Label(config_frame, text=config_text, justify=tk.LEFT).pack()

    def generate_qr(self):
        try:
            amount = float(self.amount_var.get())
            order_id = wechat_pay.generate_order_id()
            
            self.status_label.config(text=f"订单号: {order_id}", foreground="blue")
            self.root.update()
            
            try:
                code_url = wechat_pay.create_qr_code(amount, order_id)
            except ValueError as e:
                result = wechat_pay.create_demo_qr(amount, order_id)
                messagebox.showwarning("演示模式", f"{str(e)}\n\n当前为演示模式，无法连接微信支付。\n请配置 wechat_pay.py 中的商户参数。")
                code_url = result["qr_content"]
            
            if qrcode and code_url:
                qr = qrcode.QRCode(version=1, box_size=10, border=2)
                qr.add_data(code_url)
                qr.make(fit=True)
                qr_image = qr.make_image(fill_color="black", back_color="white")
                qr_image.save("/tmp/pay_qr.png")
                
                qr_photo = tk.PhotoImage(file="/tmp/pay_qr.png")
                self.qr_label.config(image=qr_photo, text="")
                self.qr_label.image = qr_photo
                
                self.status_label.config(text=f"请使用微信扫码支付 {amount} 元", foreground="green")
            else:
                self.qr_label.config(image="", text=f"二维码内容:\n{code_url}")
                self.status_label.config(text="请使用微信扫码支付", foreground="green")
                
        except Exception as e:
            messagebox.showerror("错误", f"生成二维码失败:\n{str(e)}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WeChatPayApp()
    app.run()
