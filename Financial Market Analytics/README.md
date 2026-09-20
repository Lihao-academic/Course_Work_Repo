<a id="top"></a>

[中文](#zh) | [English](#en)

<a id="zh"></a>

# 基于 S&P 500 的配对交易研究

本项目使用历史 S&P 500 成分股数据，检验基于协整关系的配对交易策略能否在样本外获得稳定收益。研究采用滚动前推回测：使用过去三年选择配对并估计参数，再在随后六个月中进行样本外交易。

## 项目概览

- **数据范围：** 1990–2018 年，1,355 只历史 S&P 500 成分股
- **形成期：** 156 周
- **交易期：** 26 周
- **配对选择：** Engle–Granger 协整检验
- **交易信号：** 价差 z-score
- **组合构建：** 每期最多 20 组配对，等额配置
- **交易成本：** 每次仓位变化 10 bps

## 项目结构

```
aaa
```

## 策略方法

对两只股票的对数价格建立协整回归：

$$
\log P_{Y,t}=\alpha+\beta\log P_{X,t}+\varepsilon_t
$$

将平稳残差作为价差，并根据 z-score 交易：

| 条件 | 操作 |
|---|---|
| $z\leq-2$ | 做多价差 |
| $z\geq2$ | 做空价差 |
| 价差回到退出区间 | 平仓 |
| $\lvert z\rvert\geq3$ | 止损 |

本周收盘产生的信号从下一周开始计算收益，以避免前视偏差。

## 基准结果

| 指标 | 配对策略（净） | 配对策略（毛） | S&P 500 |
|---|---:|---:|---:|
| 年化收益率 | -0.11% | 0.24% | 7.12% |
| 年化波动率 | 1.75% | 1.74% | 16.41% |
| 夏普比率 | -0.05 | 0.15 | 0.50 |
| 最大回撤 | -7.84% | -7.02% | -56.24% |
| 市场 beta | 0.01 | 0.01 | — |

策略与市场的相关性很低，并在扣除成本前表现出微弱的均值回归收益；但 10 bps 的交易成本已经足以消除这一优势。因此，当前策略更接近低相关性的分散化工具，而不是能够独立产生稳定收益的策略。

## 运行项目

```bash
python -m pip install pandas numpy scipy statsmodels matplotlib seaborn jupyter pyarrow openpyxl
python extract_data.py
jupyter lab
```

原始课程数据未包含在仓库中。运行前需将源 Excel 文件放到 `extract_data.py` 所配置的位置。`pyarrow` 用于读写 Parquet 缓存文件。

> **说明：**以上为当前基准结果。行业标签提取、交易成本计算和退市处理仍需进一步核验，最终数值可能在完整复跑后更新。

[返回顶部](#top) · [Read in English](#en)

---

<a id="en"></a>

# Pairs Trading on the S&P 500

This project tests whether a cointegration-based pairs-trading strategy can generate stable out-of-sample returns using historical S&P 500 constituents. It follows a walk-forward design: pairs and parameters are estimated from the previous three years and traded during the following six months.

## Project overview

- **Data:** 1,355 historical S&P 500 constituents, 1990–2018
- **Formation period:** 156 weeks
- **Trading period:** 26 weeks
- **Pair selection:** Engle–Granger cointegration test
- **Trading signal:** spread z-score
- **Portfolio:** up to 20 equally weighted pairs per window
- **Transaction cost:** 10 bps per position change

## Project Structure

```
aaa
```

## Method

For each candidate pair, log prices are modelled as:

$$
\log P_{Y,t}=\alpha+\beta\log P_{X,t}+\varepsilon_t
$$

The stationary residual is treated as the spread and traded using its z-score:

| Condition | Action |
|---|---|
| $z\leq-2$ | Long the spread |
| $z\geq2$ | Short the spread |
| Spread returns to the exit band | Close the position |
| $\lvert z\rvert\geq3$ | Stop loss |

Signals observed at the current weekly close affect the following week's return, preventing look-ahead bias.

## Baseline results

| Metric | Pairs (net) | Pairs (gross) | S&P 500 |
|---|---:|---:|---:|
| CAGR | -0.11% | 0.24% | 7.12% |
| Annualized volatility | 1.75% | 1.74% | 16.41% |
| Sharpe ratio | -0.05 | 0.15 | 0.50 |
| Maximum drawdown | -7.84% | -7.02% | -56.24% |
| Market beta | 0.01 | 0.01 | — |

The strategy has very low market exposure and a small gross mean-reversion edge. However, a 10 bps trading cost is enough to eliminate that edge. In its current form, the strategy behaves more like a low-correlation diversifier than a profitable stand-alone strategy.

## Run the project

```bash
python -m pip install pandas numpy scipy statsmodels matplotlib seaborn jupyter pyarrow openpyxl
python extract_data.py
jupyter lab
```

The original course dataset is not included. Before running the project, place the source Excel workbook in the location configured in `extract_data.py`. The `pyarrow` package is required for the Parquet cache files.

> **Note:** These are current baseline results. Sector-label extraction, transaction-cost accounting, and delisting handling still require validation, so the final numbers may change after a complete rerun.

[Back to top](#top) · [阅读中文版](#zh)

## Disclaimer

This project is for academic and educational purposes only and does not constitute investment advice.
