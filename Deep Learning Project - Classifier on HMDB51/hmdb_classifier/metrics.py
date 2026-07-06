import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf


def evaluate_to_dir(model, dataset, class_names, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    y_true, y_pred = [], []
    for videos, labels in dataset:
        probs = model.predict(videos, verbose=0)
        y_true.append(labels.numpy())
        y_pred.append(np.argmax(probs, axis=1))
    y_true = np.concatenate(y_true)
    y_pred = np.concatenate(y_pred)

    matrix = tf.math.confusion_matrix(y_true, y_pred, num_classes=len(class_names)).numpy()

    rows, f1s, precs, recs = [], [], [], []
    for i, cls in enumerate(class_names):
        tp = float(matrix[i, i])
        fp = float(matrix[:, i].sum() - tp)
        fn = float(matrix[i, :].sum() - tp)
        support = int(matrix[i, :].sum())
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) else 0.0
        precs.append(p)
        recs.append(r)
        f1s.append(f1)
        rows.append({'class_name': cls, 'precision': p, 'recall': r, 'f1': f1, 'support': support})

    metrics = {
        'accuracy': float(np.mean(y_true == y_pred)),
        'macro_precision': float(np.mean(precs)),
        'macro_recall': float(np.mean(recs)),
        'macro_f1': float(np.mean(f1s)),
        'support': float(len(y_true)),
    }

    with (output_dir / 'metrics.json').open('w', encoding='utf-8') as fh:
        json.dump(metrics, fh, indent=2)

    with (output_dir / 'classification_report.csv').open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=['class_name', 'precision', 'recall', 'f1', 'support'])
        writer.writeheader()
        writer.writerows(rows)

    np.save(output_dir / 'confusion_matrix.npy', matrix)

    # Plot normalised confusion matrix
    vals = matrix.astype(np.float32)
    row_sums = vals.sum(axis=1, keepdims=True)
    vals = np.divide(vals, row_sums, out=np.zeros_like(vals), where=row_sums != 0)
    fig, ax = plt.subplots(figsize=(16, 14))
    im = ax.imshow(vals, interpolation='nearest', cmap='Blues')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title('HMDB51 confusion matrix')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_yticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, rotation=90, fontsize=7)
    ax.set_yticklabels(class_names, fontsize=7)
    fig.tight_layout()
    fig.savefig(output_dir / 'confusion_matrix.png', dpi=180)
    plt.close(fig)

    return metrics


def plot_training_history(csv_path, output_path=None):
    csv_path = Path(csv_path)
    epochs, losses, val_losses, accs, val_accs = [], [], [], [], []
    with csv_path.open('r', encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh):
            epochs.append(int(row['epoch']))
            losses.append(float(row['loss']))
            val_losses.append(float(row.get('val_loss', row['loss'])))
            accs.append(float(row.get('accuracy', 0)))
            val_accs.append(float(row.get('val_accuracy', 0)))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(epochs, losses, label='loss')
    axes[0].plot(epochs, val_losses, label='val_loss')
    axes[0].set_title('Loss')
    axes[0].grid(alpha=0.25)
    axes[0].legend()
    axes[1].plot(epochs, accs, label='accuracy')
    axes[1].plot(epochs, val_accs, label='val_accuracy')
    axes[1].set_title('Accuracy')
    axes[1].grid(alpha=0.25)
    axes[1].legend()
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(output_path, dpi=160)
    plt.show()
