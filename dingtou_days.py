import xalpha as xa
import pandas as pd
import matplotlib.pyplot as plt

class DailyDipInvestor:
    def __init__(self, fund_code, start_date, end_date, daily_investment, investment_frequency):
        self.fund_code = fund_code
        self.start_date = start_date
        self.end_date = end_date
        self.daily_investment_default = daily_investment  # 默认每日投资金额
        self.daily_investment_custom = daily_investment  # 自定义每日投资金额
        self.investment_frequency = investment_frequency
        self.holding_default = 0  # 默认投资策略的持仓
        self.holding_custom = 0  # 自定义投资策略的持仓
        self.total_investment_cost_default = 0  # 默认投资策略的总投资成本
        self.total_investment_cost_custom = 0  # 自定义投资策略的总投资成本
        self.daily_interest_rate = 0.0001337  # 银行每年增长5%
        self.cash_growth_without_investment_default = 0  # 默认无投资的现金增长
        self.cash_growth_without_investment_custom = 0  # 自定义无投资的现金增长
        self.last_price = None  # 上一个价格
        self.previous_high = 0  # 前高净值
        self.last_investment_date = pd.to_datetime(start_date)
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
            days_diff = (date - self.last_investment_date).days
            # 更新无投资现金增长
            self.cash_growth_without_investment_default *= (1 + self.daily_interest_rate)**days_diff
            self.cash_growth_without_investment_default += self.daily_investment_default
            
            # 更新自定义的现金增长
            self.cash_growth_without_investment_custom *= (1 + self.daily_interest_rate)**days_diff
            self.cash_growth_without_investment_custom += self.daily_investment_custom

            # 检查当前价格是否为新高
            if price > self.previous_high:
                self.previous_high = price  # 更新前高
                self.daily_investment_custom = self.daily_investment_default  # 重置自定义每日投资金额

            # 进行默认投资
            self.holding_default += self.daily_investment_default / price  # 购买基金单位
            self.total_investment_cost_default += self.daily_investment_default  # 更新总投资成本

            # 计算自定义策略的每日投资金额
            if self.last_price is not None:
                price_change = (price - self.last_price) / self.last_price
                if price_change > 0:
                    self.daily_investment_custom /= (1 + 5*price_change)  # 净值上涨，减少投资金额
                else:
                    self.daily_investment_custom *= (1 - 5*price_change)  # 净值下跌，增加投资金额
            else:
                self.daily_investment_custom = self.daily_investment_default  # 如果没有上一个价格，使用默认投资金额

            self.holding_custom += self.daily_investment_custom / price  # 购买基金单位
            self.total_investment_cost_custom += self.daily_investment_custom  # 更新总投资成本

            self.last_price = price  # 更新上一个价格
            self.last_investment_date = date
            # 计算当前持仓的收益
            current_value_default = self.holding_default * price
            current_value_custom = self.holding_custom * price
            
            # 计算收益率
            return_rate_default = (current_value_default / self.total_investment_cost_default) * 100 if self.total_investment_cost_default > 0 else 0
            return_rate_custom = (current_value_custom / self.total_investment_cost_custom) * 100 if self.total_investment_cost_custom > 0 else 0

            # 记录状态
            self.status.append({
                'date': date,
                'price': price,
                'holding_default': self.holding_default,
                'holding_custom': self.holding_custom,
                'cash_growth_without_investment_default': self.cash_growth_without_investment_default,
                'cash_growth_without_investment_custom': self.cash_growth_without_investment_custom,
                'total_value_default': current_value_default,
                'total_value_custom': current_value_custom,
                'holding_gain_percentage_default': return_rate_default,
                'holding_gain_percentage_custom': return_rate_custom,
                'total_investment_cost_default': self.total_investment_cost_default,
                'total_investment_cost_custom': self.total_investment_cost_custom,
            })

        self.status = pd.DataFrame(self.status)

    def plot_cash_flow(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.status['date'], self.status['cash_growth_without_investment_default'], 
                 label='Cash Growth (Default)', color='red', linestyle=':')  # 默认现金增长的点状线
        plt.plot(self.status['date'], self.status['cash_growth_without_investment_custom'], 
                 label='Cash Growth (Custom)', color='blue', linestyle=':')  # 自定义现金增长的点状线
        plt.plot(self.status['date'], self.status['total_value_default'], 
                 label='Holding Value (Default Strategy)', color='red')
        plt.plot(self.status['date'], self.status['total_value_custom'], 
                 label='Holding Value (Custom Strategy)', color='blue')
        plt.plot(self.status['date'], self.status['total_investment_cost_default'], 
                 label='Total Investment Cost (Default Strategy)', color='red', linestyle='-')
        plt.plot(self.status['date'], self.status['total_investment_cost_custom'], 
                 label='Total Investment Cost (Custom Strategy)', color='blue', linestyle='-')

        # 标注末尾的值
        for i in range(len(self.status)):
            if i == len(self.status) - 1:  # 只标注最后一个点
                plt.annotate(f"{self.status['cash_growth_without_investment_default'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['cash_growth_without_investment_default'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='yellow')
                plt.annotate(f"{self.status['cash_growth_without_investment_custom'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['cash_growth_without_investment_custom'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='green')
                plt.annotate(f"{self.status['total_value_default'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['total_value_default'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='orange')
                plt.annotate(f"{self.status['total_value_custom'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['total_value_custom'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='blue')
                plt.annotate(f"{self.status['total_investment_cost_default'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['total_investment_cost_default'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='orange')
                plt.annotate(f"{self.status['total_investment_cost_custom'].iloc[i]:.2f}",
                             (self.status['date'].iloc[i], self.status['total_investment_cost_custom'].iloc[i]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', color='blue')

        # 设置标题
        plt.title('Cash Growth, Holding Value, and Total Investment Cost Comparison')
        plt.xlabel('Date')
        plt.ylabel('Amount (Currency)')
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('cash_growth_holding_value_investment_cost_comparison.png')  # 保存为图像文件
        plt.show()

    def plot_return_rate(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.status['date'], self.status['holding_gain_percentage_default'], 
                 label='Return Rate (Default)', color='orange')  # 默认收益率
        plt.plot(self.status['date'], self.status['holding_gain_percentage_custom'], 
                 label='Return Rate (Custom)', color='blue')  # 自定义收益率

        # 设置标题
        plt.title('Return Rate Comparison')
        plt.xlabel('Date')
        plt.ylabel('Return Rate (%)')
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('return_rate_comparison.png')  # 保存为图像文件
        plt.show()


# 使用自定义策略
fund_code = '000369'  # 替换为实际基金代码
start_date = '2017-01-01'
end_date = '2024-01-01'  # 新增结束日期
daily_investment = 100  # 每日投资金额
investment_frequency = 'B'

strategy = DailyDipInvestor(fund_code, start_date, end_date, daily_investment, investment_frequency)
strategy.simulate()
# 打印最终状态
print(strategy.status)
# 绘制持仓价值和无投资现金增长变化图表
strategy.plot_cash_flow()
# 绘制收益率对比图
strategy.plot_return_rate()