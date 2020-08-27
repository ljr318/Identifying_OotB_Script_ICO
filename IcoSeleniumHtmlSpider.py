from bs4 import BeautifulSoup
import json
import time
from selenium import webdriver


class IcoSeleniumHtmlSpider(object):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(executable_path=r'./drivers/chromedriver.exe', options=options)
        self.retry_count = 0

    # 1. Send Request
    def get_response(self, url):
        while True:
            if self.retry_count < 2:
                try:
                    self.browser.get(url)
                    html = self.browser.page_source
                    soup = BeautifulSoup(html, 'lxml')
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
        with open("ICO_Dynamic_Htmls/" + name + '.html', 'w', encoding='utf-8') as f:
            f.write(html_metadata)

    # 3. Launch
    def run(self):
        with open('IcoDataList.json', 'r') as f:
            items = json.load(f)
        for item in items:
            # 1. Get URL and name
            url = item['ICO URL']
            name = item['ICO name']
            # 2. Send request
            print("Start get html metadata on:" + url + "\n")
            data = self.get_response(url)
            if data == "error":
                continue
            # 3. Save data
            self.save_data(data, name)


IcoSeleniumHtmlSpider().run()
