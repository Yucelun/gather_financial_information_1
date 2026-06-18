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
    columns=['stockId', 
             'name', 
             'ReturnOfNetTangibleAssets_FirstQuartile', 
             'ONWR', 
             'LongDebtRatio', 
             'YoY', 
             'OperatingProfitMargin', 
             'ReturnOfEquity_FirstQuartile', 
             'GrossProfitRatio', 
             'AnnualizedReturn', 
             'SalesToPrice'])

newTable['stockId'] = sourceData['stockId']
newTable['name'] = sourceData['name']
setGroup(sourceData, 'ReturnOfNetTangibleAssets_FirstQuartile', newTable, 'ReturnOfNetTangibleAssets_FirstQuartile', True)
setGroup(sourceData, 'ONWR', newTable, 'ONWR', True)
setGroup(sourceData, 'LongDebtRatio', newTable,'LongDebtRatio', False)
setGroup(sourceData, 'YoY', newTable, 'YoY', True)
setGroup(sourceData, 'OperatingProfitMargin', newTable, 'OperatingProfitMargin', True)
setGroup(sourceData, 'ReturnOfEquity_FirstQuartile', newTable, 'ReturnOfEquity_FirstQuartile', True)
setGroup(sourceData, 'GrossProfitRatio', newTable, 'GrossProfitRatio', True)
setGroup(sourceData, 'AnnualizedReturn', newTable, 'AnnualizedReturn', True)
setGroup(sourceData, 'SalesToPrice', newTable, 'SalesToPrice', True)

newTable.to_csv("score.csv", index=False, encoding='utf-8')
newTable.to_json("score.json", orient="records")

print('end!!!')
