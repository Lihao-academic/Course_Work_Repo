# Pairs_Trading_on_the_S&P_500

[中文](#基于_S&P_500_的配对交易研究) | [English](#Pairs_Trading_on_the_S&P_500)

> Does a cointegration-based, market-neutral pairs-trading strategy remain profitable out of sample and after transaction costs?

This project develops and evaluates a statistical-arbitrage strategy on the historical S&P 500 universe. It uses a walk-forward research design: pairs are selected from a three-year formation window, traded during the following six months with frozen parameters, and then re-estimated as the sample moves forward.

The main finding is straightforward: the strategy achieves very low market exposure and exhibits a small gross mean-reversion edge, but a 10-basis-point trading cost is enough to eliminate that edge. In this implementation, pairs trading behaves more like a low-correlation diversifier than a profitable stand-alone strategy.

## Research question

The project asks:

> Can a market-neutral pairs-trading strategy deliver better risk-adjusted performance than S&P 500 buy-and-hold?

The analysis separates statistical evidence from economic profitability. Two stocks may be cointegrated in the formation period, yet their convergence can still be too slow, unstable, or costly to trade profitably out of sample.

## Strategy overview

For each candidate pair, log prices are modelled as

$$
\log P_{Y,t}=\alpha+\beta\log P_{X,t}+\varepsilon_t.
$$

If the residual is stationary, the two price series are treated as cointegrated and the residual becomes the tradable spread:

$$
S_t=\log P_{Y,t}-\alpha-\beta\log P_{X,t}.
$$

The standardized spread is

$$
z_t=\frac{S_t-\mu_S}{\sigma_S},
$$

where all parameters are estimated only from the formation period.

| Signal | Position |
|---|---|
| $z_t\leq-2$ | Long the spread: long $Y$, short $X$ |
| $z_t\geq+2$ | Short the spread: short $Y$, long $X$ |
| Spread returns to the exit band | Close the position |
| $\lvert z_t\rvert\geq3$ while a position is open | Stop loss |
| End of the trading window | Force close |

The legs are normalized using the estimated hedge ratio:

$$
w_Y=\frac{1}{1+\beta},\qquad
w_X=\frac{\beta}{1+\beta}.
$$

The cointegration coefficient $\beta$ is a hedge ratio between the two securities; it is not the CAPM market beta.

## Data

The study uses a historical S&P 500 dataset covering January 1990 to November 2018.

- 1,355 historical constituents
- 1,509 weekly observations
- Friday closing prices
- Historical monthly index weights for the investable universe
- Bloomberg sector classifications
- S&P 500 price index as the benchmark

Using historical membership reduces survivorship bias: securities are eligible according to the index composition available at each formation date, rather than according to the present-day constituent list.

The raw course dataset is not included in this repository. To reproduce the analysis, place the source workbook in the location configured in `extract_data.py`.

## Walk-forward design

Each experiment consists of two non-overlapping stages:

1. **Formation period — 156 weeks:** clean the universe, test candidate pairs, estimate hedge ratios and spread parameters, and select up to 20 pairs.
2. **Trading period — 26 weeks:** keep the selected pairs and parameters fixed, generate weekly signals, and record genuinely out-of-sample returns.

The procedure rolls forward by 26 weeks and produces 52 out-of-sample trading windows from 1993 to 2018. Current-close signals are applied to the following week's return through lagged positions, preventing the strategy from earning returns that had already occurred when the signal became observable.

## Pair selection

Candidate pairs are evaluated with the Engle–Granger cointegration procedure. The baseline selection rules are:

- same-sector candidates;
- cointegration test with $p<0.05$;
- hedge ratio $0.1\leq\beta\leq10$;
- estimated half-life between 1 and 26 weeks;
- ranking by cointegration p-value;
- no stock may appear in more than one selected pair;
- up to 20 pairs per trading window.

The half-life approximates the time required for half of a spread deviation to disappear and filters out spreads that are either implausibly fast or too slow for the six-month trading window.

## Portfolio construction

- Capital is allocated equally across the selected pairs.
- A pair that is flat or stopped remains in cash; its allocation is not redistributed to active pairs.
- Weekly P&L uses the previous week's position.
- The baseline cost is 10 bps per unit of position change, approximately 20 bps for a standard open-and-close round trip.
- Positions still open at the end of a window are closed and charged the corresponding cost.

Because inactive allocations remain in cash, realized gross exposure can be substantially below 100%. This helps explain the strategy's low volatility and should be considered when comparing it with an always-invested equity benchmark.

## Baseline results

The current notebook reports the following out-of-sample results for 1993–2018:

| Metric | Pairs — net | Pairs — gross | S&P 500 |
|---|---:|---:|---:|
| Cumulative return | -2.75% | 6.43% | 498.62% |
| CAGR | -0.11% | 0.24% | 7.12% |
| Annualized volatility | 1.75% | 1.74% | 16.41% |
| Sharpe ratio | -0.05 | 0.15 | 0.50 |
| Maximum drawdown | -7.84% | -7.02% | -56.24% |
| Correlation with S&P 500 | 0.08 | 0.08 | — |
| Market beta | 0.01 | 0.01 | — |

During 2008, the pairs portfolio returned approximately **+1.6%**, while the S&P 500 price index returned approximately **-41.0%**. This supports the market-neutrality claim, but it does not by itself establish economic profitability over the full sample.

### Transaction-cost sensitivity

| Cost per unit of position change | CAGR | Sharpe ratio |
|---:|---:|---:|
| 0 bps | 0.24% | 0.15 |
| 10 bps | -0.11% | -0.05 |
| 20 bps | -0.45% | -0.25 |
| 40 bps | -1.14% | -0.63 |

The gross edge is positive but economically small. Even modest execution costs are sufficient to turn the net result negative.

## Interpretation

The strategy succeeds at reducing broad market exposure, but not at producing attractive risk-adjusted returns:

- market correlation and CAPM beta are close to zero;
- gross returns contain a weak mean-reversion signal;
- transaction costs absorb the signal;
- low drawdown partly reflects low realized exposure and time spent in cash;
- cointegration in the formation period does not guarantee profitable convergence later.

The result is therefore a negative but informative finding: statistical relationships can survive out of sample without being strong enough to trade profitably.

## Repository structure

```text
.
├── extract_data.py       # Extracts and cleans the source workbook
├── *.ipynb               # Pair selection, backtest, analysis, and figures
├── data_cache/           # Generated Parquet/CSV cache files
├── README.md             # English documentation
└── README.zh-CN.md       # Chinese documentation
```

Generated cache files and proprietary raw data should normally be excluded from version control.

## Getting started

Python 3.10 or later is recommended.

```bash
cd FMAproject_PairsTrading

python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.venv\Scripts\activate
```

Install the main dependencies:

```bash
python -m pip install pandas numpy scipy statsmodels matplotlib seaborn jupyter pyarrow openpyxl
```

`pyarrow` is required because the extraction script stores intermediate data in Parquet format.

Run the data-extraction step:

```bash
python extract_data.py
```

Then open the analysis notebook:

```bash
jupyter lab
```

## Reproducibility note

The table above records the current baseline notebook output. Before treating these numbers as final, the following implementation checks should be completed and the full backtest rerun:

- validate the sector-label extraction and same-sector filter;
- charge opening costs correctly when a position is inherited from the seed week;
- prevent new entries beyond the stop boundary;
- close positions on the final common quote date when a security disappears;
- use a consistent convention for log returns versus simple-return compounding;
- report average active-pair count and realized gross exposure.

These checks affect execution accuracy and may change the reported performance, although they do not alter the walk-forward research framework.

## Limitations and possible extensions

Current limitations include multiple-testing risk, possible structural breaks in cointegration, fixed hedge ratios, simplified transaction costs, no explicit borrow fees or short-sale constraints, omitted dividend cash flows, and use of a price index rather than a total-return benchmark.

Possible extensions include:

- false-discovery-rate correction for pair selection;
- volatility-scaled portfolio allocation;
- time-varying hedge ratios using a Kalman filter;
- alternative distance or Johansen selection methods;
- explicit modelling of cash interest, dividends, financing, and stock-borrow costs;
- comparison with European equities or different trading frequencies.

## Academic context

This project was developed for the **Financial Markets Analytics** course as an empirical study of pairs trading, cointegration, portfolio construction, and out-of-sample evaluation.

## Disclaimer

This repository is for academic and educational purposes only. It does not constitute investment advice, and the backtest does not represent live trading performance.

# 基于_S&P_500_的配对交易研究

[中文](#基于_S&P_500_的配对交易研究) | [English](#Pairs_Trading_on_the_S&P_500)

> 基于协整关系的市场中性配对交易策略，在样本外并扣除交易成本后，是否仍然能够盈利？

本项目在历史 S&P 500 成分股上构建并检验了一套统计套利策略。研究采用滚动前推（walk-forward）设计：先用三年的形成期选择配对并估计参数，再在随后六个月中固定参数进行交易，之后继续向前滚动并重新估计。

项目得到的主要结论很直接：策略确实实现了极低的市场暴露，并在扣除成本前表现出微弱的均值回归优势；但每次仓位变化 10 个基点的交易成本已经足以完全消耗这一优势。在当前实现下，配对交易更像是一种与市场低相关的分散化工具，而不是能够独立产生高收益的策略。

## 研究问题

本项目试图回答：

> 一套市场中性的配对交易策略，能否获得优于 S&P 500 买入并持有的风险调整后收益？

研究中特别区分了统计显著性与经济盈利能力。两只股票在形成期存在协整关系，并不代表它们在样本外一定会及时收敛，更不代表收敛产生的收益足以覆盖交易成本。

## 策略原理

对于每一组候选股票，首先对对数价格建立回归：

$$
\log P_{Y,t}=\alpha+\beta\log P_{X,t}+\varepsilon_t.
$$

如果残差是平稳序列，则认为两个价格序列存在协整关系，并将残差定义为可交易的价差：

$$
S_t=\log P_{Y,t}-\alpha-\beta\log P_{X,t}.
$$

价差的标准分数为：

$$
z_t=\frac{S_t-\mu_S}{\sigma_S},
$$

其中所有参数都只能使用形成期数据估计。

| 信号 | 仓位 |
|---|---|
| $z_t\leq-2$ | 做多价差：做多 $Y$、做空 $X$ |
| $z_t\geq+2$ | 做空价差：做空 $Y$、做多 $X$ |
| 价差回到退出区间 | 平仓 |
| 持仓时 $\lvert z_t\rvert\geq3$ | 止损 |
| 交易窗口结束 | 强制平仓 |

两条交易腿根据协整系数进行归一化：

$$
w_Y=\frac{1}{1+\beta},\qquad
w_X=\frac{\beta}{1+\beta}.
$$

这里的 $\beta$ 是两只股票之间的协整对冲比例，并不是 CAPM 中衡量市场风险暴露的 beta。

## 数据

研究使用覆盖 1990 年 1 月至 2018 年 11 月的历史 S&P 500 数据集。

- 1,355 只历史成分股
- 1,509 个周度观测
- 每周五收盘价
- 用于确定各期可投资股票池的历史月度指数权重
- Bloomberg 行业分类
- 以 S&P 500 价格指数作为基准

项目根据每个形成期当时的指数成分构建股票池，而不是只使用今天仍然存续的成分股，因此能够降低幸存者偏差。

课程提供的原始数据不包含在本仓库中。如需复现分析，请将源 Excel 工作簿放到 `extract_data.py` 中配置的位置。

## 滚动样本外设计

每轮实验包括两个互不重叠的阶段：

1. **形成期——156 周：**清理股票池、检验候选配对、估计对冲比例与价差参数，并选出最多 20 组股票。
2. **交易期——26 周：**固定已经选出的配对和参数，生成周度交易信号，并记录真正的样本外收益。

整个流程每 26 周向前滚动一次，从 1993 年到 2018 年共形成 52 个样本外交易窗口。本周收盘时得到的信号只能影响下一周仓位，因此收益计算使用滞后一期的仓位，避免利用信号形成前已经发生的价格变化。

## 配对选择

候选股票使用 Engle–Granger 协整检验进行筛选。基准规则如下：

- 只比较同一行业内的股票；
- 协整检验要求 $p<0.05$；
- 对冲比例满足 $0.1\leq\beta\leq10$；
- 估计半衰期为 1–26 周；
- 按协整检验 p 值排序；
- 同一只股票不能同时出现在多个入选配对中；
- 每个交易窗口最多选择 20 组配对。

半衰期近似表示价差偏离消失一半所需的时间。该指标用于剔除收敛速度不合理或相对于六个月交易期过慢的价差。

## 组合构建

- 在选出的配对之间等额分配资本。
- 未开仓或止损后的配对保持现金，其资本不会重新分配给其他活跃配对。
- 周度损益使用上一周的仓位计算。
- 基准交易成本为每单位仓位变化 10 个基点，标准开仓—平仓往返交易约为 20 个基点。
- 交易窗口结束时仍未平仓的仓位会被强制关闭，并计入相应成本。

由于未交易的资本继续以现金形式存在，策略实际总敞口可能明显低于 100%。这也是策略波动率很低的重要原因，在与始终满仓的股票指数比较时必须考虑这一点。

## 基准结果

当前 Notebook 给出的 1993–2018 年样本外结果如下：

| 指标 | 配对策略——净收益 | 配对策略——毛收益 | S&P 500 |
|---|---:|---:|---:|
| 累计收益 | -2.75% | 6.43% | 498.62% |
| 年化复合收益率 | -0.11% | 0.24% | 7.12% |
| 年化波动率 | 1.75% | 1.74% | 16.41% |
| 夏普比率 | -0.05 | 0.15 | 0.50 |
| 最大回撤 | -7.84% | -7.02% | -56.24% |
| 与 S&P 500 的相关系数 | 0.08 | 0.08 | — |
| 市场 beta | 0.01 | 0.01 | — |

2008 年，配对策略收益约为 **+1.6%**，同期 S&P 500 价格指数收益约为 **-41.0%**。这一结果支持策略具有市场中性特征，但不能单独证明它在完整样本期内具有足够的经济盈利能力。

### 交易成本敏感性

| 每单位仓位变化成本 | 年化复合收益率 | 夏普比率 |
|---:|---:|---:|
| 0 个基点 | 0.24% | 0.15 |
| 10 个基点 | -0.11% | -0.05 |
| 20 个基点 | -0.45% | -0.25 |
| 40 个基点 | -1.14% | -0.63 |

扣除成本前的优势为正，但幅度很小。即使并不夸张的交易成本，也足以使策略净收益转为负数。

## 结果解释

该策略成功降低了整体市场暴露，却没有产生有吸引力的风险调整后收益：

- 与市场的相关性和 CAPM beta 都接近零；
- 毛收益中存在微弱的均值回归信号；
- 交易成本完全吸收了这一信号；
- 较小的回撤在一定程度上来自较低的实际敞口和大量空仓时间；
- 形成期的协整关系不能保证交易期一定出现可盈利的收敛。

因此，这是一个“结果为负但仍然有信息价值”的研究：统计关系可以在样本外继续存在，却未必强到足以转化为可交易利润。

## 项目结构

```text
.
├── extract_data.py       # 从源工作簿提取并清理数据
├── *.ipynb               # 配对选择、回测、分析与绘图
├── data_cache/           # 自动生成的 Parquet/CSV 缓存
├── README.md             # 英文说明
└── README.zh-CN.md       # 中文说明
```

自动生成的缓存文件和不可公开的原始数据通常应加入 `.gitignore`，不提交到版本库。

## 开始使用

建议使用 Python 3.10 或更高版本。

```bash
cd FMAproject_PairsTrading

python -m venv .venv
```

在 Windows 中激活虚拟环境：

```powershell
.venv\Scripts\activate
```

安装主要依赖：

```bash
python -m pip install pandas numpy scipy statsmodels matplotlib seaborn jupyter pyarrow openpyxl
```

数据提取脚本会将中间结果保存为 Parquet 文件，因此必须安装 `pyarrow`。

运行数据提取：

```bash
python extract_data.py
```

然后打开分析 Notebook：

```bash
jupyter lab
```

## 可复现性说明

上表记录的是当前基准 Notebook 的输出。在把这些数字视为最终结果之前，应完成以下实现核验并重新运行完整回测：

- 核验行业标签的提取和同行业筛选是否正确；
- 正确计入 seed week 已建立仓位的开仓成本；
- 禁止在价差已经越过止损边界时新开仓；
- 股票消失时在最后一个共同报价日平仓；
- 统一对数收益与普通收益复利的计算口径；
- 报告每周平均活跃配对数量和实际总敞口。

这些检查关系到交易执行和收益计算的精确性，可能改变最终绩效数字，但不会改变本项目的滚动样本外研究框架。

## 局限与扩展方向

当前局限包括：多重检验可能产生伪协整、协整关系可能发生结构性变化、对冲比例固定、交易成本设定较为简化、没有明确计入借券费和卖空限制、忽略股息现金流，以及 benchmark 使用价格指数而非总收益指数。

可以继续探索：

- 对配对检验使用错误发现率校正；
- 按波动率分配组合权重；
- 使用卡尔曼滤波估计时变对冲比例；
- 比较距离法或 Johansen 检验；
- 显式建模现金利息、股息、融资成本和借券费；
- 扩展到欧洲股票或其他交易频率。

## 课程背景

本项目为 **Financial Markets Analytics** 课程项目，主要研究配对交易、协整关系、投资组合构建与样本外策略评估。

## 免责声明

本仓库仅用于学术研究与教学，不构成任何投资建议。历史回测结果不代表真实交易表现。





