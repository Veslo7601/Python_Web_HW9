import scrapy
from scrapy.crawler import CrawlerProcess

class QuotesSpider(scrapy.Spider):

    name = "quote"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "qoutes.json"}

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            yield {
                "tags": quote.xpath("div[@class='tags']/a/text()").extract(),
                "author": quote.xpath("span/small/text()").get(),
                "quote": quote.xpath("span[@class='text']/text()").get(),
            }

        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            yield scrapy.Request(url=self.start_urls[0] + next_page)

class AuthorsSpider(scrapy.Spider):

    name = "authors"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "authors.json"}

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            link = quote.xpath("span/a/@href").get()
            if link:
                yield scrapy.Request(url=self.start_urls[0] + link, callback=self.parse_authors)

        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            yield scrapy.Request(url=self.start_urls[0] + next_page)

    def parse_authors(self, response):
        for author in response.xpath("//div[@class='author-details']"):
            yield {
                "fullname": author.xpath("h3[@class='author-title']/text()").get(),
                "born_date": author.xpath("p/span/text()").get(),
                "born_location": author.xpath("p/span[2]/text()").get(),
                "description": author.xpath("div/text()").get(),
            }

def main():
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()

if __name__ == "__main__":
    main()