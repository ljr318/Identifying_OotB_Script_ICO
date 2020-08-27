import requests
from bs4 import BeautifulSoup
from lxml import etree
import json
import time
import random


class IcoBackendTechStackScraper(object):
    def __init__(self):
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

        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"
        ]

        self.base_url = 'https://builtwith.com/'
        self.retry_count = 0
        self.result_list = []

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
                    res = requests.get(url, headers=header, proxies=self.proxies, timeout=8)
                    soup = BeautifulSoup(res.content.decode(), 'lxml')
                    self.retry_count = 0
                    return soup.prettify()
                except Exception as e:
                    print(e)
                    print("\n Now retry to connect to " + url + "\n")
                    self.retry_count += 1
                    continue
            else:
                print("Request to " + url + " failed\n")
                self.retry_count = 0
                return "error"

    def get_ico_tech_profile(self, url, name):
        try:
            data = self.get_response(self.base_url + url)
            if data == "error":
                return
            x_data = etree.HTML(data)
            result = x_data.xpath('//div[@class="row mb-2 mt-2"]/div/h2/a/text()')
            if len(result) == 0:
                data = self.get_response(self.base_url + url)
                x_data = etree.HTML(data)
                result = x_data.xpath('//div[@class="row mb-2 mt-2"]/div/h2/a/text()')
            if len(result) == 0:
                return
            print("Got Tech Profile on: " + name)
            item = {
                "ICO name" : name,
                "Tech Profile" : result
            }
            print(item)
            self.result_list.append(item)
            self.save_data(self.result_list, name)
        except Exception as e:
            print(e)

    @staticmethod
    # 2. Get Ico Website list
    def get_ico_website_info():
        try:
            with open('IcoDataList.json', 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(e)

    # 3. Save Data
    @staticmethod
    def save_data(data, name):
        data_str = json.dumps(data)
        with open('Collected_Data/'+name+'.json', 'w', encoding='utf-8') as f:
            f.write(data_str)

    # 4. Launch
    def run(self):
        ico_websites = self.get_ico_website_info()
        for item in ico_websites:
            self.get_ico_tech_profile(item['ICO URL'][7:], item['ICO name'])


IcoBackendTechStackScraper().run()
