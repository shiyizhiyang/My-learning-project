import xalpha as xa
import pandas as pd
import matplotlib.pyplot as plt

class DailyDipInvestor:
    def __init__(self, fund_code, start_date, end_date, daily_investment, investment_frequency):
        self.fund_code = fund_code
        self.start_date = start_date
        self.end_date = end_date
        self.daily_investment = daily_investment  # 每日投资金额
        self.holding = 0  # 持有的基金单位
        self.holding_cost = 0  # 当前持仓的成本
        self.total_investment_cost = 0  # 总投资成本
        self.daily_interest_rate = 0.0001337  # 银行每年增长5%
        self.last_investment_date = pd.to_datetime(start_date)  # 上一次投资日期
        self.investment_frequency = investment_frequency  # 投资频率
        self.cash_growth_without_investment = 0  # 无投资的现金增长

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

        for date in times:
            price_row = self.price_data[self.price_data['date'] == date]
            if not price_row.empty:
                price = price_row['netvalue'].values[0]  # 使用净值
            else:
                continue

            # 更新资金
            self.cash_growth_without_investment *= (1 + self.daily_interest_rate)  # 无投资的现金增长
            self.holding += self.daily_investment / price  # 购买基金单位
            #self.holding_cost += self.daily_investment  # 更新持仓成本
            self.total_investment_cost += self.daily_investment  # 更新总投资成本
            self.cash_growth_without_investment += self.daily_investment  # 无投资现金增长

            # 计算当前持仓的收益
            current_holding_value = self.holding * price
            holding_gain_percentage = (
                (current_holding_value - self.total_investment_cost) / self.total_investment_cost * 100
                if self.total_investment_cost > 0 else 0
            )

            # 记录状态
            total_value = self.holding * price
            self.status.append({
                'date': date,
                'price': price,
                'holding': self.holding,
                'cash_growth_without_investment': self.cash_growth_without_investment,
                'total_value': total_value,
                'holding_gain_percentage': holding_gain_percentage,
                'total_investment_cost': self.total_investment_cost,  # 记录总投资成本
                'profit_rate': (total_value - self.total_investment_cost) / self.total_investment_cost * 100 ,  # 计算盈利率
            })

        self.status = pd.DataFrame(self.status)


        # 打印最终状态
        print(self.status)
        # 绘制持仓价值和无投资现金增长变化图表
        self.plot_cash_flow()

    def plot_cash_flow(self):
        plt.figure(figsize=(12, 6))
        total_value = self.status['holding'] * self.status['price']
        
        plt.plot(self.status['date'], self.status['cash_growth_without_investment'], label='Cash Growth (without Investment)', color='red', linestyle='--')
        plt.plot(self.status['date'], total_value, label='Holding Value', color='orange')
        plt.plot(self.status['date'], self.status['total_investment_cost'], label='Total Investment Cost', color='blue', linestyle='-')  # 新增总投资成本曲线
        
        # 标注末尾的值
        for i in range(len(self.status)):
            if i == len(self.status) - 1:  # 只标注最后一个点
                plt.annotate(f"{self.status['cash_growth_without_investment'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['cash_growth_without_investment'].iloc[i]),
                             textcoords="offset points",  # 位置偏移
                             xytext=(0, 10),  # 上方偏移10个点
                             ha='center', color='red')
                plt.annotate(f"{total_value.iloc[i]:.2f}",
                             (self.status['date'].iloc[i], total_value.iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='orange')
                plt.annotate(f"{self.status['total_investment_cost'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['total_investment_cost'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='blue')

        plt.title('Cash Growth, Holding Value, and Total Investment Cost')
        plt.xlabel('Date')
        plt.ylabel('Amount (Currency)')
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('cash_growth_holding_value_investment_cost.png')  # 保存为图像文件
        plt.show()

    

# 使用自定义策略
fund_code = '000369'  # 替换为实际基金代码
start_date = '2017-01-01'
end_date = '2024-01-01'  # 新增结束日期
daily_investment = 100  # 每日投资金额
investment_frequency = 'D'

strategy = DailyDipInvestor(fund_code, start_date, end_date, daily_investment, investment_frequency)
strategy.simulate()