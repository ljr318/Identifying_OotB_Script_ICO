import requests
from bs4 import BeautifulSoup
from lxml import etree
import random
import json
import time


class IcoUrlSpider(object):
    def __init__(self):
        self.base_url = 'http://foundico.com/icos/?PAGEN_2='
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50"
        ]
        self.result_list = []
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
                    res = requests.get(url, headers=header)
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
                self.retry_count = 0
                return "error"

    def get_ico_url(self, url):
        try:
            data = self.get_response("http://foundico.com" + url)
            if data == "error":
                return
            x_data = etree.HTML(data)
            result_url = x_data.xpath('//i[@class="fa fa-globe"]/../following-sibling::td[2]/a/text()')
            result_name = x_data.xpath('//div[@class="col-xs-12 col-sm-9 col-md-9 col-lg-9"]/h1/text()')
            result_score = x_data.xpath('//span[@itemprop="ratingValue"]/@content')
            result_platform = x_data.xpath('//i[@class="fa fa-cog"]/../following-sibling::td[2]/text()')
            print("Got URL: " + result_url[0])
            if len(result_score) == 0:
                result_score.append('0')
            if len(result_platform) == 0:
                result_platform.append('Other')

            item = {
                "ICO name": result_name[0].replace(' ', '').replace('\n', ''),
                "ICO URL": result_url[0].replace(' ', '').replace('\n', ''),
                "ICO score": result_score[0].replace(' ', '').replace('\n', ''),
                "ICO platform": result_platform[0].replace(' ', '').replace('\n', '')
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
            result = x_data.xpath('//div[@class="ics-txt"]/a/@href')
            print(result)
            return result
        except Exception as e:
            print(e)

    # 3. Save Data
    def save_data(self):
        data_str = json.dumps(self.result_list, indent=4)
        with open('FoundICODataList.json', 'w', encoding='utf-8') as f:
            f.write(data_str)

    # 4. Launch
    def run(self):
        page = 159
        for i in range(1, page+1):
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
            if i % 50 == 0:
                self.save_data()

        # 4. Save data
        self.save_data()


IcoUrlSpider().run()
