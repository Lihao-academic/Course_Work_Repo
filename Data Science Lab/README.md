# Traditional and Digital Financial Literacy in Italy  
# 意大利传统与数字金融素养研究

This repository contains the reproducible analysis for a Data Science Lab project based on the **2023 IACOFI Survey of Adult Financial Literacy and Financial Competence in Italy**, published by **Banca d'Italia**.

本项目为 Data Science Lab 课程项目，使用 **Banca d'Italia 发布的 2023 IACOFI 意大利成年人金融素养调查**，研究传统金融素养与数字金融素养之间的关系及其不匹配现象。

---

## 1. Research Question / 研究问题

**English**

> To what extent do traditional and digital financial literacy overlap among Italian adults, and what patterns do mismatches between the two display in demographic characteristics, digital financial participation, and adverse financial experiences?

The analysis is descriptive and associational rather than causal.

**中文**

> 意大利成年人的传统金融素养与数字金融素养在多大程度上相互重合？当两者不一致时，这种差异在人口特征、数字金融参与和负面金融经历方面表现出怎样的模式？

本研究以描述性和关联性分析为主，不进行因果推断。

---

## 2. Dataset / 数据集

- Source / 来源: **Banca d'Italia, IACOFI 2023**
- Respondents / 受访者: **4,862**
- Variables / 变量数: **219**
- Survey weight / 调查权重: `wght`
- Main Traditional–Digital comparison sample / 主要传统—数字比较样本: **4,427 respondents with internet access**

Expected data path / 数据路径：

```text
data/raw/stata/Database_ENG.dta
```

---

## 3. Project Structure / 项目结构

```text
DSLAB/
├── data/
│   └── raw/
│       └── stata/
│           └── Database_ENG.dta
├── output/
│   ├── figures/
│   │   ├── demographic_scores.png
│   │   ├── digital_activity_and_risk.png
│   │   ├── literacy_profiles.png
│   │   ├── profiles_by_age_education.png
│   │   └── traditional_vs_digital.png
│   └── tables/
│       ├── adverse_experience_by_profile.csv
│       ├── age_profiles.csv
│       ├── demographic_scores.csv
│       ├── digital_activity_by_profile.csv
│       ├── education_profiles.csv
│       ├── literacy_profiles.csv
│       └── score_validation.csv
├── exploration.ipynb
└── README.md
```

`.venv/` and `.idea/` are local development folders and are not required for reproduction.

`.venv/` 和 `.idea/` 属于本地开发环境，不属于复现实验所需文件。

---

## 4. Analytical Workflow / 分析流程

```text
Raw questionnaire data
        ↓
Reconstruct Traditional Financial Literacy
        ↓
Reconstruct Digital Financial Literacy
        ↓
Validate against official Banca d'Italia statistics
        ↓
Compare Traditional and Digital literacy
        ↓
Construct four literacy profiles
        ↓
Demographic analysis
        ↓
Digital financial activity
        ↓
Adverse financial experiences
```

Main steps / 主要步骤：

1. Reconstruct the official Traditional Financial Literacy score (0–20).  
   重建官方传统金融素养指标（0–20）。

2. Reconstruct the Digital Financial Literacy score (0–10).  
   重建数字金融素养指标（0–10）。

3. Compare survey-weighted means with official published values.  
   使用调查权重计算均值，并与官方公布结果核对。

4. Compare the two scores using Spearman correlation.  
   使用 Spearman 相关分析两类金融素养之间的关系。

5. Divide respondents into four profiles using the 70% target:  
   根据 70% 目标线划分四类人群：
   - Both meet target
   - Traditional only
   - Digital only
   - Neither meets target

6. Compare scores and profiles across demographic groups.  
   比较不同性别、年龄、教育程度和地区群体。

7. Compare digital activity and adverse experiences across literacy profiles.  
   比较不同金融素养画像的数字金融活动和负面金融经历。

---

## 5. Reproducibility / 复现方法

All analysis is contained in:

```text
exploration.ipynb
```

To reproduce the project / 复现步骤：

1. Place the dataset at / 将数据放入：

```text
data/raw/stata/Database_ENG.dta
```

2. Install the required packages / 安装依赖：

```bash
pip install pandas numpy scipy matplotlib seaborn jupyter
```

3. Open `exploration.ipynb`.

4. Run all cells from top to bottom / 从上到下运行全部单元格。

5. Figures and tables will be generated automatically in `output/`.  
   图表和 CSV 结果会自动生成到 `output/` 目录。

The analysis was developed using **Python 3.11**.

本项目使用 **Python 3.11** 完成。

---

## 6. Main Outputs / 主要输出

Figures / 图像：

- `traditional_vs_digital.png`
- `literacy_profiles.png`
- `demographic_scores.png`
- `profiles_by_age_education.png`
- `digital_activity_and_risk.png`

Tables / 表格：

- `score_validation.csv`
- `literacy_profiles.csv`
- `demographic_scores.csv`
- `age_profiles.csv`
- `education_profiles.csv`
- `digital_activity_by_profile.csv`
- `adverse_experience_by_profile.csv`

---

## 7. References / 参考来源

1. Banca d'Italia (2023), *Surveys on Financial Literacy and Digital Financial Skills in Italy: Adults – 2023*.
2. Banca d'Italia (2023), *Data Description 2023*.
3. OECD (2022), *OECD/INFE Toolkit for Measuring Financial Literacy and Financial Inclusion 2022*.
4. OECD (2023), *OECD/INFE 2023 International Survey of Adult Financial Literacy*.

---

## 8. Authors / 作者

- **Li Hao** — MAT. 947013
- **Shen Hao Stefano Lin** — MAT. 881525
