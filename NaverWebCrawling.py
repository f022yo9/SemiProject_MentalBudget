#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 18:22:14 2023

@author: f___yo_
"""
import requests
from bs4 import BeautifulSoup
import time
import csv
from tqdm import tqdm
from collections import Counter
from konlpy.tag import Kkma
from wordcloud import WordCloud
import matplotlib.pyplot as plt




# 네이버 뉴스 크롤링: 코로나 블루, 코로나 우울
def make_naver_news_search_url(query, start_date, end_date, page):
    base_url = "https://search.naver.com/search.naver"
    params = {
        "where": "news",
        "query": query,
        "sm": "tab_opt",
        "sort": "0",
        "photo": "0",
        "field": "0",
        "pd": "3",
        "ds": start_date,
        "de": end_date,
        "start": (page - 1) * 10 + 1,
    }
    return requests.get(base_url, params=params).url


def crawl_naver_news(query, start_date, end_date, max_count=1000):
    page = 1
    news_list = []

    with tqdm(desc="Crawling news", unit="page", dynamic_ncols=True, position=0) as progress_bar:
        while len(news_list) < max_count:
            url = make_naver_news_search_url(query, start_date, end_date, page)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            news_items = soup.select(".news_wrap.api_ani_send")

            if not news_items:
                break

            for item in news_items:
                title = item.select_one(".news_tit").text
                link = item.select_one(".news_tit")['href']
                press = item.select_one(".info.press").text

                news_list.append({
                    "title": title,
                    "link": link,
                    "press": press,
                })

                if len(news_list) >= max_count:
                    break

            page += 1
            progress_bar.update(1)
            time.sleep(0.45)

    return news_list[:max_count]

def read_titles_from_csv(filename):
    titles = []
    with open(filename, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            titles.append(row["title"])
    return titles

def tokenize_titles(titles):
    kkma = Kkma()  # Kkma 형태소 분석기를 사용
    tokens = []
    for title in titles:
        tokens.extend(kkma.nouns(title))  # Kkma의 nouns 메서드를 사용해 명사를 추출
    return tokens

def create_wordcloud(tokens, top_n):
    counter = Counter(tokens)
    most_common = counter.most_common(top_n)
    wc = WordCloud(font_path='/Library/Fonts/서울한강 장체L.otf', background_color='white', width=800, height=800)
    wc.generate_from_frequencies(dict(most_common))

    plt.figure(figsize=(10, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('wordcloud.png')
    plt.show()
    
def count_related_words(tokens, related_words):
    count = 0
    for token in tokens:
        if token in related_words:
            count += 1
    return count

def main():
    queries = ["코로나 블루", "코로나 우울증"]
    start_date = "2020.01.01"
    end_date = "2021.12.31"

    for query in queries:
        news_list = crawl_naver_news(query, start_date, end_date, max_count=10000)

        with open(f"{query}_naver_news.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["title", "link", "press"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for news in news_list:
                writer.writerow(news)

        titles = read_titles_from_csv(f"{query}_naver_news.csv")
        tokens = tokenize_titles(titles)
        create_wordcloud(tokens, top_n=30)

        related_words = ['우울감', '우울']
        related_count = count_related_words(tokens, related_words)
        print(f"'{query}' 검색어와 관련된 우울감과 우울 단어가 {related_count}회 검색되었습니다.")

