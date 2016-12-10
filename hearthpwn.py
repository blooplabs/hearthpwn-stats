import scrapy
import re

class HearthPwnSpider(scrapy.Spider):
  name = 'hearthpwn'
  start_urls = ['http://www.hearthpwn.com/cards?display=1&filter-dust-cost-op=1&filter-dust-cost-val=0&filter-rarity=32&filter-show-standard=y']
  # download_delay = 0.5


  def parse(self, response):
    yield scrapy.Request('http://www.hearthpwn.com/cards?display=1&filter-dust-cost-op=1&filter-dust-cost-val=0&filter-rarity=32&filter-show-standard=y', callback=self.parse_listing)

  def parse_listing(self, response):
    # scrape all cards
    for card in response.css("table.listing tbody a[href*='cards']::attr(href)"):
      card_url = response.urljoin(card.extract())
      yield scrapy.Request(card_url, callback=self.parse_card)

    # [debug] scrape one card  
    '''
    card = response.css("table.listing tbody a[href*='cards']::attr(href)")
    card_url = response.urljoin(card.extract()[0])
    yield scrapy.Request(card_url, callback=self.parse_card)
    '''

  def parse_card(self, response):
    infobox = response.css(".card-details .infobox::text").extract()
    usage = list(filter(lambda x: "Used in" in x, infobox))
    usage = re.sub("\s+", " ", usage[0]).strip()
    
    usage_tokens = usage.split(" ")
    usage_pct = usage_tokens[2]
    usage_class = usage_tokens[4]

    yield {
      'title' : response.css(".card-details .caption::text").extract()[0],
      'set'   : response.css(".card-details .infobox li a[href*='filter-set']::text").extract()[0],
      'usage' : usage,
      "usage_pct" : usage_pct,
      "usage_class" : usage_class,

    }

