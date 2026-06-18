
import requests
import os
import pandas as pd
import shutil

class Basic:
    def downloadFile(self):
        downloadDir = 'download/basic'
        
        print('Beginning file download with requests')
        
        # 上市, 上櫃 基本資料
        targets = [['https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv', 'sii.csv'], 
                   ['https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv', 'otc.csv']]
        
        for target in targets:
            targetUrl = target[0]
            request = requests.get(targetUrl)
            savePath = os.path.join(downloadDir, target[1])
            with open(savePath, 'wb') as f:
                f.write(request.content)
                print('==> download file' + savePath)  
                        
        print('<= end download file') 

    def makeRawData(self):
        print('start make raw data =>') 
        sourceDir = 'download/basic'
        targetDir = 'raw/basic'
        backupDir = 'backup/download/basic'

        exchanges = ["sii", "otc"] 
        for exchange in exchanges: # 交易所
            file = "{}.csv".format(exchange)
            sourcePath = os.path.join(sourceDir, file)
            sourceData = pd.read_csv(sourcePath)
            sourceData = sourceData.rename(columns={'出表日期': 'dateTime',
                                                    '公司代號': 'stockId',
                                                    '已發行普通股數或TDR原股發行股數': 'commonStock'});
              
            targetPath = os.path.join(targetDir, file)
            
            newTable = pd.DataFrame()
            newTable["dateTime"] = sourceData["dateTime"]
            newTable["stockId"] = sourceData["stockId"]
            newTable["commonStock"] = sourceData["commonStock"]
            newTable.to_csv(targetPath, index=False, encoding='utf-8')

            shutil.move(sourcePath, os.path.join(backupDir, '{}_{}.csv'.format(exchange, sourceData.loc[0, 'dateTime'])));
            print('==> ' + file)
        print('<= end make raw data') 
        
    def concatBasicData(self):
        print('start concat basic data =>') 
        sourceDir = 'raw/basic'
        targetDir = 'basic'
        newTable = pd.DataFrame(columns=["dateTime", 
                                         "stockId", 
                                         # "name", 
                                         "commonStock"])
        files = os.listdir(sourceDir)
        for file in files:
            sourcePath = os.path.join(sourceDir, file)
            sourceData = pd.read_csv(sourcePath)
            newTable = pd.concat([newTable, sourceData], axis=0)
            os.remove(sourcePath)
        
        newTable.to_csv(os.path.join(targetDir, 'basic.csv'), index=False, encoding='utf-8')
        print('<= end concat basic data') 
        
        
        