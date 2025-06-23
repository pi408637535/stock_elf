
# 导入 efinance 如果没有安装则需要通过执行命令: pip install efinance 来安装
import efinance as ef
# 股票代码
stock_code = '02601'
# 数据间隔时间为 1 分钟
freq = 1
# 获取最新一个交易日的分钟级别股票行情数据
df = ef.stock.get_quote_history(stock_code, klt=freq)
# 将数据存储到 csv 文件中
print(df)

