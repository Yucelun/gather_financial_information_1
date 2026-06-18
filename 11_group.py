import pandas as pd
import numpy as np

maxGroup = 10
subLimit = 1 / maxGroup

def getLimits(series: pd.Series):
    result = []
    s = series.loc[series >= 0]
    for i in range(0, maxGroup + 1):
        limit = s.quantile(subLimit * i)
        result.append(limit)
    return result


def getGroupIndex(limits, value, ascending):
    if ascending:
        for i in range(0, maxGroup):
            if i == maxGroup-1:
                if (limits[i] <= value and value <= limits[i+1]):
                    return i+1
            else:
                if (limits[i] <= value and value < limits[i+1]):
                    return i+1
    else:
        for i in range(maxGroup-1, -1, -1):
            if i == maxGroup-1:
                if (limits[i] <= value and value <= limits[i+1]):
                    return maxGroup-i
            else:
                if (limits[i] <= value and value < limits[i+1]):
                    return maxGroup-i
    return 0

def setGroup(sourceTable, sourceCaption, targetTable, targetCaption,
             ascending):
    limits = getLimits(sourceTable[sourceCaption])
    for i, row in sourceTable.iterrows():
        targetTable.at[i,
                       targetCaption] = getGroupIndex(limits,
                                                      row[sourceCaption],
                                                      ascending)
    return


print('start!!!')

sourceData = pd.read_csv("combin_all.csv")
sourceData = sourceData.fillna(0)
sourceData.replace([np.inf, -np.inf], 0, inplace=True)

newTable = pd.DataFrame(
    columns=['stockId', 'product', 'manager', 'asset', 'finance', 'investment', 'speculation', 'main', 'mainInvestment', 'mainSpeculation', 'total'])

newTable['stockId'] = sourceData['stockId']
setGroup(sourceData, 'OperatingProfitMargin', newTable, 'product', True)
setGroup(sourceData, 'ReturnOfEquity_FirstQuartile', newTable, 'manager', True)
setGroup(sourceData, 'ReturnOfNetTangibleAssets_FirstQuartile', newTable,
         'asset', True)
setGroup(sourceData, 'LongDebtRatio', newTable, 'finance', False)

# price_json = pd.read_json('price_json.json')
# sourceData['price'] = 0
# for i, row in sourceData.iterrows():
#     stockId = row['stockId']
#     find = price_json.loc[price_json[0] == stockId]
#     if not find.empty:
#         sourceData.at[i, 'price'] = find.iloc[0, 2]

# basic_json = pd.read_json('basic_json.json')
# sourceData['share'] = 0
# for i, row in sourceData.iterrows():
#     stockId = row['stockId']
#     find = basic_json.loc[basic_json[0] == stockId]
#     if not find.empty:
#         sourceData.at[i, 'share'] = find.iloc[0, 2]

# sourceData.replace([np.inf, -np.inf], 0, inplace=True)
# sourceData['AnnualizedReturn'] = sourceData['Profit_4'] * 1000 / sourceData['share'] / sourceData['price']
# sourceData.replace([np.inf, -np.inf], 0, inplace=True)
setGroup(sourceData, 'AnnualizedReturn', newTable, 'investment', True)

# sourceData.replace([np.inf, -np.inf], 0, inplace=True)
# sourceData['SalesToPrice'] = sourceData['revenue12'] * 1000 / sourceData['share'] / sourceData['price']
# sourceData.replace([np.inf, -np.inf], 0, inplace=True)
setGroup(sourceData, 'SalesToPrice', newTable, 'speculation', True)

newTable['main'] = newTable['investment'] + newTable['speculation']
newTable['mainInvestment'] = newTable['investment'] + newTable['product'] + newTable['manager'] + newTable['asset'] + newTable['finance']
newTable['mainSpeculation'] = newTable['speculation'] + newTable['product'] + newTable['manager'] + newTable['asset'] + newTable['finance']
newTable['total'] = newTable['investment'] + newTable['speculation'] + newTable['product'] + newTable['manager'] + newTable['asset'] + newTable['finance']

newTable.to_csv("group.csv", index=False, encoding='utf-8')
newTable.to_json("group.json", orient="records")

print('end!!!')
