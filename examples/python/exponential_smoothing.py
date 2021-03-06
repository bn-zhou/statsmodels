# coding: utf-8

# DO NOT EDIT
# Autogenerated from the notebook exponential_smoothing.ipynb.
# Edit the notebook and then sync the output with this file.
#
# flake8: noqa
# DO NOT EDIT

# # 讲解
#
# 让我们思考一下 Hyndman 和 Athanasopoulos [1] 的关于指数平滑的优秀论文的第七章
# 我们通过此章论文的所有示例进行研究

# [1] [Hyndman, Rob J., 和 George Athanasopoulos. 预测: 原则和做法. OTexts, 2014.](https://www.otexts.org/fpp/7)

# # 指数平滑
#
# 首先，我们加载一些数据。 为了方便起见，我们的笔记中包含了 R 数据。

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

data = [
    446.6565, 454.4733, 455.663, 423.6322, 456.2713, 440.5881, 425.3325,
    485.1494, 506.0482, 526.792, 514.2689, 494.211
]
index = pd.DatetimeIndex(start='1996', end='2008', freq='A')
oildata = pd.Series(data, index)
oildata.index = pd.DatetimeIndex(
    oildata.index, freq=pd.infer_freq(oildata.index))

data = [
    17.5534, 21.86, 23.8866, 26.9293, 26.8885, 28.8314, 30.0751, 30.9535,
    30.1857, 31.5797, 32.5776, 33.4774, 39.0216, 41.3864, 41.5966
]
index = pd.DatetimeIndex(start='1990', end='2005', freq='A')
air = pd.Series(data, index)
air.index = pd.DatetimeIndex(air.index, freq=pd.infer_freq(air.index))

data = [
    263.9177, 268.3072, 260.6626, 266.6394, 277.5158, 283.834, 290.309,
    292.4742, 300.8307, 309.2867, 318.3311, 329.3724, 338.884, 339.2441,
    328.6006, 314.2554, 314.4597, 321.4138, 329.7893, 346.3852, 352.2979,
    348.3705, 417.5629, 417.1236, 417.7495, 412.2339, 411.9468, 394.6971,
    401.4993, 408.2705, 414.2428
]
index = pd.DatetimeIndex(start='1970', end='2001', freq='A')
livestock2 = pd.Series(data, index)
livestock2.index = pd.DatetimeIndex(
    livestock2.index, freq=pd.infer_freq(livestock2.index))

data = [407.9979, 403.4608, 413.8249, 428.105, 445.3387, 452.9942, 455.7402]
index = pd.DatetimeIndex(start='2001', end='2008', freq='A')
livestock3 = pd.Series(data, index)
livestock3.index = pd.DatetimeIndex(
    livestock3.index, freq=pd.infer_freq(livestock3.index))

data = [
    41.7275, 24.0418, 32.3281, 37.3287, 46.2132, 29.3463, 36.4829, 42.9777,
    48.9015, 31.1802, 37.7179, 40.4202, 51.2069, 31.8872, 40.9783, 43.7725,
    55.5586, 33.8509, 42.0764, 45.6423, 59.7668, 35.1919, 44.3197, 47.9137
]
index = pd.DatetimeIndex(start='2005', end='2010-Q4', freq='QS')
aust = pd.Series(data, index)
aust.index = pd.DatetimeIndex(aust.index, freq=pd.infer_freq(aust.index))

# ## 简单指数平滑
# 让我们使用“简单指数平滑”来预测以下油数据。

ax = oildata.plot()
ax.set_xlabel("Year")
ax.set_ylabel("Oil (millions of tonnes)")
plt.show()
print("Figure 7.1: Oil production in Saudi Arabia from 1996 to 2007.")

# 在这里，我们运行三种简单的指数平滑方法:
# 1. 在 ```fit1```中，我们不适用自动优化，而是选择为模型提供 $\alpha=0.2$ 参数
# 2. 在 ```fit2```中，我们选择 $\alpha=0.6$ 参数，同上
# 3. 在 ```fit3```中，我们允许 statsmodels 自动为我们找到一个优化的 $\alpha$ 值，这是推荐的方法。

fit1 = SimpleExpSmoothing(oildata).fit(smoothing_level=0.2, optimized=False)
fcast1 = fit1.forecast(3).rename(r'$\alpha=0.2$')
fit2 = SimpleExpSmoothing(oildata).fit(smoothing_level=0.6, optimized=False)
fcast2 = fit2.forecast(3).rename(r'$\alpha=0.6$')
fit3 = SimpleExpSmoothing(oildata).fit()
fcast3 = fit3.forecast(3).rename(
    r'$\alpha=%s$' % fit3.model.params['smoothing_level'])

ax = oildata.plot(marker='o', color='black', figsize=(12, 8))
fcast1.plot(marker='o', ax=ax, color='blue', legend=True)
fit1.fittedvalues.plot(marker='o', ax=ax, color='blue')
fcast2.plot(marker='o', ax=ax, color='red', legend=True)

fit2.fittedvalues.plot(marker='o', ax=ax, color='red')
fcast3.plot(marker='o', ax=ax, color='green', legend=True)
fit3.fittedvalues.plot(marker='o', ax=ax, color='green')
plt.show()

