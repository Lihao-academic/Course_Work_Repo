# english

[中文](#中文) | [English](#english)

===============================

Action Recognition on HMDB51

===============================

Author: Lihao [mat. 947013] l.hao1@campus.unimib.it
Author: Shen Hao Stefano Lin [ MAT. 881525 ] s.lin2@campus.unimib.it
Project: Action Recognition on HMDB51
Dataset: HMDB51

## 📌 Project Overview
This repository contains a robust video action recognition pipeline. It leverages a Two-Stage Fine-Tuning strategy, combining spatial feature extraction (MobileNetV2) with temporal sequence modeling (Bidirectional GRU), enhanced by Frame Differencing to suppress static background noise.

## 📂 Directory Structure & Deliverables

The project strictly follows a code-data separation paradigm:


├── hmdb_classifier/           # 🧠 Core Source Code & Entry Point
│   ├── HMDB51_Main_Experiment.ipynb  # Main Execution Notebook (Run this!)
│   ├── data.py                # tf.data pipeline (TSN sampling & augmentations)
│   ├── models.py              # Neural network architectures
│   ├── video_io.py            # Video decoding & Frame differencing physics
│   ├── prepare_dataset.py     # Manifest generation and data splitting
│   └── metrics.py             # Evaluation and learning curve plotting
│
├── best_model.keras           # 🏆 The final optimized weights (66%+ Accuracy)
├── current stage1 results/    # Pre-trained Stage-1 backbone weights
├── outputs/                   # Directory for training logs and checkpoints
├── requirements.txt           # Python dependencies
└── README.txt                 # Project documentation (This file)

## 📊 Dataset Setup (Action Required)
To ensure portability, the massive dataset files are not included in this archive. 
Before running the code, please configure the data directories at the root level:

1. Download the HMDB51 dataset and the official splits.
2. Place them in the root directory exactly with these names:
   - `hmdb51_org/`          (Contains the 51 action class folders)
   - `test_train_splits/`   (Contains the official .txt split files)

## 🚀 How to Run
1. Install the required environment:
   $ pip install -r requirements.txt

2. Open `hmdb_classifier/HMDB51_Main_Experiment.ipynb` in Jupyter Notebook or Google Colab.
3. The notebook is fully configured for dynamic path resolution. Assuming the dataset folders are placed correctly, simply execute "Run All" to reproduce the data pipeline, instantiate the model, load the `best_model.keras` weights, and generate the final Confusion Matrix on the hold-out test set.
4. Due to filesize limitation, the .keras file is shared via google drive: https://drive.google.com/file/d/1Qls1vGWrUSUJfg6pULTvnOg1lh-rabUX/view?usp=drive_link


# 中文

[中文](#中文) | [English](#english)

===============================

基于HMDB51的动作识别

===============================

作者：Lihao [学号 947013] l.hao1@campus.unimib.it
作者：Shen Hao Stefano Lin [学号 881525] s.lin2@campus.unimib.it
项目：HMDB51 动作识别
数据集：HMDB51

## 📌 项目概述
本仓库包含一个稳健的视频动作识别流程。该流程采用“两阶段微调”（Two-Stage Fine-Tuning）策略，结合了空间特征提取（MobileNetV2）与时间序列建模（双向 GRU），并利用帧差法（Frame Differencing）抑制静态背景噪声。

## 📂 目录结构与交付物

本项目严格遵循代码与数据分离的原则：


├── hmdb_classifier/           # 🧠 核心源代码与入口
│   ├── HMDB51_Main_Experiment.ipynb  # 主执行 Notebook（请运行此文件！）
│   ├── data.py                # tf.data 数据流水线（TSN 采样与数据增强）
│   ├── models.py              # 神经网络架构
│   ├── video_io.py            # 视频解码与帧差法处理逻辑
│   ├── prepare_dataset.py     # 清单生成与数据集划分
│   └── metrics.py             # 评估指标与学习曲线绘制
│
├── best_model.keras           # 🏆 最终优化后的权重（准确率 >66%）
├── current stage1 results/    # 第一阶段预训练的主干网络权重
├── outputs/                   # 训练日志与检查点（checkpoint）存储目录
├── requirements.txt           # Python 依赖项
└── README.txt                 # 项目文档（即本文件）

## 📊 数据集设置（需手动操作）
为确保可移植性，本压缩包未包含庞大的数据集文件。
在运行代码之前，请在根目录下配置数据路径：

1. 下载 HMDB51 数据集及官方划分文件（splits）。 2. 将它们按以下确切名称放置在根目录下：
- `hmdb51_org/`          (包含 51 个动作类别文件夹)
- `test_train_splits/`   (包含官方的 .txt 划分文件)

## 🚀 如何运行
1. 安装所需环境：
$ pip install -r requirements.txt

2. 在 Jupyter Notebook 或 Google Colab 中打开 `hmdb_classifier/HMDB51_Main_Experiment.ipynb`。
3. 该 Notebook 已配置好动态路径解析功能。只要数据集文件夹放置正确，只需执行“全部运行”（Run All）即可复现数据流水线、实例化模型、加载 `best_model.keras` 权重，并在留出的测试集上生成最终的混淆矩阵。
4. 由于文件大小限制，`.keras` 文件通过 Google Drive 分享：https://drive.google.com/file/d/1Qls1vGWrUSUJfg6pULTvnOg1lh-rabUX/view?usp=drive_link

