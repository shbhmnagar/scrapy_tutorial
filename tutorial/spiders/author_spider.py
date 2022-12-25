import scrapy


class AuthorSpider(scrapy.Spider):
    name = 'author'

    start_urls = ['https://quotes.toscrape.com/']

    def parse(self, response):
        author_page_links = response.xpath('//*[@class="author"]/following-sibling::a[1]')
        yield from response.follow_all(author_page_links, self.parse_author)

        pagination_links = response.xpath('//li[@class="next"]/a')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_author(self, response):

        yield {
            'name': response.xpath('//h3[@class="author-title"]/text()').get(),
            'birth_date': response.xpath('//*[@class="author-born-date"]/text()').get(),
            'birth_location': response.xpath('//*[@class="author-born-location"]/text()').get(),
            'bio': response.xpath('//*[@class="author-description"]/text()').get(),
        }