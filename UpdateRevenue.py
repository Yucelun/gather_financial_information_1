from Revenue import Revenue

# years = [108]  # 年度
# months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # 月份

years = [115]  # 年度
months = [4, 5]  # 月份

revenue = Revenue()
# 下載營收
revenue.downloadFile(years, months)
# 產生營收原始資料
revenue.makeRawData(years, months)
# 產生每月營收
revenue.makeMonthly(years, months)
# 產生12月累積營收
revenue.makeRevenue12()