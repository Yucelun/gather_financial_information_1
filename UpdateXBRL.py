from ReadXBRL import ReadXBRL

# years = [2018, 2019, 2020, 2021, 2022]
# quarters = [1, 2, 3, 4]

years = [2026]
quarters = [1]

readXBRL = ReadXBRL()
# 讀取財報資料
readXBRL.read(years, quarters)
# 產生現金流量、繼續營業利潤
readXBRL.makeCashFlow()
# 產生財務比率
readXBRL.makeFinancialRatios()
