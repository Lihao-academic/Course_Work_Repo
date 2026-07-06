import tensorflow as tf


def _weights_value(weights):
    if weights is None:
        return None
    val = str(weights).strip().lower()
    return None if val in {'', 'none', 'null', 'false'} else val


def _build_conv3d(num_classes, frame_count, image_size, dropout):
    """Legacy 3D Convolutional Architecture (Baseline)"""
    inputs = tf.keras.Input(shape=(frame_count, image_size, image_size, 3), name='video')

    x = tf.keras.layers.Conv3D(32, (3, 5, 5), padding='same', use_bias=False, name='stem_conv')(inputs)
    x = tf.keras.layers.BatchNormalization(name='stem_bn')(x)
    x = tf.keras.layers.Activation('relu', name='stem_relu')(x)
    x = tf.keras.layers.MaxPool3D(pool_size=(1, 2, 2), name='stem_pool')(x)

    for i, filters in enumerate([64, 96, 128], start=1):
        n = f'block{i}'
        x = tf.keras.layers.Conv3D(filters, 3, padding='same', use_bias=False, name=f'{n}_conv1')(x)
        x = tf.keras.layers.BatchNormalization(name=f'{n}_bn1')(x)
        x = tf.keras.layers.Activation('relu', name=f'{n}_relu1')(x)
        x = tf.keras.layers.Conv3D(filters, 3, padding='same', use_bias=False, name=f'{n}_conv2')(x)
        x = tf.keras.layers.BatchNormalization(name=f'{n}_bn2')(x)
        x = tf.keras.layers.Activation('relu', name=f'{n}_relu2')(x)
        x = tf.keras.layers.MaxPool3D(pool_size=(2, 2, 2), name=f'{n}_pool')(x)

    x = tf.keras.layers.GlobalAveragePooling3D(name='global_pool')(x)
    x = tf.keras.layers.Dropout(dropout, name='dropout')(x)
    x = tf.keras.layers.Dense(256, activation='relu', name='dense_features')(x)
    x = tf.keras.layers.Dropout(dropout, name='classifier_dropout')(x)
    outputs = tf.keras.layers.Dense(num_classes, activation='softmax', name='class_probs')(x)
    return tf.keras.Model(inputs, outputs, name='conv3d')


# 这是使用了局部解冻的特殊版本
def _build_mobilenet(num_classes, frame_count, image_size, temporal_head, weights, backbone_trainable, dropout):
    """Two-Stream Architecture: MobileNetV2 (Spatial) + GRU/Avg (Temporal)"""
    inputs = tf.keras.Input(shape=(frame_count, image_size, image_size, 3), name='video')

    x = tf.keras.layers.Rescaling(scale=2.0, offset=-1.0, name='mobilenet_preprocess')(inputs)

    wanted = _weights_value(weights)
    try:
        backbone = tf.keras.applications.MobileNetV2(
            input_shape=(image_size, image_size, 3), include_top=False,
            weights=wanted, pooling='avg',
        )
        if wanted == 'imagenet':
            print('[INFO] MobileNetV2: ImageNet weights loaded successfully.')
    except Exception as exc:
        if wanted == 'imagenet':
            raise RuntimeError(
                '[ERROR] Failed to download MobileNetV2 ImageNet weights. '
                'The model will not converge efficiently without pre-training. '
                'Check network connection or set WEIGHTS="none" to train from scratch.'
            ) from exc
        backbone = tf.keras.applications.MobileNetV2(
            input_shape=(image_size, image_size, 3), include_top=False,
            weights=None, pooling='avg',
        )

    # ========================================================
    # Partial Unfreezing Strategy (Stage-2 Fine-Tuning)
    # ========================================================
    if backbone_trainable:
        backbone.trainable = True
        # MobileNetV2 has ~154 layers. Freeze the first 110 (low/mid-level features), 
        # and unfreeze the top layers (high-level semantics) for task-specific adaptation.
        freeze_limit = 110
        for layer in backbone.layers[:freeze_limit]:
            layer.trainable = False
        print(f"[TACTICS] 局部解冻开启：前 {freeze_limit} 层已锁死，仅微调高层神经元！")
    else:
        backbone.trainable = False

    # Apply spatial feature extraction across the temporal dimension
    x = tf.keras.layers.TimeDistributed(backbone, name='frame_encoder')(x)
    x = tf.keras.layers.LayerNormalization(name='temporal_norm')(x)

    # ========================================================
    # Temporal Modeling Head
    # ========================================================

    if temporal_head == 'gru':
        x = tf.keras.layers.Bidirectional(
            tf.keras.layers.GRU(
                128,
                dropout=dropout
            ), name='bidirectional_gru')(x)
    else:
        x = tf.keras.layers.GlobalAveragePooling1D(name='temporal_average')(x)

    # Classification Bottleneck
    x = tf.keras.layers.Dropout(dropout)(x)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.Dropout(dropout)(x)

    outputs = tf.keras.layers.Dense(num_classes, activation='softmax', name='class_probs')(x)
    return tf.keras.Model(inputs, outputs, name=f'mobilenet_{temporal_head}')

def build_model(model_name, num_classes, frame_count, image_size,
                weights='imagenet', backbone_trainable=False, dropout=0.35):
    """Factory function to build the requested neural architecture."""
    if model_name == 'conv3d':
        return _build_conv3d(num_classes, frame_count, image_size, dropout)
    if model_name in ('mobilenet_gru', 'mobilenet_avg'):
        head = 'gru' if model_name == 'mobilenet_gru' else 'avg'
        return _build_mobilenet(num_classes, frame_count, image_size, head, weights, backbone_trainable, dropout)
    raise ValueError(f'[ERROR] Unknown model architecture requested: {model_name}')
