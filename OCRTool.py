import numpy as np
import paddleocr

class OCRTool:
    def __init__(self):
        # 初始化OCR模型
        self.engine = paddleocr.PaddleOCR()

    def do_ocr(self, cropped_img, hint_pre="", hint_end=""):
        # 将图像转换为ndarray
        img = np.array(cropped_img)
        # 进行OCR识别
        result = self.engine.ocr(img)

        ret_words = ""
        # 打印识别结果
        for j, line in enumerate(result):
            if not line:
                continue
            for i, word_info in enumerate(line):
                if len(word_info) == 2 and len(word_info[1]) == 2:
                    if len(hint_pre) > 0:
                        ret_words += hint_pre + str(i+1) + ":" + word_info[1][0] + hint_end
                    else:
                        ret_words += word_info[1][0]

        return ret_words
