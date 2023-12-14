import re
import os
from PIL import Image
import logging
import time
from baidusearch.baidusearch import search
from OCRTool import OCRTool
from pic_tool import PicTool
import argparse

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_mode', type=bool)
    parser.add_argument('--question_type', type=str)
    parser.add_argument('--pc_belong', type=str)
    args = parser.parse_args()

    test_mode = args.test_mode
    question_type = args.question_type
    pc_belong = args.pc_belong
    if not test_mode or not question_type or not pc_belong:
        print("param error.", args)
        exit(-1)

    rate = 2.5 if pc_belong == "w" else 1.25
    location = (0, 395, 517, 510)
    if pc_belong == "w":
        # 下面location是要切图的位置，就是问题的区域
        if question_type == "free_day":
            location = (0, 600, 1035, 800)

    if test_mode:
        get_pic_ocr_from_local()
    else:
        # 1. 获得图片，截图，取得问题
        pic_tool = PicTool('微信读书', rate, location)
        ocr_tool = OCRTool()

        last_query = ""
        while True:
            window_pic = pic_tool.get_cut_window()
            cap_pic = pic_tool.capture_pic(window_pic)

            # 2. 再调用切图，及展示
            qry_words = ocr_tool.do_ocr(cap_pic)

            if last_query == qry_words:
                print(f"same qry:{qry_words} donothing.")
                continue

            # 进行查询, 并展示结果
            word_query(qry_words)
            last_query = qry_words
