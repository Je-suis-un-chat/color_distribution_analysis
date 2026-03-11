import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def calculate_video_histogram(video_dir, num_frames=50):
    """
    遍历指定目录下的视频，截取前 num_frames 帧，累加计算 RGB 色彩直方图。
    """
    hist_b_total = np.zeros((256, 1), dtype=np.float64)
    hist_g_total = np.zeros((256, 1), dtype=np.float64)
    hist_r_total = np.zeros((256, 1), dtype=np.float64)
    
    video_paths = []
    for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv']:
        video_paths.extend(list(Path(video_dir).rglob(ext)))
        
    print(f"在 '{video_dir}' 中找到 {len(video_paths)} 个视频，开始处理...")
    
    total_frames_processed = 0
    
    for path in video_paths:
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            continue
            
        frame_count = 0
        while frame_count < num_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
            
            hist_b_total += hist_b
            hist_g_total += hist_g
            hist_r_total += hist_r
            
            frame_count += 1
            total_frames_processed += 1
            
        cap.release()
        
    print(f"'{video_dir}' 处理完成！共累计统计了 {total_frames_processed} 帧。")
    return hist_b_total, hist_g_total, hist_r_total

def plot_four_comparisons(real_dir, fake_dir, num_frames=50):
    """
    生成 2x2 的图表阵列，全部使用常规线性坐标：
    Row 1: 剔除 0 和 255 (重点看中间细节)
    Row 2: 完整保留 0-255 (直接展示尖峰对中间色调的物理级压缩)
    """
    r_hist_b, r_hist_g, r_hist_r = calculate_video_histogram(real_dir, num_frames)
    f_hist_b, f_hist_g, f_hist_r = calculate_video_histogram(fake_dir, num_frames)
    
    scale_factor = 1e7
    
    # --- 数据准备 ---
    # 完整数据 (0-255)
    r_full_b = r_hist_b / scale_factor
    r_full_g = r_hist_g / scale_factor
    r_full_r = r_hist_r / scale_factor
    
    f_full_b = f_hist_b / scale_factor
    f_full_g = f_hist_g / scale_factor
    f_full_r = f_hist_r / scale_factor

    # 截断数据 (1-254)
    r_mid_b = r_full_b[1:255]
    r_mid_g = r_full_g[1:255]
    r_mid_r = r_full_r[1:255]
    
    f_mid_b = f_full_b[1:255]
    f_mid_g = f_full_g[1:255]
    f_mid_r = f_full_r[1:255]

    # --- 开始绘图 ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    x_axis_mid = np.arange(1, 255)
    x_axis_full = np.arange(0, 256)

    # ------------------ 第一排：剔除极值 (1-254) ------------------
    max_y_mid = max(np.max(r_mid_b), np.max(r_mid_g), np.max(r_mid_r),
                    np.max(f_mid_b), np.max(f_mid_g), np.max(f_mid_r))
    ylim_mid = max_y_mid * 1.1

    # [0, 0] 真实视频 (1-254)
    axes[0, 0].plot(x_axis_mid, r_mid_r, color='red', linewidth=1)
    axes[0, 0].plot(x_axis_mid, r_mid_g, color='green', linewidth=1)
    axes[0, 0].plot(x_axis_mid, r_mid_b, color='blue', linewidth=1)
    axes[0, 0].set_title('Real Video (Mid-tones 1-254)')
    axes[0, 0].set_ylabel('Frequency (10^7)')
    axes[0, 0].set_xlim([1, 254])
    axes[0, 0].set_ylim([0, ylim_mid])

    # [0, 1] 合成视频 (1-254)
    axes[0, 1].plot(x_axis_mid, f_mid_r, color='red', linewidth=1)
    axes[0, 1].plot(x_axis_mid, f_mid_g, color='green', linewidth=1)
    axes[0, 1].plot(x_axis_mid, f_mid_b, color='blue', linewidth=1)
    axes[0, 1].set_title('Synthetic Video (Mid-tones 1-254)')
    axes[0, 1].set_xlim([1, 254])
    axes[0, 1].set_ylim([0, ylim_mid])


    # ------------------ 第二排：保留极值 (0-255) 线性坐标 ------------------
    max_y_full = max(np.max(r_full_b), np.max(r_full_g), np.max(r_full_r),
                     np.max(f_full_b), np.max(f_full_g), np.max(f_full_r))
    ylim_full = max_y_full * 1.1

    # [1, 0] 真实视频 (0-255)
    axes[1, 0].plot(x_axis_full, r_full_r, color='red', linewidth=1, label='Red')
    axes[1, 0].plot(x_axis_full, r_full_g, color='green', linewidth=1, label='Green')
    axes[1, 0].plot(x_axis_full, r_full_b, color='blue', linewidth=1, label='Blue')
    axes[1, 0].set_title('Real Video (Full 0-255)')
    axes[1, 0].set_xlabel('Pixel values (0-255)')
    axes[1, 0].set_ylabel('Frequency (10^7)')
    axes[1, 0].set_xlim([0, 255])
    axes[1, 0].set_ylim([0, ylim_full])
    axes[1, 0].legend(loc='upper right', fontsize='small')

    # [1, 1] 合成视频 (0-255)
    axes[1, 1].plot(x_axis_full, f_full_r, color='red', linewidth=1, label='Red')
    axes[1, 1].plot(x_axis_full, f_full_g, color='green', linewidth=1, label='Green')
    axes[1, 1].plot(x_axis_full, f_full_b, color='blue', linewidth=1, label='Blue')
    axes[1, 1].set_title('Synthetic Video (Full 0-255)')
    axes[1, 1].set_xlabel('Pixel values (0-255)')
    axes[1, 1].set_xlim([0, 255])
    axes[1, 1].set_ylim([0, ylim_full])
    axes[1, 1].legend(loc='upper right', fontsize='small')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    REAL_VIDEO_DIR = "./real_video"
    FAKE_VIDEO_DIR = "./fake_video"
    FRAMES_PER_VIDEO = 100
    
    plot_four_comparisons(REAL_VIDEO_DIR, FAKE_VIDEO_DIR, num_frames=FRAMES_PER_VIDEO)