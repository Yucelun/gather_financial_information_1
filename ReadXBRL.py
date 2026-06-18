
import abc
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os


sourceDirFormat = "xbrl/{}Q{}"
targetDir = "quarterly"

# 字串
# stocks = [
#     "8284",
#     "8499",
#     ]


def getStockId(soup):
#    hidden = soup.find("ix:hidden")
#    if (hidden == None):
#        return ""
    
    notes = soup.find("ix:nonnumeric", {"name" : "tifrs-notes:CompanyID"})
    if (notes is None):
        return ""

#    for note in notes:
#        if (note["name"] == "tifrs-notes:CompanyID"): 
#            return note.text
    return notes.text

def getMarket(soup):
#    hidden = soup.find("ix:hidden")
#    if (hidden == None):
#        return ""
    
    notes = soup.find("ix:nonnumeric", {"name" : "tifrs-notes:Market"})
    if (notes is None):
        notes = soup.find("tifrs-notes:Market")

    if (notes is None):
        return ""

#    for note in notes:
#        if (note["name"] == "tifrs-notes:Market"): 
#            return note.text
    return notes.text

def getFinanceTable(feildTable, year, quarter):
    financeColumns = ["year", "quarter"]
    values = [year, quarter]
    financeTable = pd.DataFrame(np.array([values]), columns=financeColumns)
    return financeTable
    
def SetOrAdd(table, year, quarter, feildTable):
    for data_index, data_row in table.iterrows():
        if (data_row['year'] == year):
            if (data_row['quarter'] == quarter):
                for feildIndex, feildRow in feildTable.iterrows():
                    if (not np.isnan(feildRow["value"])):
                        table.at[data_index, feildRow["useName"]] = feildRow["value"]
                return table
    
    financeTable = getFinanceTable(feildTable, year, quarter)
    for data_index, data_row in financeTable.iterrows():
        if (data_row['year'] == year):
            if (data_row['quarter'] == quarter):
                for feildIndex, feildRow in feildTable.iterrows():
                    if (not np.isnan(feildRow["value"])):
                        financeTable.at[data_index, feildRow["useName"]] = feildRow["value"]

    return pd.concat([table, pd.DataFrame(data=financeTable, index=[0])], ignore_index=True)

def clean_num(num_string):
    bad_chars = '(),-'
    translator = str.maketrans('', '', bad_chars)
    clean_digits = num_string.translate(translator).strip()
    if clean_digits == '':
        return 0
    else:
        if '(' in num_string:
            return -int(clean_digits)
        elif '-' in num_string:
            return -int(clean_digits)
        else:
            return int(clean_digits) 
 
class XBRLReader(abc.ABC):
 
    @abc.abstractmethod
    def getMarket(self):
        return NotImplemented
 
    @abc.abstractmethod
    def getValue(self, name, _contextRef):
        return NotImplemented

class HtmlReader(XBRLReader):
    def __init__(self, sourcePath):
        self.soup = BeautifulSoup(open(sourcePath, encoding="utf-8"), "html.parser")

    def getMarket(self):
        notes = self.soup.find("ix:nonnumeric", {"name" : "tifrs-notes:Market"})
        if (notes is None):
            return ""
        
        return notes.text  
    
    def getValue(self, name, _contextRef):
        pres = self.soup.find_all("pre")
        for pre in pres:
            item = pre.find("ix:nonfraction")
            if (item == None):
                continue
            
            if (item["name"] == name):
                if (item["contextref"] == _contextRef):
                    value = clean_num(pre.text)
                    return value
        
        return np.NaN
    
class XmlReader(XBRLReader):
    def __init__(self, sourcePath):
        self.soup = BeautifulSoup(open(sourcePath, encoding="utf-8"), "xml")
    
    def getMarket(self):
        notes = self.soup.find("tifrs-notes:Market")
        if (notes is None):
            return ""
        
        return notes.text  
    
    def getValue(self, name, _contextRef):
        item = self.soup.find(name, {"contextRef": _contextRef})
        
        if (item is None):
            return np.NaN

        value = int(clean_num(item.text) / 1000)
        return value

