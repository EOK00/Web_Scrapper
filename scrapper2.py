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
max_games = 2
num_pages = 2

# 다음 페이지로 이동하는 함수
def go_to_next_page():
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/div[2]/div/div[1]/div/div/p/a[1]'))
        )
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(5)  # 페이지 로드 대기
        return True
    except Exception as e:
        print(f"No more 'Next' button or error clicking 'Next' button: {e}")
        return False

## best_players 정규식 패턴
# best_pattern = r'\d-\d|\d'

# 상세 페이지 데이터 수집
for page in range(num_pages) :
    # 모든 게임의 링크를 먼저 수집
    games = driver.find_elements(By.XPATH, '//tr[contains(@id, "row_")]')[:max_games]
    game_link = []

    for game in games:
        try:
            title_tag = game.find_element(By.CLASS_NAME, 'primary')
            title = title_tag.text.strip()
            link = title_tag.get_attribute('href')
            release = game.find_element(By.CSS_SELECTOR, '.smallerfont.dull').text.strip()
            release_year = re.search(r'\d{4}', release).group()
            geek_rating = game.find_element(By.XPATH, '/html/body/div[2]/main/div[2]/div/div[1]/div/div/div[2]/div[3]/table/tbody/tr[2]/td[4]').text.strip()
            num_voters = game.find_element(By.XPATH, '/html/body/div[2]/main/div[2]/div/div[1]/div/div/div[2]/div[3]/table/tbody/tr[2]/td[6]').text.strip()


            game_link.append({
                'title' : title,
                'release' : release_year,
                'geek_rating' : geek_rating,
                'num_voters' : num_voters,
                'link' : link
            })
        except Exception as e:
            print(f"Error collectiong main page data: {e}")

    for game in game_link:
        driver.get(game['link'])
        driver.implicitly_wait(10)
        
        # 추가 데이터 수집
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
            'Best_Players': best_players,
            'Playing _Time': playing_time,
            'Link': game['link']
        })

    # 다음페이지로 이동
    if not go_to_next_page():
        break

# 웹드라이버 종료
driver.quit()

# 데이터프레임으로 변환 및 저장
df = pd.DataFrame(game_data)
print(df)
df.to_csv('boardgame_data.csv', index=False)
