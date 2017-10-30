import scrapy
import os

DEFAULT_MAX = 100

# get next: '//table[contains(@class, "navTable")]/tbody/tr/td[div[contains(@class, "iright")]]/a/@href'
# get all children: '//div/div/*[not(@class="navTable")]/ul[contains(@class, "ulPopover")]/li/a[contains(@class, "identifier")]/@href'
# parse children:
  # i) get hrefs of Billable children: '//div[@class="body-content"]/ul[@class="codeHierarchy"]//li[i[contains(@class, "success")]]//a/@href'
  # ia) get header: '//h2[@class="codeDescription"]'
  # ib) get description

def extract_from_css(query):
    return response.css(query).extract_first().strip()

data = []

class ICD10DiagnosesSpider(scrapy.Spider):
    name = "icd10_diagnoses"
    root_url = 'http://www.icd10data.com'
    start_urls = [
        'http://www.icd10data.com/ICD10CM/Codes/A00-B99',
        'http://www.icd10data.com/ICD10CM/Codes/C00-D49',
    ]

    def parse(self, response):
        # page = response.url.split("?page=")
        # page = 1 if len(page) != 2 else int(page[-1])

        # parse each listing on the page
        for href in response.xpath('//div/div/*[not(@class="navTable")]/ul[contains(@class, "ulPopover")]/li/a[contains(@class, "identifier")]/@href'):
            yield response.follow(self.root_url+href.extract(), self.parse_general_diagnosis)

    def parse_general_diagnosis(self, response):
        diagnosis_hrefs = response.xpath('//div[@class="body-content"]/ul[@class="codeHierarchy"]//li[i[contains(@class, "success")]]//a/@href')

        for href in diagnosis_hrefs:
            yield response.follow(self.root_url+href.extract(), self.parse_diagnosis)

        yield {}

    def parse_diagnosis(self, response):
      header = response.xpath('//h2[@class="codeDescription"]/text()').extract_first().strip()
      code = response.xpath('//span[@class="identifierDetail"]/text()').extract_first().strip()
      diagnosis = {
        'code': code,
        'header': header
      }
      data.append(diagnosis)
      self.logger.info(data)
      yield diagnosis