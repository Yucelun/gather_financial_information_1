
import pandas as pd
import numpy as np
from GoogleSheets import GoogleSheets

print('start!!!')

sourceData = pd.read_csv('combin.csv')
sourceData = sourceData.fillna('')
sourceData.replace([np.inf, -np.inf], 0, inplace=True)

columns={'stockId': '股票代號', # 0
         'ReturnOfNetTangibleAssets_FirstQuartile': '淨有形資產收益率(Q1)', # 1
         'ONWR': '本業資金占總資產比率', # 2
         'LongDebtRatio': '長期債務比率', # 3
         'YoY': '營收年增率(當月)', # 4
         'OperatingProfitMargin': '營業利益率', # 5
         'ReturnOfEquity_FirstQuartile': '股東權益報酬率(Q1)', # 6
         'ReturnOfNetTangibleAssets_Median': '淨有形資產收益率(Q2)', # 7
         'ReturnOfRequest': '要求報酬率(Q1)', # 8
         'IntrinsicValue_FirstQuartile': '內在價值', # 9
         'IntrinsicValue_Median': '內在價值(Q2)', # 10
         'QuarterLength': '季度數量', # 11
         'IntrinsicValue_ThirdQuartile': '內在價值(Q3)', # 12
         'Profit_4': '四季盈餘', # 13
         'GrossProfitRatio': '毛利率', # 14
         'revenue12': '年化營收', # 14
         }

sourceData = sourceData.rename(columns=columns)
sourceData.to_csv("filter.csv", index=False, encoding='utf_8_sig')

myWorksheet = GoogleSheets()
myWorksheet.setWorksheet(
    spreadsheetId='1T8prv6D82Ld6Ht1D_2WzHhLQwItet2nR0wuApQcP33g',
    range='all',
    df=sourceData
)

print('end!!!')

