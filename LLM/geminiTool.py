import os
import pathlib
import textwrap
import time
import google.generativeai as genai
from IPython.display import Markdown


# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)
#

# %%time
# response = model.generate_content("how to white hello with Python?")
# result = to_markdown(response.text)
# print(result)

# %%time
# response = model.generate_content("问题：“黄梅戏”是哪个省的地方戏? 选项1：福建，选项2：湖南，选项3：安徽 具体应该选哪一个，给出答案就好", stream=True)
# response = model.generate_content("问题：“扭亏增” 选项1：盈，选项2：策，选项3：股  具体应该选哪一个，给出'选项编号+答案'就好")
# response = model.generate_content("问题：强弩之末，力__穿鲁编。 选项1：不能，选项2：没有  具体应该选哪一个，给出'选项编号+答案'就好")
# for chunk in response:
#   print(chunk.text)
#   print("_"*80)


class GeminiTool:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=self.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

        # 设置 HTTP 代理
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
        # 设置 HTTPS 代理
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

    def to_markdown(self, text):
      text = text.replace('•', '  *')
      return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

    def get_response(self, req_text):
        response = self.model.generate_content(f"{req_text}")
        return response.text

if __name__ == "__main__":


    additional_materials = "东汉·班固《汉书·韩安国传》：“且臣闻之，冲风之衰，不能起毛羽；强弩之末，力不能入鲁缟。 ... 强弩之末，势不能穿鲁缟 '者也。” 明·胡应麟《诗薮内编》：“太白纵横 ...;... 力竭。《三國志．卷三十五．蜀書．諸葛亮傳》：「曹操之眾，遠來疲弊，聞追豫州，輕騎一日一夜行百餘里，此所謂『彊弩之末，勢不能穿魯縞。』者也。」也作「強弩之末」。;强弩之末，势不能穿鲁缟”，谚语，意思是强弩发射出去的箭，到最后，连薄薄的绢都穿 ... 声明：百度百科是免费编辑平台，无收费代编服务. 详情. 正在收听: 一分钟了解 ...;老公偷删微信聊天记录➡️监控微信【微信：5010716】同步记录➡️老公偷删微信聊天记录.HWe.;"
    # req_text = additional_materials + "问题：强弩之末，力__穿鲁编。 选项1：不能，选项2：没有  具体应该选哪一个，给出'选项编号+答案'就好"
    req_text = "问题：强弩之末，力__穿鲁编。 选项1：不能，选项2：没有  具体应该选哪一个，给出'选项编号+答案'就好"
    print(GeminiTool().get_response(req_text))
