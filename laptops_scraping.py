import bs4 as bs
from urllib.request import urlopen
import datetime
import time
import csv
import pandas as pd

start_time = time.time()

def scrape_and_get_data(url,page):
    #print(f'page: {page}')
    source = urlopen(url).read()
    global soup
    soup = bs.BeautifulSoup(source, 'lxml')
    for i in soup.find_all('div', {'class': 'product-row'}):
        #print(i.find('h2', {'class': 'product-name'}).text.strip())
        name.append(i.find('h2', {'class': 'product-name'}).text.strip())
        brand.append(i.find('a', {'class': 'product-brand'}).text.strip())
        category.append(i.find('p', {'class': 'product-category'}).text.strip())
        reviews.append(i.find('div', {'class': 'stars-rating'}).text.strip())
        rating.append(i.find('a', {'class': 'js-save-keyword js-scroll-by-hash'}).get('title'))
        for j in i.find_all('div', {'class': 'attributes-row'}):
            attribute = j.find('span', {'class': 'attribute-name'}).text.strip()
            value = j.find('span', {'class': 'attribute-value'}).text.strip()
            if attribute == 'Ekran':
                screen.append(value)
            elif attribute == 'Procesor':
                processor.append(value)
            elif attribute == 'Pamięć':
                memory.append(value)
            elif attribute == 'Grafika':
                graphics_card.append(value)                
            elif attribute == 'Dysk':
                disk.append(value)
            elif attribute == 'System operacyjny':
                operating_system.append(value)
        #getting price
        try:
            current_price.append(i.find('div', {'class': 'price-normal selenium-price-normal'}).text.strip())
        except AttributeError:
            current_price.append(i.find('div', {'class': 'price-normal'}).text.strip())            
        # getting old price
        try:
            former_price.append(i.find('div', {'class': 'price-old'}).text.strip())
        except AttributeError:
            former_price.append('')
        # getting delivery type
        if i.find('span', {'class': 'delivery-message-label'}).text.strip() == 'Sprawdź dostępność w sklepach':
            delivery.append('store only')
        else:
            delivery.append('online')
        #page number
        item_page.append(page)
        

#lists to store scraped data, will be used as columns
name, brand, category, reviews, rating, screen, processor, memory = ([] for i in range(8))
graphics_card, disk, operating_system, current_price, former_price, delivery, item_page = ([] for i in range(7))

#first page
main_page = 'https://www.euro.com.pl/laptopy-i-netbooki.bhtml'

#scraping data from first page
scrape_and_get_data(main_page,1)

#Accessing scraped first page to get the number of pages and scrape thrugh them
pages = [int(i.text.strip()) for i in soup.find_all('a', {'class': 'paging-number'})]
max_page = max(pages)
max_page        

#scraping pages from 2 to last
for page in range(2,max_page+1):
    page_address = f'https://www.euro.com.pl/laptopy-i-netbooki,strona-{page}.bhtml'
    scrape_and_get_data(page_address,page)
    

#new column with date
date_now = [datetime.datetime.now().strftime("%m/%d/%Y %H:%M") for i in range(len(name))]        

#zipping all the lists together
base_lists = zip(date_now, name, brand, category, reviews, rating, screen, processor
                     , memory, graphics_card, disk, operating_system, current_price, former_price
                     , delivery, item_page)

#saving all the data to a csv file
with open('laptops_scraped.csv', 'a+', newline='', encoding='UTF8') as f:
    writer = csv.writer(f)
    #writer.writerow(col_names)
    writer.writerows(base_lists)
    
print("Script executed in %s seconds" % (time.time() - start_time))
