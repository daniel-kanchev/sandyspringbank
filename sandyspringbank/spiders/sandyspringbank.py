import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sandyspringbank.items import Article


class sandyspringbankSpider(scrapy.Spider):
    name = 'sandyspringbank'
    start_urls = ['https://www.sandyspringbank.com/news']

    def parse(self, response):
        links = response.xpath('//a[text()="Read more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/span/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="field-wrapper field field-node--node-post-date field-name-node-post-date field-type-ds field-label-hidden"]/div/div/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="field-wrapper body field field-node--body field-name-body field-type-text-with-summary field-label-hidden"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
