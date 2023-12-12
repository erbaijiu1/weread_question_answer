import numpy as np
import paddleocr

class OCRTool:
    def __init__(self):
        # 初始化OCR模型
        self.engine = paddleocr.PaddleOCR()

    def do_ocr(self, cropped_img):
        # 将图像转换为ndarray
        img = np.array(cropped_img)
        # 进行OCR识别
        result = self.engine.ocr(img)

        ret_words = ""
        # 打印识别结果
        for line in result:
            if not line:
                continue
            for word_info in line:
                if len(word_info) == 2 and len(word_info[1]) == 2:
                    ret_words += word_info[1][0]
        return ret_words
