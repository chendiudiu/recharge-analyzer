import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


class ExcelWriter:
    """写入Excel文件"""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def write(self, df: pd.DataFrame):
        """写入DataFrame到Excel"""
        wb = Workbook()
        ws = wb.active
        ws.title = "充值明细"

        # 写入表头
        ws.append(["消费门店名称", "充值金额", "净笔数"])

        # 格式化表头
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="left")

        # 写入数据
        for _, row in df.iterrows():
            ws.append([row["消费门店名称"], row["充值金额"], row["净笔数"]])

        # 设置列宽
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 12
        ws.column_dimensions["C"].width = 8

        wb.save(self.filepath)