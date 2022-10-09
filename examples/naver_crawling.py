from navermap_crawler import navermap_crawling
from datetime import datetime
import pytz
import time
import pandas as pd
import numpy as np

"""
구글 및 카카오도 비슷한 로직으로 크롤링을 진행했습니다.
"""

# KST 기준 시간 생성
KST = pytz.timezone('Asia/seoul')

data = pd.read_csv('음식점리스트.csv')
json_address = '구글시트 jSON파일'

# 구글 클라이언트
google_client = gspread.service_account(filename=json_address)

# 시트 내에 가게 번호가 있는 경우 검색 리스트에서 제외
sheet = google_client.open("naver_crawling_raw_v2").worksheet("시트1")
except_number = [int(i) for i in pd.DataFrame(sheet.get_all_values()[1:], columns=sheet.get_all_values()[0])['가게번호'].tolist()]
data = data.loc[(~data['번호'].isin(except_number))]

# 크롤링할 주소
crawl_list = ['경기도 용인시 기흥구 보정동', '경기도 성남시 분당구 서현동', '경기도 성남시 분당구 삼평동',
       '서울특별시 송파구 잠실동', '서울특별시 강남구 역삼동', '서울특별시 강서구 화곡동', '서울특별시 강동구 천호동',
       '경기도 성남시 분당구 정자동']

# 크롤링할 주소 리스트       
df_final = data.loc[(data['주소_시군구'].isin(crawl_list)), :]

init_num = 1

for _, rows in df_final.iterrows():
    # 업데이트를 위해 계속 시트를 열어줘야함.
    sheet = google_client.open("naver_crawling_raw_v2").worksheet("시트1")
    
    # 200회 마다 time_sleep
    if init_num % 200 == 0:
        sleep_second_v1 = np.random.choice([1000, 1100, 1200], 1)[0]
        time.sleep(sleep_second_v1)
    
    # 변수 지정
    row_idx = rows[0]
    store_name_before_search = rows[1]
    lot_number_address = rows[2]
    road_name = rows[3]
    address_sigoongoo = rows[4]
    search_name = rows[5]
    
    store_name, address_all, address_road_name, review_rate, review_cnt = navermap_crawling(search_name=search_name)

    # 주소록 체크
    if address_road_name is lot_number_address or address_road_name is road_name:
        pass
    else:
        sleep_second_v2 = np.random.randint(3, 10, 1)[0]
        time.sleep(sleep_second_v2)        
        continue    
    
    # 집계 시간
    loadingtime = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
    
    # 집계 리스트 만들기
    append_list = [row_idx, store_name, store_name_before_search, address_all, 
                   address_sigoongoo, address_road_name, review_rate, review_cnt, loadingtime]
    
    sheet.append_row(append_list)
    
    init_num += 1