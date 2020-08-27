import requests
from bs4 import BeautifulSoup
from lxml import etree
import json
import time
import random


class ICOBenchDataScraper(object):
    def __init__(self):
        self.base_url = 'http://icobench.com/icos?page='

        # proxy server
        proxy_host = "dyn.horocn.com"
        proxy_port = "50000"

        # proxy tunnel access token
        proxy_user = "QPZF1674794049561581"
        proxy_pass = "FG6J4wADOpB0"

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

        self.result_list = []
        self.failed_list = []
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
                    res = requests.get(url, headers=header, proxies=self.proxies, timeout=10)
                    soup = BeautifulSoup(res.content.decode(), 'lxml')
                    self.retry_count = 0
                    return soup.prettify()
                except requests.exceptions.RequestException as e:
                    print(e)
                    print("\n Now retry to connect to " + url + "\n")
                    time.sleep(5)
                    self.retry_count += 1
                    continue
            else:
                print("Request to " + url + " failed\n")
                self.failed_list.append(url)
                self.retry_count = 0
                return "error"

    def get_ico_url(self, url):
        try:
            data = self.get_response("http://icobench.com" + url)
            if data == "error":
                return
            x_data = etree.HTML(data)
            result_score = x_data.xpath('//a[@class="view_rating"]/div/text()')
            result_name = x_data.xpath('//*[@id="profile_header"]/div//h1[@class = "notranslate"]/text()')
            result_url = x_data.xpath('//a[@class="button_big"]/@href')
            print("Got score: " + result_name[0].replace(' ', '').replace('\n', ''))
            item = {
                "ICO name": result_name[0].replace(' ', '').replace('\n', ''),
                "ICO score": result_score[0].replace(' ', '').replace('\n', ''),
                "ICO URL": result_url[0].replace(' ', '').replace('\n', '')
            }
            print(item)
            self.result_list.append(item)
        except Exception as e:
            print(e)

    @staticmethod
    # 2. Parse Data
    def get_links(data):
        try:
            x_data = etree.HTML(data)
            result = x_data.xpath('//a[@class="name notranslate"]/@href')
            print(result)
            return result
        except Exception as e:
            print(e)

    # 3. Save Data
    def save_data(self):
        data_str = json.dumps(self.result_list, indent=4)
        with open('ICOBenchDataList.json', 'w', encoding='utf-8') as f:
            f.write(data_str)
        failed_str = json.dumps(self.failed_list, indent=4)
        with open('ICOBenchFailedList.json', 'w', encoding='utf-8') as f:
            f.write(failed_str)

    # 4. Launch
    def run(self):
        page = 477
        for i in range(1, page + 1):
            # 1. Concatenate URL
            url = self.base_url + str(i)
            # 2. Send request
            data = self.get_response(url)
            if data == "error":
                continue
            # 3. Get links
            print("Start get links on page:" + str(i) + "\n")
            links = self.get_links(data)
            for link in links:
                self.get_ico_url(link)
            if i % 100 == 0:
                self.save_data()

        # 4. Save data
        self.save_data()


ICOBenchDataScraper().run()
