import logging
import re
import threading
import time

from LLM.geminiTool import GeminiTool
from search.search_tool import SearchTool

logger = logging.getLogger("weread_question_answer")


class QryConsumer(threading.Thread):
    def __init__(self, q, thread_name):
        super().__init__()
        self.q = q
        self.search = SearchTool()
        self.llm = GeminiTool()
        self.thread_name = thread_name

    def run(self):
        while True:
            value = self.q.get()
            if value is None:
                time.sleep(0.2)
                continue

            qry_words, options = value

            # 进行查询, 并展示结果
            self.query_and_show(qry_words, options)

    # 查询
    def query_and_show(self, qry_words, options):
        print(f"Q:  {qry_words}\n {options}")
        regex = r"第(\d+)题"
        match = re.search(regex, qry_words)
        if not qry_words or match:
            print(f"filter query: {qry_words}")
            return

        llm_req = "问题：" + qry_words + ";"
        if options:
            llm_req += options

        llm_req += self.add_add_info(qry_words )

        # llm_req += "\n如果资料不相关就忽略，回答:选项+答案即可。"
        llm_req += "\n回答:选项+答案即可。"
        try:
            response = self.llm.get_response(llm_req)
            print(f"thread:{self.thread_name}:\033[31m{response}\033[0m")
            logger.debug(response)
        except Exception as e:
            logger.error(e)

        # 展示结果
        # show_result(results, qry_words)
        time.sleep(0.2)

    def add_add_info(self, qry_words):
        # 搜索引擎的补充信息
        try:
            add_info = self.search.get_content_only(qry_words, 150)
            logger.debug(add_info)
            print(add_info)
            return "可能有用的资料：" + add_info
        except Exception as e:
            logger.error(e)
            return ""

