"""Contains HearthPwnSpider class"""

import re
import scrapy

class HearthPwnSpider(scrapy.Spider):
    """Spider for grabbing Hearthstone card usage stats from hearthpwn.com"""

    name = 'hearthpwn'
    url_base = 'http://www.hearthpwn.com/'
    url_path_listing = ('cards?display=1&filter-dust-cost-op=1&filter-dust-cost-val=0'
                        '&filter-show-standard=y')
    url_filter_rarity = '&filter-rarity=58'
    start_urls = [url_base + url_path_listing + url_filter_rarity]
    download_delay = 0.1

    def parse(self, response):
        """Issue a dummy request; hearthpwn doesn't respect url filter on first load"""
        yield scrapy.Request(self.url_base + self.url_path_listing + self.url_filter_rarity,
                             callback=self.parse_listing)

        # debug
        #yield scrapy.Request('http://www.hearthpwn.com/cards/49622-kazakus',
        #                     callback=self.parse_card)

    def parse_listing(self, response):
        """Parse the card listings page"""

        # scrape all cards
        for card in response.css('table.listing tbody a[href*="cards"]::attr(href)'):
            card_url = response.urljoin(card.extract())
            yield scrapy.Request(card_url, callback=self.parse_card)

            # debug
            # break

        # parse the next page (if it exists)
        next_page_links = response.css('li.b-pagination-item a[rel*="next"]::attr(href)').extract()
        if len(next_page_links) > 0:
            yield scrapy.Request(self.url_base + next_page_links[0], callback=self.parse_listing)

    def parse_card(self, response):
        """Parse the card details page"""
        output = {
            'title': response.css('.card-details .caption::text').extract()[0],
            'class': 'all',
        }

        infobox = response.css('.card-details .infobox')
        infobox = infobox.css('::text').extract()

        for i, infobox_line in enumerate(infobox):
            if 'Type:' in infobox_line:
                output['type'] = infobox[i+1].strip()
            if 'Rarity:' in infobox_line:
                output['rarity'] = infobox[i+1].strip()
            if 'Set:' in infobox_line:
                output['set'] = infobox[i+1].strip()
            if 'Class:' in infobox_line:
                output['class'] = infobox[i+1].strip()
            if 'Classes:' in infobox_line:
                output['class'] = 'Multi'
            if 'Used in' in infobox_line:
                usage = re.sub(r'\s+', ' ', infobox_line).strip()
                usage_tokens = usage.split(' ')
                output['usage_pct'] = usage_tokens[2]

        yield output
