====================================================================
Action Recognition on HMDB51
====================================================================

Author: Lihao [mat. 947013] l.hao1@campus.unimib.it
Author: Shen Hao Stefano Lin [ MAT. 881525 ] s.lin2@campus.unimib.it
Project: Action Recognition on HMDB51
Dataset: HMDB51

## 📌 Project Overview
This repository contains a robust video action recognition pipeline. It leverages a Two-Stage Fine-Tuning strategy, combining spatial feature extraction (MobileNetV2) with temporal sequence modeling (Bidirectional GRU), enhanced by Frame Differencing to suppress static background noise.

## 📂 Directory Structure & Deliverables

The project strictly follows a code-data separation paradigm:

.
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
