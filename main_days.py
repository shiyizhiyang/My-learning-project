import xalpha as xa
import pandas as pd
import matplotlib.pyplot as plt

class CustomInvestmentStrategy:
    def __init__(self, fund_code, start_date, end_date, total_investment, investment_frequency):
        self.fund_code = fund_code
        self.start_date = start_date
        self.end_date = end_date
        self.total_investment = total_investment
        self.cash_growth_without_investment = total_investment
        self.investment_frequency = investment_frequency
        self.status = []
        self.holding = 0
        self.cash = total_investment
        self.last_price = None
        self.holding_cost = 0  # 当前持仓的成本
        self.daily_interest_rate = 0.0001337  # 银行每年增长5%
        self.last_investment_date = pd.to_datetime(start_date)  # 上一次投资日期

        # 获取基金数据
        self.fund_data = xa.fundinfo(fund_code)
        self.get_price_data()

    def get_price_data(self):
        try:
            self.price_data = self.fund_data.price
            if self.price_data.empty:
                raise ValueError("价格数据为空，请检查基金代码或数据源。")
            self.price_data.columns = self.price_data.columns.str.strip().str.lower()
        except Exception as e:
            print(f"获取价格数据时出错: {e}")
            raise

    def simulate(self):
        self.status = []  # 重置状态
        # 使用结束日期生成日期范围
        times = pd.date_range(start=self.start_date, end=self.end_date, freq=self.investment_frequency)
        
        # 计算最大回升天数
        max_price = 0  # 记录基金的最高净值
        max_recovery_months = 0  # 记录最大回升月份数
        current_recovery_months = 0  # 当前回升月份计数
        for date in times:
            price_row = self.price_data[self.price_data['date'] == date]
            if not price_row.empty:
                price = price_row['netvalue'].values[0]  # 使用净值
            else:
                continue
            # 更新基金的最高净值
            if price > max_price:
                max_price = price
                current_recovery_months = 0  # 重置回升计数
            else:
                current_recovery_months += 1  # 增加回升月份计数
            # 更新最大回升月份数
            max_recovery_months = max(max_recovery_months, current_recovery_months)
        # 打印最大回升月份数
        print(f"最大回升天数: {max_recovery_months}")


        # 开始投资模拟
        monthly_investment = self.total_investment / max_recovery_months 
        monthly_investment = monthly_investment * 0.5 # 增加每月初始投资金额来增加波动进而增加收益
        monthly_investment_initial = monthly_investment
        
        for date in times:
            # 计算从上一次投资到当前日期的天数
            days_diff = (date - self.last_investment_date).days
            
            # 更新现金的增长
            self.cash *= (1 + self.daily_interest_rate) ** days_diff
            self.cash_growth_without_investment *=  (1 + self.daily_interest_rate) ** days_diff
            #print(f"date: {date} , cash_growth_without_investment: {self.cash_growth_without_investment}")
            #print(f"last_investment_date: {self.last_investment_date}")
            price_row = self.price_data[self.price_data['date'] == date]
            self.last_investment_date = date  # 更新最后投资日期
            if not price_row.empty:
                price = price_row['netvalue'].values[0]  # 使用净值
            else:
                continue

            # 计算当前每月可变投资金额
            if self.last_price is not None:
                price_change = (price - self.last_price)/self.last_price
                if price_change > 0:
                    monthly_investment /= (1 + 10*price_change)  # 上涨减少每月投资金额
                    #monthly_investment = monthly_investment 
                else :
                    monthly_investment *= (1 - 10*price_change)  # 下跌增加每月投资金额
                   #monthly_investment = monthly_investment 
            else:
                price_change = 0
            
            self.holding += monthly_investment / price  # 购买基金单位
            self.cash -= monthly_investment  # 减少现金
            #print(f"在 {date.date()} 买入，每月投资金额: {monthly_investment:.2f}, 现金: {self.cash:.2f}, 价格变化幅度: {price_change:.2%}")
            # 更新持仓成本
            self.holding_cost += monthly_investment  # 累加当前买入的成本

            # 计算当前持仓的收益
            current_holding_value = self.holding * price
            holding_gain_percentage = (
                (current_holding_value - self.holding_cost) / self.holding_cost * 100
                if self.holding_cost > 0 else 0
            )

            # #根据当前持仓的收益涨幅进行卖出判断
            # if holding_gain_percentage > 10:
            #     sell_amount = self.holding /3
            #     self.cash += sell_amount * price
            #     self.holding -= sell_amount
            #     # 更新持仓成本
            #     #self.holding_cost -= (sell_amount * price) / self.holding  # 更新持仓成本（按比例分配）
            #     self.holding_cost *= 2/3 # 更新持仓成本（按比例分配）
            #     monthly_investment = monthly_investment_initial  # 重新计算每月投资金额
            #     print(f"在 {date.date()} 全部卖出，持仓: {self.holding}, 现金: {self.cash}")


            if holding_gain_percentage > 4:
                sell_amount = self.holding/4
                self.cash += sell_amount * price
                self.holding -= sell_amount
                # 更新持仓成本
                #self.holding_cost -= (sell_amount * price) / self.holding  # 更新持仓成本（按比例分配）
                self.holding_cost *= 3/4  # 更新持仓成本（按比例分配）
                self.holding_cost *= (1 + holding_gain_percentage/100)
                print(f"收益率：{holding_gain_percentage},在 {date.date()} 卖出三分之一，持仓: {self.holding}, 现金: {self.cash}")
                monthly_investment = monthly_investment_initial  # 重新计算每月投资金额
            self.last_price = price

            # 记录状态
            total_value = self.cash + self.holding * price
            self.status.append({
            'date': date, 
            'price': price, 
            'holding': self.holding,
            'cash': self.cash, 
            'cash_growth_without_investment': self.cash_growth_without_investment,  # 添加这一行
            'total_value': total_value
        })

            # 每次投资后减少剩余月份
            #remaining_months -= 1

        self.status = pd.DataFrame(self.status)

        # 计算每个日期的盈利率，基于持有资产与总投资成本
        self.status['profit_rate'] = (self.status['holding'] * self.status['price'] + self.cash) / self.total_investment * 100

        # 打印最终状态并导出为 CSV
        print("最终状态:")
        print(self.status)
        self.status.to_csv('investment_status.csv', index=False)  # 导出为 CSV 文件

        # 绘制盈利率、现金流和总盈利率变化图表
        self.plot_cash_flow()
        self.visualize_table()



    def plot_cash_flow(self):
        plt.figure(figsize=(12, 6))
        
        # 计算总资金
        total_value = self.status['holding'] * self.status['price'] + self.status['cash']
        
        # 一次性买入后的总价值
        one_time_investment_value = self.total_investment * (self.status['price'] / self.status['price'].iloc[0])  # 假设一次性买入在开始时的价格
    
        # 绘制图表
        plt.plot(self.status['date'], self.status['cash_growth_without_investment'], label='Cash (without Investment)', color='red', linestyle='--')  # 只绘制不投资的现金增长
        plt.plot(self.status['date'], self.status['cash'], label='Cash (with Interest)', color='blue')
        plt.plot(self.status['date'], self.status['holding'] * self.status['price'], label='Holding Value', color='orange')
        plt.plot(self.status['date'], total_value, label='Total Value', color='green', linestyle='--')  # 添加总资金曲线
        plt.plot(self.status['date'], one_time_investment_value, label='One-time Investment Value', color='purple', linestyle=':')  # 添加一次性买入后的总价值曲线

        plt.title('Cash Flow, Holding Value, and One-time Investment Value Change')
        plt.xlabel('Date')
        plt.ylabel('Amount (Currency)')
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('cash_flow_change.png')  # 保存为图像文件
        plt.show()

    def visualize_table(self):
        # 可视化投资状态表格
        fig, ax = plt.subplots(figsize=(10, 6))  # 设置图形大小
        ax.axis('tight')
        ax.axis('off')
        table_data = self.status.values.tolist()  # 转换为列表
        columns = self.status.columns.tolist()  # 获取列名

        # 创建表格
        table = ax.table(cellText=table_data, colLabels=columns, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)  # 调整表格大小

        plt.title('Investment Status Table', fontsize=14)
        plt.savefig('investment_status_table.png')  # 保存为图像文件
        plt.show()

# 使用自定义策略
fund_code = '000369'  # 替换为实际基金代码
start_date = '2017-01-01'
end_date = '2024-01-01'  # 新增结束日期
total_investment = 10000  # 总投资金额
investment_frequency = 'D'

strategy = CustomInvestmentStrategy(fund_code, start_date, end_date, total_investment,investment_frequency)
strategy.simulate()