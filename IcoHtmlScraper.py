import requests
from bs4 import BeautifulSoup
import json
import time
import random


class IcoHtmlScraper(object):
    def __init__(self):
        '''
        # proxy server
        proxy_host = "dyn.horocn.com"
        proxy_port = "50000"

        # proxy tunnel access token
        proxy_user = "NJLF1674199269914306"
        proxy_pass = "HYn6K7fBcRfC"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxy_host,
            "port": proxy_port,
            "user": proxy_user,
            "pass": proxy_pass,
        }

        self.proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        '''

        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"
        ]
        self.retry_count = 0

    # 1. Send Request
    def get_response(self, url):
        while True:
            if self.retry_count < 5:
                try:
                    random_user_agent = random.choice(self.user_agent_list)
                    header = {
                        'User-Agent': random_user_agent,
                        'Connection': 'close'
                    }
                    res = requests.get(url, headers=header, timeout=10, verify=False)
                    soup = BeautifulSoup(res.text, 'lxml')
                    self.retry_count = 0
                    return soup.prettify()
                except Exception as e:
                    print(e)
                    print("\n Now retry to connect to " + url + "\n")
                    time.sleep(5)
                    self.retry_count += 1
                    continue
            else:
                print("Request to " + url + " failed\n")
                self.retry_count = 0
                return "error"

    # 2. Save Data
    @staticmethod
    def save_data(html_metadata, name):
        with open("ICO_Htmls/" + name + '.html', 'w', encoding='utf-8') as f:
            f.write(html_metadata)

    # 3. Launch
    def run(self):
        with open('IcoDataList.json', 'r') as f:
            items = json.load(f)
        for item in items:
            # 1. Concatenate URL
            url = item['ICO URL']
            name = item['ICO name']
            # 2. Send request
            print("Start get html metadata on:" + url + "\n")
            data = self.get_response(url)
            if data == "error":
                continue
            # 3. Save data
            self.save_data(data, name)


IcoHtmlScraper().run()
