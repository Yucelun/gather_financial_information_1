
import requests
import os
import pandas as pd
import shutil
            
class Revenue:
    def downloadFile(self, years, months):
        print('start download file =>') 
        targetDir = 'download/revenue'
        for year in years:
            for month in months: # 月份
                # 上市, 上櫃
                # targets = [['https://mops.twse.com.tw/nas/t21/sii/t21sc03_{}_{}.csv', os.path.join(targetDir, 'sii_{}_{}.csv')], 
                #            ['https://mops.twse.com.tw/nas/t21/otc/t21sc03_{}_{}.csv', os.path.join(targetDir, 'otc_{}_{}.csv')]]
                targets = [['https://mopsov.twse.com.tw/nas/t21/sii/t21sc03_{}_{}.csv', os.path.join(targetDir, 'sii_{}_{}.csv')], 
                           ['https://mopsov.twse.com.tw/nas/t21/otc/t21sc03_{}_{}.csv', os.path.join(targetDir, 'otc_{}_{}.csv')]]
                for target in targets:
                    targetUrl = target[0].format(year, month)
                    
                    print(targetUrl) 
                    request = requests.get(targetUrl)
                    
                    savePath = target[1].format(year, month)
                    with open(savePath, 'wb') as f:
                        f.write(request.content)
                print('==> download file' + savePath)  
                        
        print('<= end download file') 

    def makeRawData(self, years, months):
        print('start make raw data =>') 
        sourceDir = 'download/revenue'
        targetDir = 'raw/revenue'
        backupDir = 'backup/download/revenue'

        for year in years:
            for month in months: # 月份
                exchanges = ["sii", "otc"] 
                for exchange in exchanges: # 交易所
                    file = "{}_{}_{}.csv".format(exchange, year, month)
                    sourcePath = os.path.join(sourceDir, file)
                    sourceData = pd.read_csv(sourcePath)
                    sourceData = sourceData.rename(columns={'資料年月': 'dateTime',
                                                            '公司代號': 'stockId',
                                                            '公司名稱': 'name',
                                                            '營業收入-當月營收': 'revenue',
                                                            '營業收入-去年同月增減(%)': 'YoY'});
                      
                    targetPath = os.path.join(targetDir, file)
                    
                    newTable = pd.DataFrame()
                    newTable["dateTime"] = sourceData["dateTime"]
                    newTable["stockId"] = sourceData["stockId"]
                    newTable["name"] = sourceData["name"]
                    newTable["revenue"] = sourceData["revenue"]
                    newTable["YoY"] = sourceData["YoY"]
                    newTable.to_csv(targetPath, index=False, encoding='utf-8')
                    
                    shutil.move(sourcePath, os.path.join(backupDir, file))
                    print('==> ' + file)
        print('<= end make raw data') 

    def makeMonthly(self, years, months):
        print('start make monthly =>') 
        sourceDir = 'raw/revenue'
        targetDir = 'monthly'
            
        for year in years:
            for month in months: # 月份
                exchanges = ["sii", "otc"] 
                for exchange in exchanges: # 交易所
                    file = "{}_{}_{}.csv".format(exchange, year, month)
                    sourcePath = os.path.join(sourceDir, file)
                    sourceData = pd.read_csv(sourcePath)
        
                    for data_index, data_row in sourceData.iterrows():
                        stockId = data_row['stockId']
                        revenue = data_row['revenue']
                        YoY = data_row['YoY'] / 100
                        
                        targetfile = '{}.csv'.format(stockId)
                        targetPath = os.path.join(targetDir, targetfile)
        
                        if (os.path.exists(targetPath)):
                            newTable = pd.read_csv(targetPath)
                        else:
                            newTable = pd.DataFrame(columns=['year', 'month', 'revenue', 'YoY', 'revenue12'])

                        newTable = self.SetOrAddRevenue(newTable, year + 1911, month, revenue, YoY)
                        newTable = newTable.sort_values(by=["year", "month"], ascending = False)
                        newTable.to_csv(targetPath, index=False, encoding='utf-8')

                    os.remove(sourcePath)
                    print('==> ' + file)    
        print('<= end make monthly') 

    def makePerValue(self, years, months):
        print('start make per value =>') 
        sourceDir = 'raw/revenue'
        
        perValuePath = 'per_value.csv'
        if (os.path.exists(perValuePath)):
            perValueTable = pd.read_csv(perValuePath)
        else:
            perValueTable = pd.DataFrame(columns=['stockId', 'name', 'perValue']);
            
        for year in years:
            for month in months: # 月份
                exchanges = ["sii", "otc"] 
                for exchange in exchanges: # 交易所
                    file = "{}_{}_{}.csv".format(exchange, year, month)
                    sourcePath = os.path.join(sourceDir, file)
                    sourceData = pd.read_csv(sourcePath)
        
                    for data_index, data_row in sourceData.iterrows():
                        stockId = data_row['stockId']
                        name = data_row['name']
                        if (name.find('*') != -1):
                            perValueTable = self.SetOrAddPerValue(perValueTable, stockId, name)
                    
                    # os.remove(sourcePath)
                    print('==> ' + file)
             
        perValueTable.to_csv(perValuePath, index=False, encoding='utf-8')           
        print('<= end make per value') 
        
    def SetOrAddRevenue(self, table, year, month, revenue, YoY):
        for data_index, data_row in table.iterrows():
            if (data_row['year'] == year):
                if (data_row['month'] == month):
                    table.at[data_index, 'revenue'] = revenue
                    table.at[data_index, 'YoY'] = YoY
                    return table
                
        table.loc[len(table)] = [
            year,
            month,
            revenue,
            YoY,
            0
        ]
        return table

    def SetOrAddPerValue(self, table, stockId, name):
        for data_index, data_row in table.iterrows():
            if (data_row['stockId'] == stockId):
                table.at[data_index, 'name'] = name
                return table
            
        table.loc[len(table)] = [
            stockId,
            name,
        ]
        return table
    
    def makeRevenue12(self): 
        print('start make revenue12 =>') 
        sourceDir = 'monthly'
        targetDir = 'monthly'
        files = os.listdir(sourceDir)
        
        print('=> file number is', len(files))
        file_count = 0
        for file in files:
            sourcePath = os.path.join(sourceDir, file)
            sourceData = pd.read_csv(sourcePath)
            
            sourceData = sourceData.sort_values(by = ['year', 'month'], ascending = False)
            sourceData['revenue12'] = sourceData['revenue'].rolling(window=12,center=False).sum().shift(-11)
              
            targetPath = os.path.join(targetDir, file)
            sourceData.to_csv(targetPath, index=False, encoding='utf-8')
        
        print('<= end make revenue12') 