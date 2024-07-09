import time
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

base_url = "https://boardgamegeek.com/browse/boardgame"
driver.get(base_url)

# 페이지 로딩 대기
driver.implicitly_wait(10)

# 데이터 저장용 리스트
game_data = []

# 수집 데이터 개수 제한
max_games = 10

# 모든 게임의 링크를 먼저 수집
games = driver.find_elements(By.XPATH, '//tr[@id]')[:max_games]
game_first=[]

for game in games:
    try:
        title_tag = game.find_element(By.CLASS_NAME, 'primary')
        title = title_tag.text.strip()
        released_tag = game.find_element(By.CLASS_NAME, '.smallerfont dull')
        released = released_tag.text.strip()
        geek_rating = game.find_element(By.XPATH, './/td[@class="collection_bggrating"]').text.strip()
        num_voters = game.find_elements(By.XPATH, './/td[@class="collection_bggrating"]')[2].text.strip()

        game_first.append({
            'title': title,
            'released' : released,
            'geek_rating': geek_rating,
            'num_voters': num_voters
        })
    except Exception as e:
        print(f"Error collecting main page data: {e}")

# 각 게임의 세부 페이지로 이동하여 추가 데이터 수집
# for game in game_links:
#     driver.get(game['game_link'])
#     driver.implicitly_wait(10)

#     # 추가 데이터 수집
#     try:
#         players = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//span[contains(@ng-show, 'geekitemctrl.geekitem.data.item.polls.userplayers.totalvotes > 0')]"))
#         ).text
#     except:
#         players = 'N/A'

#     try:
#         min_time = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//span[contains(@ng-if, 'min > 0')]"))
#         ).text
#     except:
#         min_time = 'N/A'

#     try:
#         max_time = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, "//span[contains(@ng-if, 'max>0 & min != max')]"))
#         ).text
#     except:
#         max_time = 'N/A'

    game_data.append({
        'Title': game['title'],
        'Released' : game['released'],
        'Geek Rating': game['geek_rating'],
        'Num Voters': game['num_voters'],
    })

# 웹드라이버 종료
driver.quit()

# 데이터프레임으로 변환 및 저장
df = pd.DataFrame(game_data)
print(df)
df.to_csv('boardgame_data.csv', index=False)
