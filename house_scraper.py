## importing Beatiful Soup, requests and panda

from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging

## importing headers

my_headers = {
    
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'\
        'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'referer': 'https://www.idealista.pt/en/comprar-casas/lisboa/?ordem=atualizado-desc',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '\
            'Chrome/91.0.4472.77 Safari/537.36'
    }

## Base url for the requests

base_url = "https://www.idealista.pt/comprar-casas/lisboa/"

## Creating empty dictionary

regions = {
    'campolide': [],
    'lumiar': [],
    'sao-domingos-de-benfica': []
  }

## Website Scraper. It will scan each page and creat a soup, them it will look on the soup for the 'next page' button. If it finds it, index++ and goes for the next page. If it doesnt, break the loop and go for the next region

def get_regions(regions):
  print("Starting extraction")
  index = 1
  for region in regions:
    page = requests.get(f'{base_url}{region}/', headers=my_headers)
    print(page)
    print(f'{base_url}{region}/')
    soup = BeautifulSoup(page.content, 'html.parser')
    regions[region].append(soup)
    while page.status_code == 200:
      print('-------------------------------------------------------------------------------------------------------------------------------------------------')
      page = requests.get(f'{base_url}{region}/pagina-{index}', headers=my_headers)
      print(page)
      print(f'{base_url}{region}/pagina-{index}')
      soup = BeautifulSoup(page.content, 'html.parser')
      regions[region].append(soup)
      if soup.find_all('a', {"class": "icon-arrow-right-after"}):
        index += 1
      else:
        index = 1
        break
  return regions

## just a string transformer (helper function)

def transform_string(string):
  if string == 'lumiar':
    return('Lumiar')
  elif string == 'sao-domingos-de-benfica':
    return('São Domingo de Benfica')
  else:
     return('Campolide')

## This function gets HTML data and extract into a list of dictionaries

def store_data(final_list, regions, region):
  print('-------------------------------------------------------------')
  print(f'Fetching data from HTML for {region}')
  for page in regions[region]:
    anouncements = page.find('main').find('section').find_all("div", class_="item-info-container")
    for anouncement in anouncements:
      spans = anouncement.find("div", class_="item-detail-char").find_all("span")
      link = anouncement.find("a", class_="item-link")['href']
      price = anouncement.find("div", class_="price-row").span.get_text()
      house_info = {}
      try:
        house_info['Title'] = anouncement.find("a", class_="item-link")['title']
      except Exception as Argument:
        house_info['Title'] = '-'
        logging.exception("Error occured while fetching 'Title' from HTML")
      try:
        house_info['Region'] = transform_string(region)
      except Exception as Argument:
        house_info['Region'] = '-'
        logging.exception("Error occured while fetching 'Region' from HTML")
      try:
        house_info['Link'] = f'https://www.idealista.pt{link}'
      except Exception as Argument:
        house_info['Link'] = '-'
        logging.exception("Error occured while fetching 'Region' from HTML")
      try:
        house_info['Typology'] = anouncement.find("div", class_="item-detail-char").find("span", class_="item-detail").get_text()
      except Exception as Argument:
        house_info['Typology'] = '-'
        logging.exception("Error occured while fetching 'Typology' from HTML") 
      try:
        house_info['House price'] = int(float(price[:-1].replace('.', '')))
      except Exception as Argument:
        house_info['House price'] = None
        logging.exception("Error occured while fetching 'House Price' from HTML") 
      try:
        house_info['House area'] = spans[1].get_text()          
      except Exception as Argument:
        logging.exception("Error occured while fetching 'House area' from HTML")
        house_info['House area'] = '-'
      try:
        house_info['House floor'] = spans[-1].get_text()
      except Exception as Argument:
        logging.exception("Error occured while fetching 'House floor' from HTML")
        house_info['House floor'] = '-'
      try:
        house_info['Seller contact'] = anouncement.find("div", class_="item-toolbar").find("span", class_="icon-phone item-not-clickable-phone").get_text()
      except Exception as Argument:
        logging.exception("Error occured while fetching 'Seller contact' from HTML")
        house_info['Seller contact'] = '-'
      final_list.append(house_info)

## Process regions one by one

def process_regions(regions):
  final_list = []
  store_data(final_list, regions, 'campolide')    
  store_data(final_list, regions, 'lumiar')
  store_data(final_list, regions, 'sao-domingos-de-benfica')
  df = pd.DataFrame(final_list)
  return (df)

## Main function

def main():
  extracted = get_regions(regions)
  data_frame = process_regions(extracted)
  data_frame.to_excel('houses_data.xlsx')
  print('------------------------------------------------------------')
  print('Excel file created.')

if __name__ == "__main__":
    main()