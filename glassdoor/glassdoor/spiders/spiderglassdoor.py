import scrapy
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as CondicaoExperada
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from time import sleep


def iniciar_driver():
    chrome_options = Options()
    LOGGER.setLevel(logging.WARNING)
    arguments = ['--lang=pt-BR', '--window-size=1920,1080', '--headless']
    for argument in arguments:
        chrome_options.add_argument(argument)

    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1,

    })
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=chrome_options)

    wait = WebDriverWait(
        driver,
        10,
        poll_frequency=1,
        ignored_exceptions=[
            NoSuchElementException,
            ElementNotVisibleException,
            ElementNotSelectableException,
        ]
    )
    return driver, wait


class ProductScraperSpider(scrapy.Spider):
    # identidade
    name = 'vagasbot'
    # Request

    def start_requests(self):
        # não esqueça de setar ROBOTSTXT_OBEY = False dentro do arquivo settings.py
        urls = ['https://www.glassdoor.com/Job/london-software-engineer-jobs-SRCH_IL.0,6_IC2671300_KO7,24.htm?clickSource=searchBox']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'next_url': url})
    # Response

    def parse(self, response):
        driver, wait = iniciar_driver()
        driver.get(response.meta['next_url'])
        sleep(10)
        response_webdriver = Selector(text=driver.page_source)
        for item in response.xpath("//div[@class='d-flex flex-column pl-sm css-3g3psg css-1of6cnp e1rrn5ka4']"):
            yield {
                'Function': item.xpath('.//a[@class="jobLink css-1rd3saf eigr9kq2"]//span/text()').get(),
                'Company': item.xpath('.//div//a//span[1]/text()').get(),
                'Place': item.xpath('.//div[@class="d-flex flex-wrap css-11d3uq0 e1rrn5ka2"]/span/text()').get()
            }
        try:
            link_proxima_pagina = response.xpath(
                "////div//button[@aria-label='Next']//span").get()
            if link_proxima_pagina is not None:
                link_proxima_pagina_completo = 'https://www.glassdoor.com/Job/london-software-engineer-jobs-SRCH_IL.0,6_IC2671300_KO7,24_IP' + link_proxima_pagina
                yield scrapy.Request(url=link_proxima_pagina_completo, callback=self.parse)
        except:
            print('CHEGAMOS NA ÚLTIMA PÁGINA')
        driver.close()