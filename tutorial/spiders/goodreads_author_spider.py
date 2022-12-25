import scrapy


class AuthorSpider(scrapy.Spider):
    name = 'quotes_with_auth'

    def start_requests(self):
        url = 'https://quotes.toscrape.com/login'

        yield scrapy.Request(url, self.login)


    def login(self, response):
        csrf_token = response.xpath('//*[@name="csrf_token"]/@value').get()

        yield scrapy.FormRequest.from_response(
            response,
            formdata={
                'username': 'username',
                'password': 'password',
                'csrf_token': csrf_token
            },
            callback=self.after_login
        )


    def after_login(self, response):
        
        for quote in response.xpath('//div[@class="quote"]'):
            quote_data = {
                'text': quote.xpath('./span[@class="text"]/text()').get(),
                'author': quote.xpath('.//small[@class="author"]/text()').get(),
                'tags': quote.xpath('.//div[@class="tags"]/a[@class="tag"]/text()').getall(),
                'author_link': quote.xpath('.//*[@class="author"]/following-sibling::a[1]/@href').get(),
                'goodreads_author_link': quote.xpath('.//*[@class="author"]/following-sibling::a[2]/@href').get()
            }
            yield response.follow(quote_data['author_link'], callback=self.parse_author, cb_kwargs={'quote_data': quote_data})

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.after_login)


    def parse_author(self, response, quote_data):
        yield {
            **quote_data,
            'author_detail': {
                'name': response.xpath('//h3[@class="author-title"]/text()').get(),
                'birth_date': response.xpath('//*[@class="author-born-date"]/text()').get(),
                'birth_location': response.xpath('//*[@class="author-born-location"]/text()').get(),
                'bio': response.xpath('//*[@class="author-description"]/text()').get(),
            }
        }