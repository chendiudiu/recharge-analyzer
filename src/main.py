import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import pandas as pd
from src.utils.excel_reader import ExcelReader
from src.utils.excel_writer import ExcelWriter
from src.core.processor import Processor
from src.ui.wechat_pay_gui import open_wechat_pay


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("充值明细统计工具")
        self.root.geometry("600x500")
        self.input_file = None
        self.result_df = None
        self._create_menu()
        self.setup_ui()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="微信支付充值", command=self._open_wechat_pay)

    def _open_wechat_pay(self):
        open_wechat_pay(self.root)

    def setup_ui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="请选择集团会员账户明细Excel文件:").pack(anchor="w")

        file_frame = tk.Frame(frame)
        file_frame.pack(fill=tk.X, pady=10)
        self.file_entry = tk.Entry(file_frame)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        tk.Button(file_frame, text="选择文件", command=self.select_file).pack(side=tk.RIGHT)

        tk.Button(frame, text="开始处理", command=self.process, bg="#4CAF50", fg="white", 
                  font=("Arial", 12, "bold"), padx=20, pady=5).pack(pady=10)

        tk.Label(frame, text="处理结果预览:").pack(anchor="w", pady=(20, 5))

        self.tree = ttk.Treeview(frame, columns=("门店", "金额", "笔数"), show="headings", height=15)
        self.tree.heading("门店", text="消费门店名称")
        self.tree.heading("金额", text="充值金额")
        self.tree.heading("笔数", text="净笔数")
        self.tree.column("门店", width=250)
        self.tree.column("金额", width=100)
        self.tree.column("笔数", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(frame, text="状态: 未处理", fg="gray")
        self.status_label.pack(anchor="w", pady=(10, 0))

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_file = filename
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def process(self):
        if not self.input_file:
            messagebox.showwarning("提示", "请先选择文件！")
            return

        try:
            self.status_label.config(text="处理中...", fg="orange")
            self.root.update()

            reader = ExcelReader(self.input_file)
            df = reader.read()
            processor = Processor(df)
            self.result_df = processor.process()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for _, row in self.result_df.head(100).iterrows():
                self.tree.insert("", "end", values=(row["消费门店名称"], row["充值金额"], row["净笔数"]))

            if len(self.result_df) > 100:
                self.tree.insert("", "end", values=("...", "...", "..."))

            default_output = self.input_file.replace(".xlsx", "_充值统计.xlsx")
            output_file = filedialog.asksaveasfilename(
                title="保存结果",
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx")],
                initialfile=default_output
            )

            if output_file:
                writer = ExcelWriter(output_file)
                writer.write(self.result_df)
                self.status_label.config(text=f"处理完成！共 {len(self.result_df)} 条记录，已保存至: {output_file}", fg="green")
                messagebox.showinfo("成功", f"处理完成！\n共 {len(self.result_df)} 条记录")
            else:
                self.status_label.config(text="已处理，但未保存文件", fg="orange")

        except Exception as e:
            self.status_label.config(text=f"处理失败: {str(e)}", fg="red")
            messagebox.showerror("错误", f"处理失败: {str(e)}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()