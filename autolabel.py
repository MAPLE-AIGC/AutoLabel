import os
import argparse
import pygame
import cv2
from tqdm import tqdm

# 视频标注工具
def video_labeling_tool(video_folder, label_path, label_filename, video_size):
    # 设定标签字典（按方向键进行绑定）
    label_map = {
        # pygame.K_UP: 'Label_Up',
        # pygame.K_DOWN: 'Label_Down',
        pygame.K_LEFT: 1, # good case
        pygame.K_RIGHT: 0, # badcase
    }

    pygame.init()

    # 如果 label_filename 为 None，则使用 video_folder 的名称作为文件名
    if label_filename is not None:
        full_label_filename = os.path.basename(video_folder) + f'_{label_filename}.txt'
    else:
        full_label_filename = os.path.basename(video_folder) + '_label.txt'

    # 创建标签文件存储路径
    label_file = os.path.join(label_path, full_label_filename)

    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4') or f.endswith('.avi')]
    video_files.sort()  # 按字母顺序排序

    # 打开标签存储文件
    with open(label_file, 'w') as f:
        for video_name in tqdm(video_files, desc=f"Processing video", unit="video"):
            video_path = os.path.join(video_folder, video_name)

            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"无法打开视频文件 {video_name}")
                continue

            # 获取视频的总帧数
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 如果传入了指定的视频大小，修改分辨率
            if video_size:
                target_width, target_height = video_size
            else:
                target_width, target_height = width, height

            # 创建显示窗口，大小根据视频分辨率设置
            screen = pygame.display.set_mode((target_width, target_height))
            pygame.display.set_caption('Video Labeling Tool')

            # 显示视频并等待用户输入标签
            label = None
            frame_idx = 0  # 记录当前播放的帧
            video_playing = True  # 视频播放状态，默认为播放

            while True:
                if frame_idx >= total_frames:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 如果视频读取完毕，跳回到第一帧
                    frame_idx = 0

                ret, frame = cap.read()
                if not ret:
                    print(f"无法读取视频帧 {frame_idx}，跳过该视频")
                    break
                
                 # 如果需要调整帧大小
                if (width != target_width) or (height != target_height):
                    frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)

                # 转换为RGB格式，便于pygame显示
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # 旋转帧，纠正方向（逆时针旋转 90 度）
                frame_rgb = cv2.rotate(frame_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)

                # 将视频帧显示到pygame窗口
                frame_surface = pygame.surfarray.make_surface(frame_rgb)
                screen.blit(frame_surface, (0, 0))
                pygame.display.update()

                # 监听用户输入
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print(f'用户退出，标注进度已保存到 {label_file}')
                        cap.release()
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key in label_map:
                            label = label_map[event.key]
                            # 保存标签与视频文件路径
                            f.write(f"{os.path.join(video_folder, video_name)}: {label}\n")
                            print(f"标注 {video_name} 为 {label}")
                            video_playing = False  # 记录标签后暂停播放
                            break  # 跳到下一个视频

                # 如果没有键盘输入，则循环播放
                if video_playing:
                    frame_idx += 1
                else:
                    break  # 记录完标签后跳出循环

            cap.release()

    pygame.quit()
    print("标注完成！")

# 主函数
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="视频标注工具")
    parser.add_argument('--video_folder', type=str, required=True, help="视频文件夹路径")
    parser.add_argument('--label_path', type=str, required=True, help="标签存储路径")
    parser.add_argument('--label_filename', type=str, default=None, help="标签存储文件名 (默认为 None, 使用文件夹名)")
    parser.add_argument('--video_size', type=int, nargs=2, default=None, help="视频大小, 格式: 宽 高 (可选)")

    args = parser.parse_args()

    print(f'Video label notes: Left means good case, Right means bad case')
    video_labeling_tool(args.video_folder, args.label_path, args.label_filename, args.video_size)
