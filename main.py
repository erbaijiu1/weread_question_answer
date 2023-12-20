# -*- coding: utf-8 -*-
import queue
import re
import os

import numpy as np
from PIL import Image
import logging
import time

from LLM.geminiTool import GeminiTool
from OCRTool import OCRTool
from QryConsumer import QryConsumer
from pic_tool import PicTool
import argparse
from ultralytics import YOLO

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
        title = item['title']
        abstract = item['abstract']
        abstract = abstract.replace("\n", "")

        for word in char_list:
            title = replace_longest_word(title, word)
            abstract = replace_longest_word(abstract, word)

        print(title)
        print(abstract)
        print()


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

    isShowCut = False
    cap_pic = pic_tool.get_capture_pic_by_location(results[0].orig_img, isShowCut, location)
    return cap_pic


# logger = get_pro_logger(logging.DEBUG)
logger = get_pro_logger(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--screen_rate', type=float)  # 1.25 or 2.5
    args = parser.parse_args()
    screen_rate = args.screen_rate
    # 这里的rate, 表示的是屏幕的放大, 不同显示不一样，可以截图试一下
    if not screen_rate:
        logger.error("param error.", args)
        exit(-1)

    # 1. 获得图片，截图，取得问题
    pic_tool = PicTool('微信读书', screen_rate)
    ocr_tool = OCRTool()

    model = YOLO('./model/que_answer.pt', )  # 预训练的模型

    last_query = ""
    qry_pic = None

    q = queue.Queue()
    threads = []
    thread_num = 3
    for i in range(thread_num):
        t = QryConsumer(q, str(i))
        threads.append(t)
        t.start()

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

            # 放进队列里，由多线程处理，这样可以避免像LLM查询的时候耗时比较长，
            pair = (qry_words, options)
            q.put(pair)
            # query_and_show(qry_words, options)
            last_query = qry_words

        except Exception as e:
            print(e)

    for t in threads:
        t.join()

