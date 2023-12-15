import re
import os

import numpy as np
from PIL import Image
import logging
import time
from baidusearch.baidusearch import search
from OCRTool import OCRTool
from pic_tool import PicTool
import argparse
from ultralytics import YOLO
import cv2



# 设置日志级别为ERROR
logging.getLogger('ppocr').setLevel(logging.ERROR)


def replace_longest_word(src_content, src_word):
    return src_content.replace(src_word, f"\033[31m{src_word}\033[0m")


def show_result(results, qry_words):
    char_list = [char for char in qry_words]

    for item in results:
        # print(item)
        title = item['title']
        abstract = item['abstract']
        abstract = abstract.replace("\n", "")

        for word in char_list:
            title = replace_longest_word(title, word)
            abstract = replace_longest_word(abstract, word)

        print(title)
        print(abstract)
        print()


# 截图跟查询
def word_query(qry_words):
    print(f"Q:  {qry_words}")
    regex = r"第(\d+)题"
    match = re.search(regex, qry_words)
    if not qry_words or match:
        print(f"filter query: {qry_words}")
        return

    # 进行关键字查询
    results = baidu_search(qry_words, 2)

    # 展示结果
    show_result(results, qry_words)
    time.sleep(2)


# 本地环境测试及验证
def get_pic_ocr_from_local():
    dire = "weread_pic"  # 目录路径
    dire = "weread_pic/free_day/"  # 目录路径
    ocr_tool = OCRTool()
    location = (0, 600, 1035, 800)

    # 遍历目录下的文件
    last_query = "" # 用于判断是不是同一个问题，同一个问题不需要再次发查询，避免刷屏
    for filename in os.listdir(dire):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # 打开图片文件
            filepath = os.path.join(dire, filename)
            img = Image.open(filepath)
            # 截图
            cropped_img = img.crop(location)
            # OCR得到文字
            qry_words = ocr_tool.do_ocr(cropped_img)
            # 重复的不进行查询
            if last_query == qry_words:
                # print(f"same qry:{qry_words} donothing.")
                continue

            # 切图跟查询
            word_query(qry_words)
            last_query = qry_words


def baidu_search(qry_words, number):
    results = search(qry_words, number)  # returns 10 or less results
    return results


def get_cut_pic(window_pic, pic_tool):
    # 将截图转换为 NumPy 数组
    arr = np.asarray(window_pic)
    # 将 NumPy 数组转换为 PIL Image 对象
    image = Image.fromarray(arr)
    # image.show()

    # predict
    # image = cv2.imread("./pic/ed_16.jpg")
    results = model.predict(source=image, save=False, save_txt=False, save_crop=False)
    if len(results) == 0:
        print("no result")
        return None

    # print(results[0].boxes.conf)
    if len(results[0].boxes.conf) == 0 or results[0].boxes.conf < 0.4:
        # print("result not fit,", results[0].boxes.conf)
        return None

    # cap_pic = pic_tool.capture_pic(window_pic)
    isShowCut = False
    cap_pic = pic_tool.get_capture_pic_from_boxes(results[0], isShowCut)
    return cap_pic


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_mode', type=int)
    parser.add_argument('--screen_rate', type=float) # 1.25 or 2.5
    args = parser.parse_args()
    test_mode = args.test_mode
    screen_rate = args.screen_rate
    if not screen_rate:
        print("param error.", args)
        exit(-1)

    rate = screen_rate
    if test_mode == 1:
        get_pic_ocr_from_local()
    else:
        # 1. 获得图片，截图，取得问题
        pic_tool = PicTool('微信读书', rate)
        ocr_tool = OCRTool()

        model = YOLO('./model/question.pt', )  # 预训练的 YOLOv8n 模型

        last_query = ""
        while True:
            try:
                # get wx window img
                window_pic = pic_tool.get_cut_window()

                # 获取到截图
                cap_pic = get_cut_pic(window_pic, pic_tool)
                if not cap_pic:
                    continue

                # 2. 再调用切图，及展示
                qry_words = ocr_tool.do_ocr(cap_pic)

                if last_query == qry_words:
                    print(f"same qry:{qry_words} donothing.")
                    continue

                # 进行查询, 并展示结果
                word_query(qry_words)
                last_query = qry_words

                time.sleep(0.1)
            except Exception as e :
                print(e)
