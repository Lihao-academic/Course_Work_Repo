import cv2
import numpy as np
import random  # 🚨 必须引入 random 库




# 使用帧差法的版本：
def decode_video(path, frame_count=16, image_size=160, random_shift=False):
    """
    Decodes a video file into a tensor of motion-differenced frames.
    
    Args:
        path: Path to the AVI file.
        frame_count: Number of frames to extract.
        image_size: Target spatial resolution.
        random_shift: If True, uses temporal jittering (TSN); otherwise uses uniform sampling.
    """
    path = str(path)
    capture = cv2.VideoCapture(path)
    if not capture.isOpened():
        print(f'[ERROR] Failed to open video: {path}')
        return np.zeros((frame_count, image_size, image_size, 3), dtype=np.float32)

    # Decode all frames from the video file
    all_frames = []
    while True:
        ok, frame = capture.read()
        if not ok or frame is None:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (image_size, image_size), interpolation=cv2.INTER_AREA)
        all_frames.append(frame.astype(np.float32) / 255.0)
    capture.release()

    total_frames = len(all_frames)
    if total_frames == 0:
        print(f'[ERROR] No frames decoded from: {path}')
        return np.zeros((frame_count, image_size, image_size, 3), dtype=np.float32)

    # ========================================================
    # 1. Temporal Sampling (TSN vs. Uniform)
    # ========================================================
    if random_shift and total_frames >= frame_count:
        # Training Mode: Segment-based random temporal sampling
        frames = []
        segment_length = total_frames / frame_count
        for i in range(frame_count):
            start_idx = int(i * segment_length)
            end_idx = int((i + 1) * segment_length) - 1
            # 确保不越界
            end_idx = max(start_idx, min(end_idx, total_frames - 1))
            
            # 随机抽取一帧
            random_idx = random.randint(start_idx, end_idx)
            frames.append(all_frames[random_idx])
            
        frames_array = np.stack(frames, axis=0).astype(np.float32)
        
    else:
        # Validation/Test Mode: Strict uniform sampling
        indices = np.linspace(0, total_frames - 1, frame_count).astype(np.int32)
        frames = [all_frames[i] for i in indices]
        frames_array = np.stack(frames, axis=0).astype(np.float32)

    # ========================================================
    # 2. Motion Extraction: Frame Differencing (Physics-based)
    # ========================================================
    # Computes absolute pixel differences between consecutive frames.
    # Static background noise is suppressed (values approach 0), highlighting motion.
    diff_frames = np.abs(frames_array[1:] - frames_array[:-1])

    # Dimensionality preservation: Concatenate the first frame difference 
    # to maintain the original temporal dimension (frame_count).
    final_frames = np.concatenate([diff_frames[0:1], diff_frames], axis=0)

    return final_frames
