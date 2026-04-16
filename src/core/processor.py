import pandas as pd
from .config import COL_STORE_NAME, COL_TRANSACTION_TYPE, COL_AMOUNT, TRANSACTION_TYPES


class Processor:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def filter_recharge(self) -> pd.DataFrame:
        return self.df[self.df[COL_TRANSACTION_TYPE].isin(TRANSACTION_TYPES)].copy()

    def process(self) -> pd.DataFrame:
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