# -*- coding: utf-8 -*-

import re
import os

import numpy as np
from PIL import Image
import logging
import time

from LLM.geminiTool import GeminiTool
from OCRTool import OCRTool
from pic_tool import PicTool
import argparse
from ultralytics import YOLO
import cv2

from search.search_tool import SearchTool

# 设置日志级别为ERROR
logging.getLogger('ppocr').setLevel(logging.ERROR)
logging.getLogger('ultralytics').setLevel(logging.ERROR)


def get_pro_logger(log_level=None):
    # 创建服务的logger
    logger = logging.getLogger('weread_question_answer')
    # 设置日志级别
    logger.setLevel(logging.INFO)
    if log_level:
        logger.setLevel(log_level)

    return logger


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
def query_and_show(qry_words, options):
    print(f"Q:  {qry_words}\n {options}")
    regex = r"第(\d+)题"
    match = re.search(regex, qry_words)
    if not qry_words or match:
        print(f"filter query: {qry_words}")
        return

    # 搜索引擎的补充信息
    try:
        search = SearchTool()
        add_info = search.get_content_only(qry_words, 100)
        logger.debug(add_info)
    except Exception as e:
        logger.error(e)

    llm_req = "问题：" + qry_words + ";"
    if options:
        llm_req += options
    if add_info:
        llm_req += "相关搜索资料：" + add_info

    # llm_req += "\n如果资料不相关就忽略，回答:选项+答案即可。"
    llm_req += "\n回答:选项+答案即可。"
    try:
        llm = GeminiTool()
        response = llm.get_response(llm_req)
        print(f"\033[31m{response}\033[0m")
        logger.debug(response)
    except Exception as e:
        logger.error(e)

    # 展示结果
    # show_result(results, qry_words)
    time.sleep(0.2)


# 本地环境测试及验证
def get_pic_ocr_from_local():
    dire = "weread_pic"  # 目录路径
    dire = "weread_pic/free_day/"  # 目录路径
    ocr_tool = OCRTool()
    location = (0, 600, 1035, 800)

    # 遍历目录下的文件
    last_query = ""  # 用于判断是不是同一个问题，同一个问题不需要再次发查询，避免刷屏
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
            query_and_show(qry_words)
            last_query = qry_words


def get_target_location(results, label, min_conf):
    get_key = None
    names = results[0].names
    for key in names:
        if names[key] == label:
            get_key = key
            break

    if get_key is None:
        return None

    boxes = results[0].boxes
    for i in range(0, len(boxes)):
        # Find the record corresponding to the key
        if boxes.cls[i] != get_key:
            continue

        # check the conf
        if boxes.conf[i] < min_conf:
            return None

        xyxy = boxes.xyxy[i]
        return (int(xyxy[1]), int(xyxy[3]), int(xyxy[0]), int(xyxy[2]))


def get_cut_pic(pic_tool, results, label, min_conf):
    location = get_target_location(results, label, min_conf)
    if not location:
        return None
    # answer_location = get_target_location(results, 'answer', 0.3)

    isShowCut = False
    cap_pic = pic_tool.get_capture_pic_by_location(results[0].orig_img, isShowCut, location)
    return cap_pic
    # if not answer_location:
    #     answer_cap_pic = pic_tool.get_capture_pic_by_location(results[0].orig_img, isShowCut, answer_location)
    # return que_cap_pic, answer_cap_pic


# logger = get_pro_logger(logging.DEBUG)
logger = get_pro_logger(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_mode', type=int)
    parser.add_argument('--screen_rate', type=float)  # 1.25 or 2.5
    args = parser.parse_args()
    test_mode = args.test_mode
    screen_rate = args.screen_rate
    # 这里的rate, 表示的是屏幕的放大, 不同显示不一样，可以截图试一下
    if not screen_rate:
        logger.error("param error.", args)
        exit(-1)

    if test_mode == 1:
        get_pic_ocr_from_local()
    else:
        # 1. 获得图片，截图，取得问题
        pic_tool = PicTool('微信读书', screen_rate)
        ocr_tool = OCRTool()

        model = YOLO('./model/que_answer.pt', )  # 预训练的模型

        last_query = ""
        qry_pic = None
        logger.info("ready? go...")
        while True:
            time.sleep(0.2)
            try:
                logger.debug("new job.")
                # get wx window img
                window_pic = pic_tool.get_window_img()

                # 将截图转换为 NumPy 数组
                arr = np.asarray(window_pic)
                # 将 NumPy 数组转换为 PIL Image 对象
                image = Image.fromarray(arr)
                # image.show()

                # predict
                # image = cv2.imread("./pic/ed_16.jpg")
                results = model.predict(source=image, save=False, save_txt=False, save_crop=False)
                if len(results) == 0:
                    logger.debug("no result")
                    continue
                logger.debug("get result")

                # 获取到问题的截图
                que_cap_pic = get_cut_pic(pic_tool, results, 'que', 0.3)
                if not que_cap_pic:
                    continue
                if pic_tool.is_same_pic(qry_pic, que_cap_pic):
                    logger.debug("same pic.")
                    continue
                qry_pic = que_cap_pic
                logger.debug("get question pic.")

                # 2. 再调用切图，及展示
                qry_words = ocr_tool.do_ocr(que_cap_pic)
                logger.debug(f"Q：{qry_words}  {last_query} ")
                if last_query == qry_words:
                    logger.debug(f"same qry:{qry_words} ")
                    continue

                answer_cap_pic = get_cut_pic(pic_tool, results, 'answer', 0.3)
                logger.debug("get answer pic.")
                options = ""
                if answer_cap_pic:
                    options = ocr_tool.do_ocr(answer_cap_pic, "选项", ";  ")
                    logger.debug(options)

                # 进行查询, 并展示结果
                query_and_show(qry_words, options)
                last_query = qry_words

            except Exception as e:
                print(e)
