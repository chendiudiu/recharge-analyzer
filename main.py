import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

COL_STORE_NAME = "消费门店名称"
COL_TRANSACTION_TYPE = "交易类型"
COL_AMOUNT = "交易金额（实付）"
TRANSACTION_TYPES = ["充值", "充值退款"]


class ExcelReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None

    def read(self):
        self.df = pd.read_excel(self.filepath)
        return self.df


class ExcelWriter:
    def __init__(self, filepath):
        self.filepath = filepath

    def write(self, df):
        wb = Workbook()
        ws = wb.active
        ws.title = "充值明细"
        ws.append(["消费门店名称", "充值金额", "净笔数"])
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="left")
        for _, row in df.iterrows():
            ws.append([row["消费门店名称"], row["充值金额"], row["净笔数"]])
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 12
        ws.column_dimensions["C"].width = 8
        wb.save(self.filepath)


class Processor:
    def __init__(self, df):
        self.df = df

    def filter_recharge(self):
        return self.df[self.df[COL_TRANSACTION_TYPE].isin(TRANSACTION_TYPES)].copy()

    def process(self):
        recharge_df = self.filter_recharge()
        positive = recharge_df[recharge_df[COL_AMOUNT] > 0].groupby(
            [COL_STORE_NAME, COL_AMOUNT]
        ).size().reset_index(name="正笔数")
        negative = recharge_df[recharge_df[COL_AMOUNT] < 0].copy()
        negative[COL_AMOUNT] = negative[COL_AMOUNT].abs()
        negative = negative.groupby([COL_STORE_NAME, COL_AMOUNT]).size().reset_index(name="负笔数")
        result = pd.merge(positive, negative, on=[COL_STORE_NAME, COL_AMOUNT], how="outer").fillna(0)
        result["净笔数"] = (result["正笔数"] - result["负笔数"]).astype(int)
        result = result[result["净笔数"] > 0]
        store_net = recharge_df.groupby(COL_STORE_NAME)[COL_AMOUNT].sum().sort_values(ascending=False)
        store_order = store_net.index.tolist()
        result[COL_STORE_NAME] = pd.Categorical(result[COL_STORE_NAME], categories=store_order, ordered=True)
        result = result.sort_values([COL_STORE_NAME, COL_AMOUNT], ascending=[True, False])
        result = result.rename(columns={COL_AMOUNT: "充值金额", COL_STORE_NAME: "消费门店名称"})
        return result[["消费门店名称", "充值金额", "净笔数"]]


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("充值明细统计工具")
        self.root.geometry("600x500")
        self.input_file = None
        self.result_df = None
        self.setup_ui()

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