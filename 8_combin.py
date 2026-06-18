import pandas as pd
import os
import numpy as np


def is_number(n):
    is_number = True
    try:
        num = np.float64(n)
        # 檢查 "nan"
        is_number = num == num  # 或者使用 `math.isnan(num)`
    except ValueError:
        is_number = False
    return is_number


quarterlyDir = 'quarterly'
monthlyDir = 'monthly'

files = os.listdir(quarterlyDir)

print('start!!!')

newTable = pd.DataFrame(columns=[
    'stockId', 'ReturnOfNetTangibleAssets_FirstQuartile', 'ONWR',
    'LongDebtRatio', 'YoY', 'OperatingProfitMargin',
    'ReturnOfEquity_FirstQuartile', 'ReturnOfNetTangibleAssets_Median',
    'ReturnOfRequest', 'IntrinsicValue_FirstQuartile', 'IntrinsicValue_Median',
    'QuarterLength', 'IntrinsicValue_ThirdQuartile', 'Profit_4',
    'GrossProfitRatio', 'revenue12'
])

files = os.listdir(quarterlyDir)
print('file_number=', len(files))

file_count = 0
for file in files:
    stockId = int(file.split(".")[0])

    quarterlyPath = os.path.join(quarterlyDir, file)

    if (not os.path.exists(quarterlyPath)):
        continue

    quarterlyData = pd.read_csv(quarterlyPath)

    # checkKey = "GrossProfit"
    # if ( not (checkKey in quarterlyData.columns.values)):
    #     print("'{}',".format(stockId))
    #     continue

    # if (np.sum(pd.isna(quarterlyData[checkKey])) > 0):
    #     print("'{}',".format(stockId))
    #     continue

    monthlyData = None
    monthlyPath = os.path.join(monthlyDir, file)
    if (not os.path.exists(monthlyPath)):
        # print(stockId)
        continue

    monthlyData = pd.read_csv(monthlyPath)
    if (monthlyData is None):
        continue

    NetTangibleAssets = quarterlyData["NetTangibleAssets"].loc[0]

    ReturnOfNetTangibleAssets_FirstQuartile = quarterlyData[
        "ReturnOfNetTangibleAssets_4"].quantile(0.25)
    if (np.isnan(ReturnOfNetTangibleAssets_FirstQuartile)):
        ReturnOfNetTangibleAssets_FirstQuartile = 0

    ReturnOfNetTangibleAssets_Median = quarterlyData[
        "ReturnOfNetTangibleAssets_4"].quantile(0.5)
    if (np.isnan(ReturnOfNetTangibleAssets_Median)):
        ReturnOfNetTangibleAssets_Median = 0

    ReturnOfNetTangibleAssets_ThirdQuartile = quarterlyData[
        "ReturnOfNetTangibleAssets_4"].quantile(0.75)
    if (np.isnan(ReturnOfNetTangibleAssets_ThirdQuartile)):
        ReturnOfNetTangibleAssets_ThirdQuartile = 0

    # 營收年增率 (YoY)
    YoY = monthlyData["YoY"].loc[0]
    revenue12 = monthlyData["revenue12"].loc[0]

    # 長期債務比例
    LongDebtRatio = quarterlyData["LongDebtRatio"].loc[0]

    # 毛利率
    OperatingProfitMargin = quarterlyData["OperatingProfitMargin"].loc[0]

    #計算本業資金占比 ONWR
    ONWR = quarterlyData["NetTangibleAssets"].values[0] / quarterlyData[
        "Assets"].values[0]

    #要求報酬率 (11%, 9, 11%),  (8%, 12, 25%)
    # ReturnOfRequest = max(0.16 - ReturnOfNetTangibleAssets_FirstQuartile / 3, 0.08);
    ReturnOfRequest = max(0.14 - ReturnOfNetTangibleAssets_FirstQuartile / 4,
                          0.08)

    #淨利
    Profit_4 = quarterlyData["Profit_4"].loc[0]

    #股東權益報酬率
    ReturnOfEquity_FirstQuartile = quarterlyData["ReturnOfEquity_4"].quantile(
        0.25)
    ReturnOfEquity_Median = quarterlyData["ReturnOfEquity_4"].quantile(0.5)
    ReturnOfEquity_ThirdQuartile = quarterlyData["ReturnOfEquity_4"].quantile(
        0.75)

    #生產力資產報酬率
    ReturnOfProductivityAssets_FirstQuartile = quarterlyData[
        "ReturnOfProductivityAssets_4"].quantile(0.25)
    ReturnOfProductivityAssets_Median = quarterlyData[
        "ReturnOfProductivityAssets_4"].quantile(0.5)
    ReturnOfProductivityAssets_ThirdQuartile = quarterlyData[
        "ReturnOfProductivityAssets_4"].quantile(0.75)

    #生產力資產
    ProductivityAssets = quarterlyData["ProductivityAssets"].loc[0]

    #預期收益率
    ExpectEarning_FirstQuartile = ReturnOfProductivityAssets_FirstQuartile * ProductivityAssets
    ExpectEarning_Median = ReturnOfProductivityAssets_Median * ProductivityAssets
    ExpectEarning_ThirdQuartile = ReturnOfProductivityAssets_ThirdQuartile * ProductivityAssets

    # 現金與約當現金 & 流動金融資產 & 非流動金融資產
    CashAndCashEquivalents = quarterlyData["CashAndCashEquivalents_All"].loc[0]

    #債務
    NoncurrentLiabilities = quarterlyData["NoncurrentLiabilities"].loc[0]

    #內在價值
    NtaValue_FirstQuartile = ExpectEarning_FirstQuartile / ReturnOfRequest
    IntrinsicValue_FirstQuartile = NtaValue_FirstQuartile + CashAndCashEquivalents - NoncurrentLiabilities

    NtaValue_Median = ExpectEarning_Median / ReturnOfRequest
    IntrinsicValue_Median = NtaValue_Median + CashAndCashEquivalents - NoncurrentLiabilities

    NtaValue_ThirdQuartile = ExpectEarning_ThirdQuartile / ReturnOfRequest
    IntrinsicValue_ThirdQuartile = NtaValue_ThirdQuartile + CashAndCashEquivalents - NoncurrentLiabilities

    #財務報表季度數量
    QuarterLength = len(quarterlyData)

    # 毛利率
    GrossProfitRatio = quarterlyData["GrossProfitRatio"].loc[0]

    newTable = pd.concat([newTable, pd.DataFrame(data={
        "stockId": stockId,
        "ReturnOfNetTangibleAssets_FirstQuartile": ReturnOfNetTangibleAssets_FirstQuartile,
        "ONWR": ONWR,
        "LongDebtRatio": LongDebtRatio,
        "YoY": YoY,
        "OperatingProfitMargin": OperatingProfitMargin,
        "ReturnOfEquity_FirstQuartile": ReturnOfEquity_FirstQuartile,
        "ReturnOfNetTangibleAssets_Median": ReturnOfNetTangibleAssets_Median,
        "ReturnOfRequest": ReturnOfRequest,
        "IntrinsicValue_FirstQuartile": IntrinsicValue_FirstQuartile,
        "IntrinsicValue_Median": IntrinsicValue_Median,
        "QuarterLength": QuarterLength,
        "IntrinsicValue_ThirdQuartile": IntrinsicValue_ThirdQuartile,
        "Profit_4": Profit_4,
        "GrossProfitRatio": GrossProfitRatio,
        "revenue12": revenue12
        }, index=[0])], ignore_index = True)

newTable.to_csv("combin.csv", index=False, encoding='utf-8')

print('end!!!')
