# https://cn.bing.com/search?q=test&first=10
import json
import os
from pprint import pprint
from urllib import parse, request

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class SearchTool:
    def __init__(self, search_type=None, count=3):
        if not search_type:
            self.search_type = "bing"
        else:
            self.search_type = search_type

        self.user_agent = UserAgent()
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_cx = os.getenv('GOOGLE_SEARCH_CX')
        self.count = count


    def baidu_search(self, question):
        random_ua = self.user_agent.random

        url = 'https://www.baidu.com/s?wd={}'.format(parse.quote(question))
        headers = {
            'User-Agent': f'{self.user_agent.random}',
        }
        req = request.Request(url, headers=headers)
        response = request.urlopen(req)
        content = response.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        knowledge = soup.get_text()
        print(knowledge)
        return knowledge

    def bing_search(self, question):
        # Add your Bing Search V7 subscription key and endpoint to your environment variables.
        subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
        # endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/bing/v7.0/search"
        endpoint = "https://api.bing.microsoft.com/v7.0/search"

        # Construct a request
        mkt = 'en-US'
        params = {'q': question, 'mkt': mkt, 'count':self.count }
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}

        # Call the API
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()

            response_data = json.loads(response.text.encode('utf-8'))
            # response_data = response.text.encode('utf-8').json()
            results = [{"title": d["name"], "snippet": d["snippet"]} for d in response_data["webPages"]["value"]]
            return results

            # result = [{"title": d["name"], "snippet": d["snippet"]} for d in json.loads(response.text)]
            # return result

        except Exception as ex:
            raise ex

    def google_search(self, question):
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': question,
            'key': self.google_api_key,
            'cx': self.google_cx,
            'start': 0,
            'num':4
            # ,'lr': 'lang_zh-CN' # 设置语言为中文
        }

        proxy = {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890'
        }

        response = requests.get(base_url, params=params, proxies=proxy)
        response_data = json.loads(response.text.encode('utf-8'))

        results = [{"title": d["title"], "snippet": d["snippet"]} for d in response_data["items"]]
        return results

    def do_search(self, question):
        results = []
        if self.search_type == "bing":
            results = self.bing_search(question)
        elif self.search_type == "google":
            results = self.google_search(question)
        else: # 很不幸，其它的容易被封
            pass
            # return None
        return results

    def get_content_only(self, question, each_max_len=None):
        results = self.do_search(question)
        ret_context = ""
        for one_context in results:
            if each_max_len and len(one_context['snippet']) > each_max_len:
                ret_context += one_context['snippet'][:each_max_len] + ";\n"
            else:
                ret_context += one_context['snippet'] + ";\n"

        return ret_context


if __name__ == "__main__":
    st = SearchTool()
    st = SearchTool("bing")
    st = SearchTool("google")
    # additional materials
    result = st.get_content_only("强弩之末，力_穿鲁编。")
    print(result)
