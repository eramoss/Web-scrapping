import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options




from enum import Enum

class REGION(Enum):
    BR = ".br"  # Brazil
    CA = ".ca"  # Canada
    GB = ".uk"  # United Kingdom
    AU = ".au"  # Australia
    DE = ".de"  # Germany
    FR = ".fr"  # France
    IN = ".in"  # India
    CN = ".cn"  # China

def get_url(search_name, region):
    template = "https://www.amazon.com{}/s?k={}&ref=nb_sb_noss_1"
    search_name = search_name.replace(' ','+')
    url = template.format(region,search_name)
    url += "&page{}"
    return url

def extract_record(item, region):
    a_tag = item.find_all('h2')
    a_tag = a_tag[len(a_tag)-1].find('a')
    description = a_tag.span.text.strip()
    url = 'https://www.amazon.com{}/'
    url = url.format(region)
    url +=  a_tag.get('href')

    try:
        #price
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
    except AttributeError:
        return

    try:
        rating_count = item.find('span', 'a-icon-alt')
        if rating_count:
            rating_count = rating_count.text
    except ArithmeticError:
        rating_count = ''

    result = (description,price,rating_count,url)
    return result

def main(search_name, region=''):
    # Option of web driver
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)

    records = []
    url = get_url(search_name, region)

    for page in range(1, 4):
        driver.get(url.format(page))
        print(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        results = soup.find_all('div', {'data-component-type':"s-search-result"})

        for item in results:
            record = extract_record(item, region)
            if record:
                records.append(record)

    driver.close()


    with open('results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['description', 'price', 'review counting', 'url'])
        writer.writerows(records)

main('caderno', REGION.BR.value)