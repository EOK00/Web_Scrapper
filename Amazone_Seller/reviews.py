import time
import re # 텍스트 가공
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# 웹드라이버 경로 설정
webdriver_service = Service(r'C:\code\chromedriver-win64\chromedriver.exe')  # chromedriver 경로 설정

# 웹드라이버 초기화
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
base_url = "https://www.amazon.com/Kitsch-Strengthening-Shampoo-All-Natural-Moisturizing/product-reviews/B09FB1YXF1/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1"
driver.get(base_url)

# 페이지 로딩 대기
driver.implicitly_wait(10)

# 데이터 셋
review_data = []

# 수집 데이터 개수 제한
num_page = 5

reviews = driver.find_elements(By.XPATH, '//div[contains(@id, "row_")]')#[:max_games_per_page]

# for review in reviews:
#         try:
#             title_tag = review.finde_element(By.CLASS_NAME, '//*[@id="customer_review-R2Z3755K118XL8"]/div[2]')
#             title = title_tag.text.strip()


#             review_data.append({
#                 'Date' : date,
#                 'Title' : title,
#                 'Rating' : rating,


#             })
#         except Exception as e:
#             print(f"Error collectiong main page data: {e}")

title_tag = reviews.find_element(By.CLASS_NAME, '//*[@id="customer_review-R2Z3755K118XL8"]/div[2]')
title = title_tag.text.strip()
date = reviews.find_element(By.TAG_NAME, 'data-hook="review-date"').text.strip()
print(date)
