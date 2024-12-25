import asyncio
import json
import time

from asyncio import sleep

from selenium.webdriver.common.by import By
import undetected_chromedriver as undetect_driver

from bs4 import BeautifulSoup


class Card:
    def __init__(self, data: dict):
        self.__data = data

        for key, value in data.items():
            self.__setattr__('__' + key, value)
            self.__setattr__(key, getattr(self, '__' + key))

    def get_json(self):
        return self.__data

    def __str__(self):

        string = ''
        for key, value in self.__data.items():
            string += f'{key}: {value}\n'

        return string


class Parser:

    def __init__(self, search_text: str, sorting: str = "score", path_to_dir: str = './', count_of_cards: int = 10,
                 offset: int = 0, headless: bool = False):
        self.search_text = search_text

        if sorting in ('score', 'new', 'price', 'price_desc', 'discount', 'rating'):
            self.sorting = sorting
        else:
            self.sorting = 'score'

        self.count = count_of_cards
        self.offset = offset

        options = undetect_driver.ChromeOptions()

        if not path_to_dir[-1] in '\/':
            path_to_dir += '/'

        self.path_to_dir = path_to_dir
        self.driver = undetect_driver.Chrome(options=options, headless=headless)

        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {'userAgent': user_agent})

    def __get_cards_links(self):
        url = f"https://ozon.ru/search/?sorting={self.sorting}&text={self.search_text}"
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        time.sleep(0.7)
        find_elements = self.driver.find_elements(By.CLASS_NAME, "tile-clickable-element.x7i_23")
        while len(self.driver.find_elements(By.CLASS_NAME, "tile-clickable-element.x7i_23")) < self.count + self.offset:
            self.page_down()
            time.sleep(1)
            find_elements = self.driver.find_elements(By.CLASS_NAME, "tile-clickable-element.x7i_23")

        find_elements = find_elements[self.offset:self.count + self.offset]
        try:
            cards = tuple(set([element.get_attribute("href") for element in find_elements]))

            if cards:
                print('[+++] Found cards:', cards)
            else:
                raise Exception('No cards found')
        except Exception as e:
            print('[---] Error while searching for cards')
            raise e

        card_urls = dict()
        for i, url in enumerate(cards):
            card_urls[i] = url

        return card_urls

    def parse(self):
        self.card_urls = self.__get_cards_links()
        self.collect_data = [self.__parse_card(url) for url in self.card_urls.values()]
        self.collect_data = [card.get_json() for card in self.collect_data]

        self.driver.quit()

        return self.collect_data

    def page_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def __parse_card(self, card_link: str) -> Card:

        self.driver.get(card_link)
        self.driver.implicitly_wait(15)
        time.sleep(0.8)

        self.driver.save_screenshot('test.png')

        html = self.driver.page_source

        soup = BeautifulSoup(html, 'lxml')

        # title and card_id
        title = soup.find(
            'h1',
            attrs={'class': 'x0l_27 tsHeadline550Medium'}).text.strip()
        card_id = int(
            soup.find('button',
                      attrs={'class': 'rj9_27 r9j_27 ga121-a undefined ga121-a5'}).text.split(': ')[-1])
        # rating
        rating_text = soup.find('div', attrs={'class': 'ga121-a2 tsBodyControl500Medium'}).text.strip()
        if '•' in rating_text:
            rating = float(rating_text.split()[0])
            count_of_reviews = int(rating_text.split()[-2])
        else:
            rating = None
            count_of_reviews = 0
        # desc
        description_element = soup.find('div', attrs={'class': 'RA-a1'})
        if description_element:
            description = description_element.text.strip()
        else:
            description = None
        # collect prices
        price = soup.find('span', attrs={'class': 'l4w_27 l5w_27 l3w_27 wl4_27'}).text.strip()
        price = int(''.join(price[:-1].split()))
        discounted_price_element = soup.find('span', attrs={'class': 'w4l_27 lw5_27 w8l_27'})
        ozon_card_price_element = soup.find('span', attrs={'class': 'lw0_27 v8l_27'})
        if discounted_price_element:
            discounted_price = discounted_price_element.text
            discounted_price = int(''.join(discounted_price[:-1].split()))
        else:
            discounted_price_element = soup.find('span', attrs={'class': 'w4l_27 lw5_27 l9w_27'})
            if discounted_price_element:
                discounted_price = discounted_price_element.text
                discounted_price = int(''.join(discounted_price[:-1].split()))
            else:
                discounted_price = None

        if ozon_card_price_element:
            ozon_card_price = ozon_card_price_element.text
            ozon_card_price = int(''.join(ozon_card_price[:-1].split()))
        else:
            ozon_card_price = None

        # deliver

        deliver_date_element = soup.find('span', attrs={'class': 'q6b06-a1'})
        if deliver_date_element:
            deliver_date = deliver_date_element.text.strip()
        else:
            deliver_date = None
        # seller info
        seller_element = soup.find('a', attrs={'class': 'k5l_27'})
        seller_name = seller_element.text
        seller_url = 'https://ozon.ru' + seller_element.get('href')
        # main photo

        main_photo = soup.find('img', attrs={'class': 'w0j_27 jw1_27 b933-a'})
        if main_photo:
            main_photo = main_photo.get('src')
        # collect data to dict

        product_card = dict()

        product_card['title'] = title
        product_card['main_photo'] = main_photo
        product_card['ozon_card_price'] = ozon_card_price
        product_card['discounted_price'] = discounted_price
        product_card['price'] = price
        product_card['rating'] = rating
        product_card['count_of_reviews'] = count_of_reviews
        product_card['description'] = description
        product_card['deliver_date'] = deliver_date
        product_card['seller_name'] = seller_name
        product_card['seller_url'] = seller_url
        product_card['url'] = card_link

        card = Card(product_card)

        return card

    def dump_json_files(self, path_to_dir=None):

        if not path_to_dir:
            path_to_dir = self.path_to_dir

        if self.card_urls:
            with open(path_to_dir + f'{self.search_text}_card_urls.json', 'w') as f:
                json.dump(self.card_urls, f, indent=4, ensure_ascii=False)

        if self.collect_data:
            with open(path_to_dir + f'{self.search_text}_collect_data.json', 'w') as f:
                json.dump(self.collect_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = Parser(search_text='Лололошка', sorting='rating', path_to_dir='Lolowka', count_of_cards=10, offset=0,
                    headless=True)
    parser.parse()
    parser.dump_json_files()
