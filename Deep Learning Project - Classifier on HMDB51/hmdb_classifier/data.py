import csv
import random
from collections import defaultdict
from pathlib import Path

import numpy as np
import tensorflow as tf

from .video_io import decode_video


def read_class_names(classes_path):
    with Path(classes_path).open('r', encoding='utf-8') as fh:
        return [line.strip() for line in fh if line.strip()]


def read_manifest(manifest_path, limit_per_class=None, seed=42):
    with Path(manifest_path).open('r', encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
    records = [{'path': r['path'], 'label': int(r['label']),
                'class_name': r['class_name'], 'subset': r['subset']} for r in rows]
    if not limit_per_class or limit_per_class <= 0:
        return records
    rng = random.Random(seed)
    by_class = defaultdict(list)
    for r in records:
        by_class[r['class_name']].append(r)
    limited = []
    for cls in sorted(by_class):
        items = list(by_class[cls])
        rng.shuffle(items)
        limited.extend(items[:limit_per_class])
    rng.shuffle(limited)
    return limited



def _augment_video(video, label):
    """
    Applies spatial and color augmentations to the video tensor.
    Input shape: (frames, height, width, channels)
    """
    # 1. Random horizontal flip
    if tf.random.uniform(()) < 0.5:
        video = tf.reverse(video, axis=[2])

    # 2. Random spatial crop (scale up by 15%, then crop to original size to break background bias)
    original_size = tf.shape(video)[1]
    larger_size = tf.cast(tf.cast(original_size, tf.float32) * 1.15, tf.int32)

    video_zoomed = tf.image.resize(video, [larger_size, larger_size])
    frames = tf.shape(video)[0]
    channels = tf.shape(video)[3]
    video = tf.image.random_crop(video_zoomed, size=[frames, original_size, original_size, channels])

    # 3. Color jittering (brightness and contrast)
    video = tf.image.random_brightness(video, max_delta=0.08)
    video = tf.image.random_contrast(video, lower=0.9, upper=1.1)

    return tf.clip_by_value(video, 0.0, 1.0), label


def make_dataset(manifest_path, frame_count, image_size, batch_size,
                 training, seed=42, limit_per_class=None, cache=False):
    records = read_manifest(manifest_path, limit_per_class=limit_per_class, seed=seed)
    if not records:
        raise ValueError(f'No records found in {manifest_path}')

    paths = [r['path'] for r in records]
    labels = np.array([r['label'] for r in records], dtype=np.int32)
    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))
    if training:
        dataset = dataset.shuffle(len(records), seed=seed, reshuffle_each_iteration=True)


    def load(path_tensor, label):
        def decode_np(path_bytes):
            if isinstance(path_bytes, np.ndarray):
                path_bytes = path_bytes.item()
            if isinstance(path_bytes, bytes):
                path_bytes = path_bytes.decode('utf-8')

            # Enable random temporal shift (TSN) only during training
            return decode_video(path_bytes, frame_count=frame_count, image_size=image_size, random_shift=training)

        video = tf.numpy_function(decode_np, [path_tensor], tf.float32)
        video.set_shape((frame_count, image_size, image_size, 3))
        label.set_shape(())
        return video, label

    dataset = dataset.map(load, num_parallel_calls=tf.data.AUTOTUNE)

    # Conditional Caching: Cache validation/test sets to speed up I/O.
    # Do NOT cache the training set to preserve dynamic temporal/spatial augmentations.
    if cache:
        if training:
            pass
        else:
            dataset = dataset.cache('/content/val_cache')

    if training:
        dataset = dataset.map(_augment_video, num_parallel_calls=tf.data.AUTOTUNE)
    return dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE), len(records)
