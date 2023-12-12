import time
import win32gui
from PIL import ImageGrab, ImageChops

class PicTool:
    def __init__(self, window_name, rate):
        self.hwnd = win32gui.FindWindow(0, "window_name")
        if self.hwnd == 0:
            raise Exception(f"没有找到'{window_name}'的窗口")
        self.bound = win32gui.GetWindowRect(self.hwnd)
        self.rate = rate
        # self.rpx = self._rpx2px(self.bound[2] - self.bound[0])

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


    def capture_pic(self, img, x1,y1, x2, y2):
        return img.crop((x1, y1, x2, y2))


if __name__ == "__main__":
    rate = 1.25  # 这个是放大或者缩小的比例，因为展示的时候，显示器可能放大了
    pic_tool = PicTool('微信读书', rate)
    pic_tool.bound = [num * rate for num in pic_tool.bound]
    print(pic_tool.bound)
    tmpImg = None
    for i in range(0, 200):
        img = pic_tool.get_cut_window()
        if not pic_tool.is_same_pic(tmpImg, img):
            img_name = f'../weread_pic/{i}.jpg'
            img.save(img_name)
            tmpImg = img
            print(img_name)
        time.sleep(1)