class ReadXBRL:
    def read(self, years, quarters):
        for year in years:
            for quarter in quarters:
                if (quarter == 1):
                    contextRef1 = "AsOf{0}0331".format(year) #資產負債表
                    contextRef2 = "From{0}0101To{0}0331".format(year) #損益表
                    contextRef3 = "From{0}0101To{0}0331".format(year) #現金流量表
                elif (quarter == 2):
                    contextRef1 = "AsOf{0}0630".format(year)
                    contextRef2 = "From{0}0101To{0}0630".format(year)
                    contextRef3 = "From{0}0101To{0}0630".format(year)
                elif (quarter == 3):
                    contextRef1 = "AsOf{0}0930".format(year)
                    contextRef2 = "From{0}0101To{0}0930".format(year)
                    contextRef3 = "From{0}0101To{0}0930".format(year)
                elif (quarter == 4):
                    contextRef1 = "AsOf{0}1231".format(year)
                    contextRef2 = "From{0}0101To{0}1231".format(year)
                    contextRef3 = "From{0}0101To{0}1231".format(year)
                else:
                    continue
        
                sourceDir = sourceDirFormat.format(year, quarter)
                if (not os.path.exists(sourceDir)):
                    continue
                
                files = os.listdir(sourceDir)
                print('start read xbrl year = {}, quarter = {}, files= {} =>'.format(year, quarter, len(files)))
                
                for file in files:
                    extension = os.path.splitext(file)[-1]
                    stockId = file.split('-')[5]
                    
                    # if ( not (stockId in stocks )):
                    #     continue
                        
                    sourcePath = os.path.join(sourceDir, file)
                    if (extension == ".html"):
                        reader = HtmlReader(sourcePath)
                    elif (extension == ".xml"):
                        reader = XmlReader(sourcePath)
                    
                        
                    market = reader.getMarket()
                    if not (market in ["Listed company", "Over-the-counter"]):
                        continue
                    
        
                    # 行業別代號：
                    # BASI（basi）：金融業
                    # BD（bd）：證券期貨業 6026
                    # CI（ci）：一般工商業 1101
                    # FH（fh）：金控業 2881
                    # INS（ins）：保險業 5828
                    # MIM（mim）：異業合併 2207
        
                    feildTable = pd.DataFrame(columns=["name", "contextRef", "useName", "value"])
                    
                    # 流動資產
                    feildTable = self.readCurrentAssets(feildTable, contextRef1)
                    # 現金及約當現金
                    feildTable = self.readCashAndCashEquivalents(feildTable, contextRef1)
                    # 金融資產－流動
                    feildTable = self.readCurrentFinancialAssets(feildTable, contextRef1)

                    # 金融資產－非流動
                    feildTable = self.readNoncurrentFinancialAssets(feildTable, contextRef1)
                    # 無形資產
                    feildTable = self.readIntangibleAsset(feildTable, contextRef1)
                    # 資產總計
                    feildTable = self.readAssets(feildTable, contextRef1)
                    
                    # 非流動負債
                    feildTable = self.readNoncurrentLiabilities(feildTable, contextRef1)
                    # 負債總計
                    feildTable = self.readLiabilities(feildTable, contextRef1)
                    # 股東權益
                    feildTable = self.readEquity(feildTable, contextRef1)
                    
                    # 營業收入
                    feildTable = self.readRevenue(feildTable, contextRef2)
                    # 營業毛利
                    feildTable = self.readGrossProfit(feildTable, contextRef2)
                    # 營業利益
                    feildTable = self.readOperatingProfit(feildTable, contextRef2)
                    # 繼續營業單位本期淨利
                    # 淨利（損）歸屬於：母公司業主（淨利／損）
                    feildTable = self.readAccProfitLossAttributableToOwnersOfParent(feildTable, contextRef2)

                    for index, data in feildTable.iterrows():
                        name = data["name"]
                        tmpContextRef = data["contextRef"]
        
                        value = reader.getValue(name, tmpContextRef)
                        feildTable.at[index, "value"] = value
        
                    targetfile = '{}.csv'.format(stockId)
                    targetPath = os.path.join(targetDir, targetfile)
                    if (os.path.exists(targetPath)):
                        newTable = pd.read_csv(targetPath)
                    else:
                        financeColumns = ["year", "quarter"]
                        financeColumns.extend(feildTable["useName"].unique())
                        newTable = pd.DataFrame(columns=financeColumns)
                    
                    
                    newTable = SetOrAdd(newTable, year, quarter, feildTable)
                    newTable.to_csv(targetPath, index=False, encoding='utf-8')
        
                print('<= end read xbrl')
                      
    # 無形資產
    def readIntangibleAsset(self, feildTable: pd.DataFrame, contextRef1):
        
        # 無形資產 - 2018 ~
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:IntangibleAssetsAndGoodwill",
                                                               "contextRef": contextRef1,
                                                               "useName": "IntangibleAsset"}, index=[0])], ignore_index = True)
        # 無形資產 - 金融業
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-basi:IntangibleAssetsNet ",
                                                               "contextRef": contextRef1,
                                                               "useName": "IntangibleAsset"}, index=[0])], ignore_index = True)
        # 無形資產 - 證券期貨業
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-bd:IntangibleAssets",
                                                               "contextRef": contextRef1,
                                                               "useName": "IntangibleAsset"}, index=[0])], ignore_index = True)
        # 無形資產 - 一般工商業
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-ci:IntangibleAssets",
                                                               "contextRef": contextRef1,
                                                               "useName": "IntangibleAsset"}, index=[0])], ignore_index = True)
        # 無形資產 - 金控業
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-fh:IntangibleAssetsNet",
                                                               "contextRef": contextRef1,
                                                               "useName": "IntangibleAsset"}, index=[0])], ignore_index = True)
        # 無形資產 - 保險業
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-ins:IntangibleAssets ",
                                                               "contextRef": contextRef1,
                                                               "useName": "IntangibleAsset"}, index=[0])], ignore_index = True)
        # 無形資產 - 異業合併
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-mim:IntangibleAssetsNet",
                                                               "contextRef": contextRef1,
                                                               "useName": "IntangibleAsset"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 股東權益
    def readEquity(self, feildTable, contextRef1):
        # 股東權益 - 2016, 2017
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:Equity",
                                                               "contextRef": contextRef1,
                                                               "useName": "Equity"}, index=[0])], ignore_index = True)
        # 股東權益 - 2018 ~
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:Equity",
                                                               "contextRef": contextRef1,
                                                               "useName": "Equity"}, index=[0])], ignore_index = True)                                 
        return feildTable
        
    # 資產總計
    def readAssets(self, feildTable, contextRef1):
        # 資產總計
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:Assets",
                                                               "contextRef": contextRef1,
                                                               "useName": "Assets"}, index=[0])], ignore_index = True)
        # 資產總計
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:Assets",
                                                               "contextRef": contextRef1,
                                                               "useName": "Assets"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 負債總計
    def readLiabilities(self, feildTable, contextRef1):
        # 負債總計
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:Liabilities",
                                                               "contextRef": contextRef1,
                                                               "useName": "Liabilities"}, index=[0])], ignore_index = True)
        # 負債總計
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:Liabilities",
                                                               "contextRef": contextRef1,
                                                               "useName": "Liabilities"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 非流動負債
    def readNoncurrentLiabilities(self, feildTable, contextRef1):
        # 非流動負債
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:NoncurrentLiabilities",
                                                               "contextRef": contextRef1,
                                                               "useName": "NoncurrentLiabilities"}, index=[0])], ignore_index = True)
        # 非流動負債
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:NoncurrentLiabilities",
                                                               "contextRef": contextRef1,
                                                               "useName": "NoncurrentLiabilities"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 流動資產
    def readCurrentAssets(self, feildTable, contextRef1):
        # 流動資產
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:CurrentAssets",
                                                               "contextRef": contextRef1,
                                                               "useName": "CurrentAssets"}, index=[0])], ignore_index = True)
        # 流動資產
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:CurrentAssets",
                                                               "contextRef": contextRef1,
                                                               "useName": "CurrentAssets"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 現金及約當現金
    def readCashAndCashEquivalents(self, feildTable, contextRef1):
        # 現金及約當現金
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:CashAndCashEquivalents",
                                                               "contextRef": contextRef1,
                                                               "useName": "CashAndCashEquivalents"}, index=[0])], ignore_index = True)
        # 現金及約當現金
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:CashAndCashEquivalents",
                                                               "contextRef": contextRef1,
                                                               "useName": "CashAndCashEquivalents"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 金融資產－流動
    def readCurrentFinancialAssets(self, feildTable, contextRef1):
        # 透過損益按公允價值衡量之金融資產－流動 (基金) 
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:CurrentFinancialAssetsAtFairValueThroughProfitOrLoss",
                                                               "contextRef": contextRef1,
                                                               "useName": "CurrentFinancialAssetsAtFairValueThroughProfitOrLoss"}, index=[0])], ignore_index = True)
        # 透過其他綜合損益按公允價值衡量之金融資產－流動 (股票)
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome",
                                                               "contextRef": contextRef1,
                                                               "useName": "CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"}, index=[0])], ignore_index = True)
        # 按攤銷後成本衡量之金融資產－流動 (定存)
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:CurrentFinancialAssetsAtAmortisedCost",
                                                               "contextRef": contextRef1,
                                                               "useName": "CurrentFinancialAssetsAtAmortisedCost"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 金融資產－非流動
    def readNoncurrentFinancialAssets(self, feildTable, contextRef1):
        # 透過損益按公允價值衡量之金融資產－流動 (基金) 
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss",
                                                               "contextRef": contextRef1,
                                                               "useName": "NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss"}, index=[0])], ignore_index = True)
        # 透過其他綜合損益按公允價值衡量之金融資產－流動 (股票)
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome",
                                                               "contextRef": contextRef1,
                                                               "useName": "NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"}, index=[0])], ignore_index = True)
        # 按攤銷後成本衡量之金融資產－流動 (定存)
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:NoncurrentFinancialAssetsAtAmortisedCost",
                                                               "contextRef": contextRef1,
                                                               "useName": "NoncurrentFinancialAssetsAtAmortisedCost"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 營業收入
    def readRevenue(self, feildTable, contextRef2):
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-basi:Income",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-basi:NetIncome",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-bd:OperatingRevenue",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-ci:OperatingRevenue",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-fh:NetIncomeLoss",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-ins:OperatingRevenue",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-min:OperatingRevenue",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        # 營業收入
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:Revenue",
                                                               "contextRef": contextRef2,
                                                               "useName": "Revenue"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 營業毛利
    def readGrossProfit(self, feildTable, contextRef2):
        # 營業毛利
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "tifrs-bsci-ci:GrossProfitLossFromOperationsNet",
                                                               "contextRef": contextRef2,
                                                               "useName": "GrossProfit"}, index=[0])], ignore_index = True)
        # 營業毛利
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:GrossProfit",
                                                               "contextRef": contextRef2,
                                                               "useName": "GrossProfit"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 營業利益
    def readOperatingProfit(self, feildTable, contextRef2):
        # 營業利益
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:ProfitLossFromOperatingActivities",
                                                               "contextRef": contextRef2,
                                                               "useName": "OperatingProfit"}, index=[0])], ignore_index = True)
        return feildTable
    
    # 繼續營業單位本期淨利
    # 淨利（損）歸屬於：母公司業主（淨利／損）
    def readAccProfitLossAttributableToOwnersOfParent(self, feildTable, contextRef2):
        # 以 淨利（損）歸屬於：母公司業主（淨利／損）為主, 不存在的, 則使用繼續營業單位本期淨利
        
        # 繼續營業單位本期淨利
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:ProfitLossFromContinuingOperations",
                                                               "contextRef": contextRef2,
                                                               "useName": "AccProfitLossAttributableToOwnersOfParent"}, index=[0])], ignore_index = True)
        # 繼續營業單位本期淨利
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:ProfitLossFromContinuingOperations",
                                                               "contextRef": contextRef2,
                                                               "useName": "AccProfitLossAttributableToOwnersOfParent"}, index=[0])], ignore_index = True)
        
        # 淨利（損）歸屬於：母公司業主（淨利／損）
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs:ProfitLossAttributableToOwnersOfParent",
                                                               "contextRef": contextRef2,
                                                               "useName": "AccProfitLossAttributableToOwnersOfParent"}, index=[0])], ignore_index = True)
        # 淨利（損）歸屬於：母公司業主（淨利／損）
        feildTable = pd.concat([feildTable, pd.DataFrame(data={"name": "ifrs-full:ProfitLossAttributableToOwnersOfParent",
                                                               "contextRef": contextRef2,
                                                               "useName": "AccProfitLossAttributableToOwnersOfParent"}, index=[0])], ignore_index = True)
        return feildTable

    # 產生現金流量、繼續營業利潤
    def makeCashFlow(self): 
        sourceDir = 'quarterly'
        targetDir = 'quarterly'
        files = os.listdir(sourceDir)
        print('file_number=', len(files))
            
        file_count = 0
        for file in files:
            stockId = file.split('.')[0]
            
            sourcePath = os.path.join(sourceDir, file)
            sourceData = pd.read_csv(sourcePath)
            
            sourceData = sourceData.sort_values(by = ['year', 'quarter'], ascending = False)
            sourceData["ProfitLossAttributableToOwnersOfParent"] = np.NaN
            
            for index, rowData in sourceData.iterrows():
                quarter1 = None
                if (rowData["quarter"] == 1): 
                    sourceData.at[index, "ProfitLossAttributableToOwnersOfParent"] = rowData["AccProfitLossAttributableToOwnersOfParent"]
                elif (rowData["quarter"] == 2): 
                    quarter1 = sourceData.loc[(sourceData['year'] == rowData["year"]) & (sourceData['quarter'] == 1)]
                elif (rowData["quarter"] == 3): 
                    quarter1 = sourceData.loc[(sourceData['year'] == rowData["year"]) & (sourceData['quarter'] == 2)]
                elif (rowData["quarter"] == 4): 
                    quarter1 = sourceData.loc[(sourceData['year'] == rowData["year"]) & (sourceData['quarter'] == 3)]
                else:
                    continue
                
                if isinstance(quarter1, pd.DataFrame):
                    if (quarter1.size > 0):
                        sourceData.at[index, "ProfitLossAttributableToOwnersOfParent"] = rowData["AccProfitLossAttributableToOwnersOfParent"] - quarter1["AccProfitLossAttributableToOwnersOfParent"].values[0]
            
            targetPath = os.path.join(targetDir, file)
            sourceData.to_csv(targetPath, index=False, encoding='utf-8')
        
        print('end!!!')
        
    def makeFinancialRatios(self):
        sourceDir = 'quarterly'
        targetDir = 'quarterly'
        files = os.listdir(sourceDir)
        print('start make financial ratios: file number is {} =>'.format(len(files)))
        
        for file in files:
            stockId = file.split('.')[0]

            sourcePath = os.path.join(sourceDir, file)
            sourceData = pd.read_csv(sourcePath)
                    
            if ( not ("CurrentAssets" in sourceData.columns.values)):
                sourceData["CurrentAssets"] = 0
        
            sourceData["CurrentAssets"] = sourceData["CurrentAssets"].fillna(0)
            
            if ( not ("IntangibleAsset" in sourceData.columns.values)):
                sourceData["IntangibleAsset"] = 0
        
            sourceData["IntangibleAsset"] = sourceData["IntangibleAsset"].fillna(0)
            
            if ( not ("NoncurrentLiabilities" in sourceData.columns.values)):
                sourceData["NoncurrentLiabilities"] = 0
        
            sourceData["NoncurrentLiabilities"] = sourceData["NoncurrentLiabilities"].fillna(0)
            
            if (not ("CashAndCashEquivalents" in sourceData.columns.values)):
                sourceData["CashAndCashEquivalents"] = 0
            sourceData["CashAndCashEquivalents"] = sourceData["CashAndCashEquivalents"].fillna(0)
            
            if (not ("CurrentFinancialAssetsAtFairValueThroughProfitOrLoss" in sourceData.columns.values)):
                sourceData["CurrentFinancialAssetsAtFairValueThroughProfitOrLoss"] = 0
            sourceData["CurrentFinancialAssetsAtFairValueThroughProfitOrLoss"] = sourceData["CurrentFinancialAssetsAtFairValueThroughProfitOrLoss"].fillna(0)
            
            if (not ("CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome" in sourceData.columns.values)):
                sourceData["CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"] = 0
            sourceData["CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"] = sourceData["CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"].fillna(0)
            
            if (not ("CurrentFinancialAssetsAtAmortisedCost" in sourceData.columns.values)):
                sourceData["CurrentFinancialAssetsAtAmortisedCost"] = 0
            sourceData["CurrentFinancialAssetsAtAmortisedCost"] = sourceData["CurrentFinancialAssetsAtAmortisedCost"].fillna(0)
            
            if (not ("NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss" in sourceData.columns.values)):
                sourceData["NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss"] = 0
            sourceData["NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss"] = sourceData["NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss"].fillna(0)
            
            if (not ("NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome" in sourceData.columns.values)):
                sourceData["NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"] = 0
            sourceData["NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"] = sourceData["NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"].fillna(0)
            
            if (not ("NoncurrentFinancialAssetsAtAmortisedCost" in sourceData.columns.values)):
                sourceData["NoncurrentFinancialAssetsAtAmortisedCost"] = 0
            sourceData["NoncurrentFinancialAssetsAtAmortisedCost"] = sourceData["NoncurrentFinancialAssetsAtAmortisedCost"].fillna(0)
            
            # 流動金融資產
            sourceData["CurrentFinancialAssets"] = 0
            sourceData["CurrentFinancialAssets"] += sourceData["CurrentFinancialAssetsAtFairValueThroughProfitOrLoss"]
            sourceData["CurrentFinancialAssets"] += sourceData["CurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"]
            sourceData["CurrentFinancialAssets"] += sourceData["CurrentFinancialAssetsAtAmortisedCost"]
            
            # 非流動金融資產
            sourceData["NoncurrentFinancialAssets"] = 0
            sourceData["NoncurrentFinancialAssets"] += sourceData["NoncurrentFinancialAssetsAtFairValueThroughProfitOrLoss"]
            sourceData["NoncurrentFinancialAssets"] += sourceData["NoncurrentFinancialAssetsAtFairValueThroughOtherComprehensiveIncome"]
            sourceData["NoncurrentFinancialAssets"] += sourceData["NoncurrentFinancialAssetsAtAmortisedCost"]
    
            # 現金, 約當現金, 流動金融資產, 非流動金融資產
            sourceData["CashAndCashEquivalents_All"] = sourceData["CashAndCashEquivalents"] + sourceData["CurrentFinancialAssets"] + sourceData["NoncurrentFinancialAssets"]
            
            # 有形資產淨值（Net Tangible Assets, NTA）
            sourceData["NetTangibleAssets"] = sourceData["Assets"] - sourceData["IntangibleAsset"] - sourceData["CashAndCashEquivalents_All"]
            
            # 生產力資產 => 非流動資產, 扣除無形資產, 非流動金融資
            sourceData["ProductivityAssets"] = sourceData["Assets"] - sourceData["IntangibleAsset"] - sourceData["CurrentAssets"] - sourceData["NoncurrentFinancialAssets"]
        
            # 收益
            sourceData["Profit"] = sourceData["ProfitLossAttributableToOwnersOfParent"]
            sourceData["Profit_4"] = sourceData["Profit"].rolling(window=4,center=False).sum().shift(-3)

            # 有形資產淨值收益率
            sourceData["ReturnOfNetTangibleAssets"] = sourceData["Profit"] / sourceData["NetTangibleAssets"]
            sourceData["ReturnOfNetTangibleAssets_4"] = sourceData["ReturnOfNetTangibleAssets"].rolling(window=4,center=False).sum().shift(-3)
            
            # 長期債務比率
            sourceData["LongDebtRatio"] = sourceData["NoncurrentLiabilities"] / sourceData["Assets"]
            
            if ( not ("Revenue" in sourceData.columns.values)):
                sourceData["Revenue"] = 0
            sourceData["Revenue"] = sourceData["Revenue"].fillna(0)
            
            # 毛利率
            if ( not ("GrossProfit" in sourceData.columns.values)):
                sourceData["GrossProfit"] = 0
            sourceData["GrossProfit"] = sourceData["GrossProfit"].fillna(0)
            sourceData["GrossProfitRatio"] = sourceData["GrossProfit"] / sourceData["Revenue"]
            
            # 營業利益率
            if ( not ("OperatingProfit" in sourceData.columns.values)):
                sourceData["OperatingProfit"] = 0
            sourceData["OperatingProfit"] = sourceData["OperatingProfit"].fillna(0)
            sourceData["OperatingProfitMargin"] = sourceData["OperatingProfit"] / sourceData["Revenue"]
            
            # 股東權益報酬率
            sourceData["ReturnOfEquity"] = sourceData["Profit"] / sourceData["Equity"]
            sourceData["ReturnOfEquity_4"] = sourceData["ReturnOfEquity"].rolling(window=4,center=False).sum().shift(-3)
            
            # 生產力資產報酬率
            sourceData["ReturnOfProductivityAssets"] = sourceData["Profit"] / sourceData["ProductivityAssets"]
            sourceData["ReturnOfProductivityAssets_4"] = sourceData["ReturnOfProductivityAssets"].rolling(window=4,center=False).sum().shift(-3)
            # 收購可能膨脹價值
            # 固定資產暴增可能膨脹價值
            
            targetPath = os.path.join(targetDir, file)
            sourceData.to_csv(targetPath, index=False, encoding='utf-8')
        
        print('<= end make financial ratios')