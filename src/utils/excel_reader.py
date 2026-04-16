import pandas as pd


class ExcelReader:
    """读取Excel文件"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = None

    def read(self) -> pd.DataFrame:
        """读取Excel文件"""
        self.df = pd.read_excel(self.filepath)
        return self.df

    def get_columns(self) -> list:
        """获取所有列名"""
        return self.df.columns.tolist()