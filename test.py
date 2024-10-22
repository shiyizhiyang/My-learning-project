import xalpha as xa

# 假设 'yyws' 是你选择的基金代码
fund_code = 'yyws'
start_date = '2016-01-01'

# 创建买入并持有策略实例
st = xa.policy.buyandhold(fund_code, start_date)

# 配置策略以实现分红再投资
st.reinvest_dividends = True  # 确保分红再投资

# 运行模拟
results = st.simulate()

# 打印结果
print(results)