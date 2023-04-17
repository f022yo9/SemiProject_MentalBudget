#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 19:13:12 2023

@author: f___yo_
"""

# stigma web crawling
from urllib.request import urlopen
from urllib.request import Request
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver

query_list = ['정신과 기록', '정신과 취업', '정신과 불이익']
baseUrl = 'https://www.google.com/search?q='
base = 'https://www.google.com/'

crawled = []

for query in query_list:
    quoteUrl = quote(query)
    url = baseUrl + quoteUrl
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    webpage = urlopen(req)
    source = webpage.read()
    webpage.close()
    
    driver = webdriver.Safari()
    driver.get(url)
    driver.implicitly_wait(7)

    for i in range(1, 41):
        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            v = soup.select('.yuRUbf')

            for j in v:
                print(j.select_one('.LC20lb.DKV0Md').text)
                print()
                crawled.append(j.select_one('.LC20lb.DKV0Md').text)

            next_url = base + soup.select_one(f'a[aria-label="Page {i+1}"]').get('href')
            driver.get(next_url)
            driver.implicitly_wait(3)

        except AttributeError:
            break

    driver.close()

print(crawled)




## WordCloud
from konlpy.tag import Kkma
from wordcloud import WordCloud

kkma = Kkma()

### 1. 단어 추출
nouns_extend = []

for sent in crawled:
    nouns_extend.extend(kkma.nouns(sent))
print()
print(nouns_extend)



### 2. 단어 전처리
from re import match # 숫자 제외 

nouns_count = {} # 단어 카운터 

for noun in nouns_extend: 
    if len(noun) > 1 and not(match('^[0-9]', noun)):
        nouns_count[noun] = nouns_count.get(noun, 0) + 1
        
print(nouns_count)        



### 3. TopN Selecting
from collections import Counter # class 

word_count = Counter(nouns_count)
top30_word = word_count.most_common(30)



### 4. Generate WordCloud
wc = WordCloud(font_path='/Library/Fonts/서울한강 장체L.otf',
          width=500, height=400,
          max_words=100,max_font_size=150,
          background_color='white')


wc_result = wc.generate_from_frequencies(dict(top30_word))

import matplotlib.pyplot as plt 

plt.imshow(wc_result)
plt.axis('off') # 축 눈금 감추기 
plt.show()