# ## Holt's 方法
#
# 让我们来看另一个例子
# 这次我们使用空气污染数据和 Holt's 方法.
# 我们将再次拟合三个示例数据.
# 1. 在 ```fit1```中，我们再次选择不适用优化器，并提供 $\alpha=0.8$ 和 $\beta=0.2$ 确切值
# 2. 在 ```fit2```中，我们使用与 ```fit1```一样做法（不适用优化器），但我们选择使用指数模型而不是 Holt's 加法模型.
# 3. 在 ```fit3```中，我们使用一个 Holt's 加法模型的阻尼版本，但在固定值 $\alpha=0.8$ 和 $\beta=0.2$的情况下，允许优化阻尼参数 $\phi$ 

fit1 = Holt(air).fit(smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
fcast1 = fit1.forecast(5).rename("Holt's linear trend")
fit2 = Holt(
    air, exponential=True).fit(
        smoothing_level=0.8, smoothing_slope=0.2, optimized=False)
fcast2 = fit2.forecast(5).rename("Exponential trend")
fit3 = Holt(air, damped=True).fit(smoothing_level=0.8, smoothing_slope=0.2)
fcast3 = fit3.forecast(5).rename("Additive damped trend")

ax = air.plot(color="black", marker="o", figsize=(12, 8))
fit1.fittedvalues.plot(ax=ax, color='blue')
fcast1.plot(ax=ax, color='blue', marker="o", legend=True)
fit2.fittedvalues.plot(ax=ax, color='red')
fcast2.plot(ax=ax, color='red', marker="o", legend=True)
fit3.fittedvalues.plot(ax=ax, color='green')
fcast3.plot(ax=ax, color='green', marker="o", legend=True)

plt.show()

# ### 季节性调整数据
# 让我们来看看季节性调整的牲畜数据。 我们拟合五个Holt模型。
#
# 下表我们可以比较 指数 vs 加法、阻尼 vs 非阻尼的结果。
#
# 请注意: 在```fit4```中，不允许通过提供固定值 $\phi=0.98$ 来优化参数 $\phi$
 

fit1 = SimpleExpSmoothing(livestock2).fit()
fit2 = Holt(livestock2).fit()
fit3 = Holt(livestock2, exponential=True).fit()
fit4 = Holt(livestock2, damped=True).fit(damping_slope=0.98)
fit5 = Holt(livestock2, exponential=True, damped=True).fit()
params = [
    'smoothing_level', 'smoothing_slope', 'damping_slope', 'initial_level',
    'initial_slope'
]
results = pd.DataFrame(
    index=[r"$\alpha$", r"$\beta$", r"$\phi$", r"$l_0$", "$b_0$", "SSE"],
    columns=['SES', "Holt's", "Exponential", "Additive", "Multiplicative"])
results["SES"] = [fit1.params[p] for p in params] + [fit1.sse]
results["Holt's"] = [fit2.params[p] for p in params] + [fit2.sse]
results["Exponential"] = [fit3.params[p] for p in params] + [fit3.sse]
results["Additive"] = [fit4.params[p] for p in params] + [fit4.sse]
results["Multiplicative"] = [fit5.params[p] for p in params] + [fit5.sse]
results

# ### 季节性调整数据图
# 下图允许我们去评估上表拟合的水平和斜率/趋势成分。

for fit in [fit2, fit4]:
    pd.DataFrame(np.c_[fit.level, fit.slope]).rename(columns={
        0: 'level',
        1: 'slope'
    }).plot(subplots=True)
plt.show()
print(
    'Figure 7.4: Level and slope components for Holt’s linear trend method and the additive damped trend method.'
)

# ## 对照
# 在这里，我们针对各种加法、指数和阻尼组合绘制一张简单指数平滑和Holt 方法的比较图。 statsmodels将优化所有模型参数。

fit1 = SimpleExpSmoothing(livestock2).fit()
fcast1 = fit1.forecast(9).rename("SES")
fit2 = Holt(livestock2).fit()
fcast2 = fit2.forecast(9).rename("Holt's")
fit3 = Holt(livestock2, exponential=True).fit()
fcast3 = fit3.forecast(9).rename("Exponential")
fit4 = Holt(livestock2, damped=True).fit(damping_slope=0.98)
fcast4 = fit4.forecast(9).rename("Additive Damped")
fit5 = Holt(livestock2, exponential=True, damped=True).fit()
fcast5 = fit5.forecast(9).rename("Multiplicative Damped")

ax = livestock2.plot(color="black", marker="o", figsize=(12, 8))
livestock3.plot(ax=ax, color="black", marker="o", legend=False)
fcast1.plot(ax=ax, color='red', legend=True)
fcast2.plot(ax=ax, color='green', legend=True)
fcast3.plot(ax=ax, color='blue', legend=True)
fcast4.plot(ax=ax, color='cyan', legend=True)
fcast5.plot(ax=ax, color='magenta', legend=True)
ax.set_ylabel('Livestock, sheep in Asia (millions)')
plt.show()
print(
    'Figure 7.5: Forecasting livestock, sheep in Asia: comparing forecasting performance of non-seasonal methods.'
)

# ## Holt's 冬天季节性
# 最后，我们能够运行完整的 Holt's 冬天季节性指数平滑，包括趋势和季节成分。 statsmodels 允许包括以下示例所示的所有组合：

# 1. 在```fit1```中增加趋势性和季节性周期  ```season_length=4``` 并使用一个 Box-Cox 进行转换.
# 2. 在```fit2```中增加趋势性和倍增的季节性周期  ```season_length=4``` 并使用一个 Box-Cox 进行转换
# 3. 在```fit3```中增加阻尼趋势性和季节性周期 ```season_length=4``` 并使用一个 Box-Cox 进行转换
# 4. 在```fit4```中增加阻尼趋势性和倍增季节性周期 ```season_length=4``` 并使用一个 Box-Cox 进行转换
#
# 该图展示了`fit1`和`fit2`的结果和预测。 该表比较了结果和参数设置。

fit1 = ExponentialSmoothing(
    aust, seasonal_periods=4, trend='add', seasonal='add').fit(use_boxcox=True)
fit2 = ExponentialSmoothing(
    aust, seasonal_periods=4, trend='add', seasonal='mul').fit(use_boxcox=True)
fit3 = ExponentialSmoothing(
    aust, seasonal_periods=4, trend='add', seasonal='add',
    damped=True).fit(use_boxcox=True)
fit4 = ExponentialSmoothing(
    aust, seasonal_periods=4, trend='add', seasonal='mul',
    damped=True).fit(use_boxcox=True)
results = pd.DataFrame(index=[
    r"$\alpha$", r"$\beta$", r"$\phi$", r"$\gamma$", r"$l_0$", "$b_0$", "SSE"
])
params = [
    'smoothing_level', 'smoothing_slope', 'damping_slope',
    'smoothing_seasonal', 'initial_level', 'initial_slope'
]
results["Additive"] = [fit1.params[p] for p in params] + [fit1.sse]
results["Multiplicative"] = [fit2.params[p] for p in params] + [fit2.sse]
results["Additive Dam"] = [fit3.params[p] for p in params] + [fit3.sse]
results["Multiplica Dam"] = [fit4.params[p] for p in params] + [fit4.sse]

ax = aust.plot(
    figsize=(10, 6),
    marker='o',
    color='black',
    title="Forecasts from Holt-Winters' multiplicative method")
ax.set_ylabel("International visitor night in Australia (millions)")
ax.set_xlabel("Year")
fit1.fittedvalues.plot(ax=ax, style='--', color='red')
fit2.fittedvalues.plot(ax=ax, style='--', color='green')

fit1.forecast(8).rename('Holt-Winters (add-add-seasonal)').plot(
    ax=ax, style='--', marker='o', color='red', legend=True)
fit2.forecast(8).rename('Holt-Winters (add-mul-seasonal)').plot(
    ax=ax, style='--', marker='o', color='green', legend=True)

plt.show()
print(
    "Figure 7.6: Forecasting international visitor nights in Australia using Holt-Winters method with both additive and multiplicative seasonality."
)

results

# ### The Internals
# 可以了解指数平滑模型的内部。
#
# 在这里我们展示一些表格允许你并排查看原始值 $y_t$, 水平 $l_t$, 趋势性 $b_t$, 季节性 $s_t$ 和拟合值 $\hat{y}_t$.

df = pd.DataFrame(
    np.c_[aust, fit1.level, fit1.slope, fit1.season, fit1.fittedvalues],
    columns=[r'$y_t$', r'$l_t$', r'$b_t$', r'$s_t$', r'$\hat{y}_t$'],
    index=aust.index)
df.append(fit1.forecast(8).rename(r'$\hat{y}_t$').to_frame(), sort=True)

df = pd.DataFrame(
    np.c_[aust, fit2.level, fit2.slope, fit2.season, fit2.fittedvalues],
    columns=[r'$y_t$', r'$l_t$', r'$b_t$', r'$s_t$', r'$\hat{y}_t$'],
    index=aust.index)
df.append(fit2.forecast(8).rename(r'$\hat{y}_t$').to_frame(), sort=True)

# 最后，让我们看一下模型的水平，斜率/趋势和季节性成分。

states1 = pd.DataFrame(
    np.c_[fit1.level, fit1.slope, fit1.season],
    columns=['level', 'slope', 'seasonal'],
    index=aust.index)
states2 = pd.DataFrame(
    np.c_[fit2.level, fit2.slope, fit2.season],
    columns=['level', 'slope', 'seasonal'],
    index=aust.index)
fig, [[ax1, ax4], [ax2, ax5], [ax3, ax6]] = plt.subplots(3, 2, figsize=(12, 8))
states1[['level']].plot(ax=ax1)
states1[['slope']].plot(ax=ax2)
states1[['seasonal']].plot(ax=ax3)
states2[['level']].plot(ax=ax4)
states2[['slope']].plot(ax=ax5)
states2[['seasonal']].plot(ax=ax6)
plt.show()
