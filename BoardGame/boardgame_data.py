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

base_url = "https://boardgamegeek.com/browse/boardgame"
driver.get(base_url)

# 페이지 로딩 대기
driver.implicitly_wait(10)

# 데이터 저장용 리스트
game_data = []

# 수집 데이터 개수 제한
# max_games_per_page = 5
num_pages=5

# URL을 생성하는 함수
def generate_page_url(base_url, page_number):
    return f"{base_url}/page/{page_number}"

# 보드게임 기본 데이터 수집 함수
def collect_page_data(base_url, page_number):
    page_url = generate_page_url(base_url, page_number)
    driver.get(page_url)
    driver.implicitly_wait(10)
    # 모든 게임의 링크를 먼저 수집
    games = driver.find_elements(By.XPATH, '//tr[contains(@id, "row_")]')#[:max_games_per_page]
    game_link = []

    for game in games:
        try:
            title_tag = game.find_element(By.CLASS_NAME, 'primary')
            title = title_tag.text.strip()
            link = title_tag.get_attribute('href')
            release = game.find_element(By.CSS_SELECTOR, '.smallerfont.dull').text.strip()
            release_year = re.search(r'\d{4}', release).group()
            geek_rating = game.find_element(By.XPATH, './/td[@class="collection_bggrating"][1]').text.strip()
            num_voters = game.find_element(By.XPATH, './/td[@class="collection_bggrating"][3]').text.strip()


            game_link.append({
                'title' : title,
                'release' : release_year,
                'geek_rating' : geek_rating,
                'num_voters' : num_voters,
                'link' : link
            })
        except Exception as e:
            print(f"Error collectiong main page data: {e}")

    return game_link

# 상세 페이지 데이터 수집 함수
def collect_detail_data(game):
    driver.get(game['link'])
    driver.implicitly_wait(10)

    try:
        community_players = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[2]/div/div[1]/div[2]/ng-include/div/ng-include/div/div[2]/div[2]/div[2]/gameplay-module/div/div/ul/li[1]/div[2]/span/button/span[2]"))
        ).text
        community_players = community_players.replace('–', '~')  # '-'를 '~'로 대체
    except:
        best_players = 'N/A'
    
    try:
        best_players = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[2]/div/div[1]/div[2]/ng-include/div/ng-include/div/div[2]/div[2]/div[2]/gameplay-module/div/div/ul/li[1]/div[2]/span/button/span[3]"))
        ).text
        match = re.search(r'\d+–\d+|\d+', best_players)
        best_players = match.group() if match else 'N/A'
        best_players = best_players.replace('–', '~')  # '-'를 '~'로 대체
        # 텍스트 가공 (예: 'Best: 3–4'에서 숫자만 추출)
    except:
        best_players = 'N/A'

    try:
        playing_time = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[2]/div/div[1]/div[2]/ng-include/div/ng-include/div/div[2]/div[2]/div[2]/gameplay-module/div/div/ul/li[2]/div[1]/span/span"))
        ).text
        playing_time = playing_time.replace('–', '~')
    except:
        playing_time = 'N/A'

    game_data.append({
        'Title': game['title'],
        'Release': game['release'],
        'Geek_Rating': game['geek_rating'],
        'Num_Voters': game['num_voters'],
        'Community_Players': community_players,
        'Best_Players': best_players,
        'Playing _Time': playing_time,
        'Link': game['link']
    })

# 페이지를 반복하며 데이터 수집
base_url = "https://boardgamegeek.com/browse/boardgame"
for page_number in range(1,  num_pages + 1):    # 페이지 조정 가능
    game_link = collect_page_data(base_url, page_number)
    for game in game_link:
        collect_detail_data(game)

# 웹드라이버 종료
driver.quit()

# 데이터프레임으로 변환 및 저장
df = pd.DataFrame(game_data)
print(df)
df.to_csv('boardgame_data.csv', index=False)
