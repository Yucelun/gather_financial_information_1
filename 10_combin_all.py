import pandas as pd
import numpy as np

sourceData = pd.read_csv("combin.csv")
sourceData = sourceData.fillna(0)
sourceData.replace([np.inf, -np.inf], 0, inplace=True)

price_json = pd.read_json('price_json.json')
sourceData['price'] = 0
sourceData['name'] = ""
for i, row in sourceData.iterrows():
    stockId = row['stockId']
    find = price_json.loc[price_json[0] == stockId]
    if not find.empty:
        sourceData.at[i, 'name'] = find.iloc[0, 1]
        sourceData.at[i, 'price'] = find.iloc[0, 2]

basic_json = pd.read_json('basic_json.json')
sourceData['share'] = 0
for i, row in sourceData.iterrows():
    stockId = row['stockId']
    find = basic_json.loc[basic_json[0] == stockId]
    if not find.empty:
        sourceData.at[i, 'share'] = find.iloc[0, 2]
        
sourceData.replace([np.inf, -np.inf], 0, inplace=True)
sourceData['IntrinsicValuePerShare_FirstQuartile'] = sourceData['IntrinsicValue_FirstQuartile'] * 1000 / sourceData['share']
sourceData['IntrinsicValuePerShare_Median'] = sourceData['IntrinsicValue_Median'] * 1000 / sourceData['share']
sourceData['IntrinsicValuePerShare_ThirdQuartile'] = sourceData['IntrinsicValue_ThirdQuartile'] * 1000 / sourceData['share']
sourceData['AnnualizedReturn'] = sourceData['Profit_4'] * 1000 / sourceData['share'] / sourceData['price']
sourceData['SalesToPrice'] = sourceData['revenue12'] * 1000 / sourceData['share'] / sourceData['price']
sourceData.replace([np.inf, -np.inf], 0, inplace=True)

sourceData.to_csv("combin_all.csv", index=False, encoding='utf-8')
sourceData.to_json("combin_all.json", orient="records")

print('end!!!')
