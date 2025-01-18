import os
import cv2
import pygame

# 视频标注工具
def video_labeling_tool(video_folder, label_file):
    # 设定标签字典（按方向键进行绑定）
    label_map = {
        pygame.K_UP: 'Label_Up',
        pygame.K_DOWN: 'Label_Down',
        pygame.K_LEFT: 'Label_Left',
        pygame.K_RIGHT: 'Label_Right'
    }
    
    pygame.init()

    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4') or f.endswith('.avi')]
    video_files.sort()  # 按字母顺序排序

    # 打开标签存储文件
    with open(label_file, 'w') as f:
        for video_name in video_files:
            video_path = os.path.join(video_folder, video_name)

            # 打开视频文件
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                print(f"无法打开视频文件 {video_name}")
                continue

            # 获取视频的宽度和高度
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 创建显示窗口，大小根据视频分辨率设置
            screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption('Video Labeling Tool')

            # 显示视频并等待用户输入标签
            label = None
            frame_idx = 0  # 记录当前播放的帧
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 获取视频总帧数
            video_playing = True  # 视频播放状态，默认为播放

            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # 如果视频读取完成，退出

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
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key in label_map:
                            label = label_map[event.key]
                            # 保存标签与视频文件路径
                            f.write(f"{video_name}: {label}\n")
                            print(f"标注 {video_name} 为 {label}")
                            video_playing = False  # 记录标签后暂停播放
                            break  # 跳到下一个视频

                # 如果没有键盘输入，则循环播放
                if video_playing:
                    frame_idx += 1
                    if frame_idx >= total_frames:  # 如果播放完所有帧
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 回到视频的第一帧
                        frame_idx = 0  # 重置帧计数
                else:
                    break  # 记录完标签后跳出循环

            cap.release()

    pygame.quit()
    print("标注完成！")

# 主函数
if __name__ == '__main__':
    # 设置视频文件夹路径和标签保存文件路径
    video_folder = '/home/maliyuan/projects/autolabel'  # 请替换为实际视频文件夹路径
    label_file = '/home/maliyuan/projects/autolabel/label_file.txt'  # 请替换为标签存储文件路径
    
    video_labeling_tool(video_folder, label_file)

