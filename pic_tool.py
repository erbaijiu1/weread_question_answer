import time
import win32gui
from PIL import ImageGrab, ImageChops, Image


class PicTool:
    def __init__(self, window_name, rate):
        self.hwnd = win32gui.FindWindow(0, f"{window_name}")
        if self.hwnd == 0:
            raise Exception(f"没有找到'{window_name}'的窗口")
        bound = win32gui.GetWindowRect(self.hwnd)
        # 使用 map() 函数
        self.bound = map(lambda x: x * 2.5, bound)
        self.rate = rate

    def is_same_pic(self, imgA, imgB):
        if imgA is None or imgB is None:
            return False
        diff = ImageChops.difference(imgA, imgB)
        if diff.getbbox():
            return False
        return True

    # 截图
    def get_cut_window(self):
        cut_pic = ImageGrab.grab(self.bound)
        return cut_pic

    def capture_pic(self, img, location):
        return img.crop(location)

    def get_capture_pic_from_boxes(self, result, isShow):
        im = result.orig_img
        xyxy = result.boxes.xyxy
        BGR = True
        crop = im[int(xyxy[0, 1]):int(xyxy[0, 3]), int(xyxy[0, 0]):int(xyxy[0, 2]), ::(1 if BGR else -1)]
        img = Image.fromarray(crop[..., ::-1])
        if isShow:
            img.show()

        return img

if __name__ == "__main__":
    rate = 1.25  # 这个是放大或者缩小的比例，因为展示的时候，显示器可能放大了
    rate = 2.5
    location = (0, 395, 517, 510)
    file_pre = "ed"
    pic_tool = PicTool('微信读书', rate, location)
    print("src:bound:", pic_tool.bound, rate)
    pic_tool.bound = [num * rate for num in pic_tool.bound]
    print("src:bound:", pic_tool.bound)
    tmpImg = None
    for i in range(0, 200):
        img = pic_tool.get_cut_window()
        if not pic_tool.is_same_pic(tmpImg, img):
            img_name = f'./weread_pic/{file_pre}_{i}.jpg'
            img.save(img_name)
            tmpImg = img
            print(img_name)
        time.sleep(1)
