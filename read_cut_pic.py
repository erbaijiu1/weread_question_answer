import os
from PIL import Image

directory = "weread_pic/free_day/"  # 目录路径

# 遍历目录下的文件
for filename in os.listdir(directory):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        # 拼接文件的完整路径
        filepath = os.path.join(directory, filename)
        # 打开图片文件
        img = Image.open(filepath)
        # 进行截图
        # cropped_img = img.crop((0, 395, 517, 510))
        cropped_img = img.crop((0, 600, 1035, 800))
        # cropped_img.show()
        # 保存截图
        cropped_img.save(f"./weread_pic/cut_pic/cropped_{filename}")