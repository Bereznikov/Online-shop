import asyncio
import json

import aiohttp
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Parser:
    def __init__(self):
        self._section_links = []
        self._section_names = ['ДЕВОЧКИ', 'МАЛЬЧИКИ', 'ДЛЯ МАЛЫШЕЙ', 'ЖЕНЩИНЫ', "МУЖЧИНЫ", "ДЛЯ ДОМА"]
        self.categories = []
        self.result = []
        self.sections = []
        self.id_set = set()
        self.product_id = 1
        self.category_name_set = set()

    @staticmethod
    def making_soup_txt(url):
        ua = UserAgent()
        fake_ua = {'user-agent': ua.random}
        response = requests.get(url=url, headers=fake_ua)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'lxml')

    @staticmethod
    def get_url_sections(soup):
        res = []
        sections = [f'{link["href"]}' for link in soup.find('ul', id='snail-trail-container').find_all('a')]
        for section in sections:
            res.append(section)
        del res[5]  # отсеиваем секции сайта состоящие из повторений продуктов
        res = res[:-4]  # отсеиваем секции сайта состоящие из повторений продуктов
        return res

    @staticmethod
    def summary_categories_check(link):
        if ('Вся ' in link.text) or ('Все ' in link.text) or ('Новинки' in link.text) or (
                'Новые ' in link.text) or ('Всё ' in link.text):
            return True
        else:
            return False

    def women_check(self, url, soup):
        categories_links = []
        categories_names = []
        for link in soup.find_all('div', class_="sidebar-sec col-sm-12 col-md-3 col-lg-12"):
            women_links = link.find_all('a')
            for women_link in women_links:
                if 'Все Дамское белье' in women_link.text:
                    categories_links.append(f'{url[:33]}{women_link["href"][7:]}')
                    categories_names.append(women_link.text)
                elif self.summary_categories_check(women_link):  # проверка на наличие обобщенных категорий
                    continue
                else:
                    categories_links.append(f'{url[:33]}{women_link["href"][7:]}')
                    categories_names.append(women_link.text)
        categories_links = categories_links[:15] + [categories_links[27]] + categories_links[30:]
        categories_names = categories_names[:15] + [categories_names[27]] + categories_names[30:]
        return zip(categories_names, categories_links)

    def kids_check(self, url, soup):
        categories_links = []
        categories_names = []
        link_list = soup.find_all('div', class_='row tablet-rows')[1]
        for link in link_list.find_all('a'):
            if self.summary_categories_check(link):  # проверка на наличие обобщенных категорий
                continue
            else:
                categories_links.append(f'{url[:33]}{link["href"][7:]}')
                categories_names.append(link.text)
        categories_links = categories_links[-6:]
        categories_names = categories_names[-6:]
        return zip(categories_names, categories_links)

    def normal_chek(self, url, soup):
        categories_links = []
        categories_names = []
        for link in soup.find('div', class_='row tablet-rows').find_all('a'):
            if self.summary_categories_check(link):  # проверка на наличие обобщенных категорий
                continue
            else:
                categories_links.append(f'{url[:33]}{link["href"][7:]}')
                categories_names.append(link.text)
        return zip(categories_names, categories_links)

    def get_url_categories(self, url):
        soup = self.making_soup_txt(url)
        if url == 'https://www.nextdirect.com/kz/ru/women':
            res = self.women_check(url, soup)
        elif url == 'https://www.nextdirect.com/kz/ru/baby':
            res = self.kids_check(url, soup)
        else:
            res = self.normal_chek(url, soup)
        return res

    async def get_data(self, session, info_pair, counter, category_pair_id):
        url = info_pair[1]
        for i in range(1, 826):
            pagen_url = url.strip('-0') + '?p=' + str(i)
            async with session.get(url=pagen_url) as response:
                resp = await response.text()
                page_soup = BeautifulSoup(resp, 'lxml')
                items = page_soup.find('div',
                                       "MuiGrid-root MuiGrid-container plp-product-grid-wrapper plp-1s9f1m4").find_all(
                    'div', class_="MuiCardContent-root produc-1ivfcou")
                if items:
                    for item in items:
                        name_id, price, *tale = item.find('a')['aria-label'].split(' | ')
                        good_name = name_id[:name_id.find(' (')]
                        good_id = name_id.rstrip(')').lstrip(' (')[-6:]
                        previous_sib = item.previous_sibling
                        image = previous_sib.find('img')['src']
                        if 'V&A' in name_id:
                            continue
                        if '-' in price or '&' in good_id:
                            price_low = price.split(' - ')[0].strip(' тг').replace(' ', '')
                            good_dict = {
                                'pk': self.product_id,
                                "model": "products.product",
                                'fields': {'name': good_name,
                                           'price': price_low,
                                           'image': image,
                                           "category": category_pair_id,
                                           "section": counter + 1
                                           }
                            }
                        else:
                            good_dict = {
                                'pk': self.product_id,
                                "model": "products.product",
                                'fields': {'name': good_name,
                                           'price': price.strip('тг').replace(' ', ''),
                                           'image': image,
                                           "category": category_pair_id,
                                           "section": counter + 1
                                           }
                            }
                        if good_dict['pk'] not in self.id_set:
                            self.product_id += 1
                            self.result.append(good_dict)
                            self.id_set.add(good_dict['pk'])
                        else:
                            continue
                else:
                    break

    async def main(self):
        counter = 0
        category_pair_id = 0
        ua = UserAgent()
        fake_ua = {'user-agent': ua.random}
        async with aiohttp.ClientSession(headers=fake_ua) as session:
            tasks = []
            for section_link in self._section_links:
                category_names_links = self.get_url_categories(section_link)
                for category_pair in category_names_links:
                    category_name = category_pair[0].strip().upper() + self._section_names[counter]
                    if category_name not in self.category_name_set:
                        task = asyncio.create_task(self.get_data(session, category_pair, counter, category_pair_id))
                        tasks.append(task)
                        category = {
                            "model": "products.productcategory",
                            "pk": category_pair_id,
                            "fields": {
                                "name": category_pair[0].strip().upper(),
                                "section": counter + 1
                            }
                        }
                        self.categories.append(category)
                        self.category_name_set.add(category_name)
                    category_pair_id += 1
                section = {
                    "model": "products.productsection",
                    "pk": counter + 1,
                    "fields": {
                        "name": self._section_names[counter],
                    }
                }
                self.sections.append(section)
                counter += 1
            await asyncio.gather(*tasks)

    def __call__(self, url, *args, **kwargs):
        soup = self.making_soup_txt(url)
        sections = self.get_url_sections(soup)
        self._section_links = sections
        asyncio.run(self.main())


def make_fixtures(result, categories, sections):
    with open('../products/fixtures/products.json', 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)
    with open('../products/fixtures/categories_next.json', 'w', encoding='utf-8') as file:
        json.dump(categories, file, indent=4, ensure_ascii=False)
    with open('../products/fixtures/sections_next.json', 'w', encoding='utf-8') as file:
        json.dump(sections, file, indent=4, ensure_ascii=False)


def main():
    parse_site = Parser()
    parse_site('https://www.nextdirect.com/kz/ru')
    print('Парсинг выполнен')
    make_fixtures(parse_site.result, parse_site.categories, parse_site.sections)
    print('Файлы обновлены')


if __name__ == '__main__':
    main()
