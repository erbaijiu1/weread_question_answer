import numpy as np
import win32gui
from PIL import ImageGrab
import requests
import json
import re
import jieba
import os
from PIL import Image
import logging
import time
from baidusearch.baidusearch import search

from OCRTool import OCRTool
from pic_tool import PicTool

last_query = ""

# 设置日志级别为ERROR
logging.getLogger('ppocr').setLevel(logging.ERROR)
logging.getLogger('jieba').setLevel(logging.ERROR)



def get_window_pos(name):
    handle = win32gui.FindWindow(0, name)  # 获取窗口句柄
    if handle == 0:
        return None
    else:
        return win32gui.GetWindowRect(handle)  # 获取窗口的位置和大小


def get_cut():
    # 获取微信读书窗口的位置和大小
    x1, y1, x2, y2 = get_window_pos('微信读书')
    print(x1,y1,x2,y2)
    # 获取微信读书窗口的截图
    # screenshot = ImageGrab.grab((x1, y1, x2, y2))
    #
    # # 保存截图
    # screenshot.save("wechat_reading.png")
    #
    # # 打开并显示图像
    # img = Image.open("wechat_reading.png")
    # img.show()

def google_search(search_term, api_key, cse_id, start, num, language):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': search_term,
        'key': api_key,
        'cx': cse_id,
        'start': start,
        'num': num
        # ,'lr': 'lang_zh-CN' # 设置语言为中文
    }

    proxy = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }

    response = requests.get(base_url, params=params, proxies=proxy)
    return response.json()


def do_google_search(qry_word):
    # 使用你的API密钥和自定义搜索引擎ID
    api_key = ""
    api_key = ""
    cse_id = ""

    # 搜索词
    search_term = qry_word

    # 开始索引和结果数量
    start = 10
    num = 10

    # 语言设置为中文
    language = "zh-CN"

    # 调用函数
    result = google_search(search_term, api_key, cse_id, start, num, language)

    return result


def get_longest_words_final(qry_word):
    sentence = qry_word
    words = list(jieba.cut(sentence))

    non_empty_words = [word for word in words if word.strip() and len(word) > 1]
    # 按长度排序
    sorted_words = sorted(non_empty_words, key=len, reverse=True)

    if len(sorted_words) <= 1:
        return sorted_words

    ret_list = []
    first_word = sorted_words[0]
    ret_list.append(first_word)

    for word in sorted_words[1:]:
        if word not in first_word and len(ret_list) < 2 and len(word) > 1:
            ret_list.append(word)

    return ret_list


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
    print(f"doing:{qry_words}")
    if not qry_words or ('第' in qry_words and '题' in qry_words):
        print(f"filter query: {qry_words}")
        return

    # 进行关键字查询
    results = baidu_search(qry_words, 4)

    # 展示结果
    show_result(results, qry_words)

    time.sleep(3)


# 本地环境测试及验证
def get_pic_ocr_from_local():
    dire = "weread_pic"  # 目录路径
    last_query = "" # 用于判断是不是同一个问题，同一个问题不需要再次发查询，避免刷屏
    ocr_tool = OCRTool()
    # 遍历目录下的文件
    for filename in os.listdir(dire):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # 打开图片文件
            filepath = os.path.join(dire, filename)
            img = Image.open(filepath)
            # 截图
            cropped_img = img.crop((0, 395, 517, 510))

            # OCR得到文字
            qry_words = ocr_tool.do_ocr(cropped_img)

            if last_query == qry_words:
                print(f"same qry:{qry_words} donothing.")
                continue

            # 切图跟查询
            word_query(qry_words)
            last_query = qry_words


def baidu_search(qry_words, number):
    results = search(qry_words, number)  # returns 10 or less results
    return results


if __name__ == "__main__":
    ocr_tool = OCRTool()
    # 获取程序开始时间戳
    start_time = time.time()
    local_test = True
    if local_test:
        get_pic_ocr_from_local()
    else:
        # 1. 获得图片，截图，取得问题
        rate = 1.25  # 这个是放大或者缩小的比例，因为展示的时候，显示器可能放大了
        pic_tool = PicTool('微信读书', rate)
        x1 = 0
        y1 = 395
        x2 = 517
        y2 = 510

        last_query = ""
        while True:
            window_pic = pic_tool.get_cut_window()
            cap_pic = pic_tool.capture_pic(window_pic, x1, y1, x2, y2)

            # 2. 再调用切图，及展示
            qry_words = ocr_tool.do_ocr(cap_pic)

            if last_query == qry_words:
                print(f"same qry:{qry_words} donothing.")
                continue

            word_query(qry_words)
            last_query = qry_words

    # 打印程序耗时
    end_time = time.time()
    print(f"程序耗时：{end_time-start_time:.2f}秒")
