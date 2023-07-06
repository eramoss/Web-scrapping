import csv
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from urllib.parse import urlparse


# Options of csv that im using
def get_referential_urls(file_path):
    urls = []
    
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            url = row['URL REFERENCIAL']
            urls.append(url)
    
    return urls

csv_file_path = './modelo.csv'
referential_urls = get_referential_urls(csv_file_path)
referential_urls = [line for line in referential_urls if line.strip()]

def get_domain(url):
    # Parse the URL using urlparse
    parsed_url = urlparse(url)

    # Extract the domain from the parsed URL
    domain = parsed_url.netloc

    # Return the domain as a string
    return domain


def get_price_from_amazon(url):
    # Option of web crawler
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tag_with_price = soup.find('span', 'a-offscreen')
    driver.close()
    return tag_with_price

def get_price_from_maximustecidos(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) firefox/80.0.3987.149 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    html_content = response.content
    
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    pattern = r'R\$ ?\d+,\d+'
    tags_with_price = re.findall(pattern, str(soup))
    # maximus has a price in end of prices
    return [tags_with_price[len(tags_with_price) -1]]


def get_price(url):
    if "www.amazon.com" in get_domain(url):
        tag_with_price = get_price_from_amazon(url);
    elif "www.maximustecidos.com" in get_domain(url):
        tag_with_price = get_price_from_maximustecidos(url)
    else:
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) firefox/80.0.3987.149 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        html_content = response.content
        
        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the first tag containing "R$"
        tag_with_price = soup.find(text=lambda text: text and "$" in text)
        
    pattern = r"R\$(?:\s|\\xa0)?([\d,\.]+)"
    tag_with_price = re.findall(pattern, str(tag_with_price))   
    return tag_with_price;


for line in referential_urls:
    price = get_price(line);
    print(price," site: " + get_domain(line))
