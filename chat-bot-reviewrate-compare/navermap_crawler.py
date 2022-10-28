from typing import Optional, Tuple
import re
from roadname_translate import roadname_translate

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


import time
import numpy as np

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 드라이버로 부터 URL정보를 실행합니다.
def _get_from_driver(*, driver: WebDriver, url: str) -> None:
    driver.get(url)


# element를 찾습니다.
def _find_element(*, driver: WebDriver, by, value: str):
    # get store id
    try:
        return driver.find_element(by=by, value=value)
    except Exception:
        return None


# 특성에 따라 엘리먼트를 찾습니다.
def _find_element_with_get_attribute(
    *, driver: WebDriver, by, value: str, attribute: str
) -> Optional[str]:
    element = _find_element(driver=driver, by=by, value=value)
    return element.get_attribute(attribute) if element else None


# 엘리먼트의 텍스트 정보를 얻어옵니다.
def _find_element_with_text(*, driver: WebDriver, by, value: str) -> Optional[str]:
    element = _find_element(driver=driver, by=by, value=value)
    return element.text if element else None


# 네이버 지도의 엘리먼트 구조에 따라 주소만 가져옵니다.
def _get_address(*, driver: WebDriver, by, value: str) -> Tuple[str, str]:
    address_origin = _find_element_with_text(driver=driver, by=by, value=value)
    # 주소만 가져오는 정규식
    address_compile_all = re.compile("(?<=\n).+")

    address_all = address_compile_all.search(address_origin).group()
    address_road_name = roadname_translate(address_all)
    return address_all, address_road_name


# 리뷰 내에서 평점과 리뷰 수 정보를 가져옵니다.
def _get_review_info(
    *, driver: WebDriver, by, value_rate: str, value_cnt: str
) -> Tuple[str, str]:
    primitive_review_rate = _find_element_with_text(
        driver=driver, by=by, value=value_rate
    )
    review_rate = float(primitive_review_rate) if primitive_review_rate else 0
    primitive_review_cnt = _find_element_with_text(
        driver=driver, by=by, value=value_cnt
    )
    review_cnt_compile = re.compile(".+(?=개)")
    review_cnt = (
        int(review_cnt_compile.search(primitive_review_cnt).group().replace(",", ""))
        if primitive_review_cnt
        else 0
    )

    return review_rate, review_cnt


def navermap_crawling(search_name: str):

    """네이버 크롤링

        네이버 지도 데이터 크롤링 하는 함수입니다. 21년 10월 이후 데이터만 확인할 수 있습니다.

    Args:
        search_name(str): 시 + 구 + 동 + 상호명

    Return:
        address_all(str): 전체주소
        address_road_name(str): 도로명 주소
        store_name(str): 가게명
        review_rate(float): 평점 결과
        review_cnt(int): 평점 응답 참여 유저수

    Example:
        address_all, address_road_name, store_name, review_rate, review_cnt = navermap_crawling("경기도 용인시 기흥구 보정동 백채김치찌개")

    Note:
        김문과의 데이터 이야기 블로그를 참고했습니다.
        https://data101.oopy.io/recommendation-engine-cosine-similarity-naver-version-code-sharing
    """

    with webdriver.Chrome(
        "/home/pangyooldonev2/chromedriver", chrome_options=chrome_options
    ) as driver:

        # naver v5 map search_url
        naver_map_search_url = f"https://m.map.naver.com/search2/search.naver?query={search_name}&sm=hty&style=v5"
        _get_from_driver(driver=driver, url=naver_map_search_url)
        time.sleep(0.5)

        url = driver.current_url

        store_id = _find_element_with_get_attribute(
            driver=driver,
            by=By.CSS_SELECTOR,
            value="#ct > div.search_listview._content._ctList > ul > li:nth-child(1) > div.item_info > a.a_item.a_item_distance._linkSiteview",
            attribute="data-cid",
        )

        if store_id is None:
            return "unknown", "unknown", "unknown", 0.0, 0

        store_name = _find_element_with_text(
            driver=driver,
            by="xpath",
            value="//*[@id=/'ct']/div[2]/ul/li/div[1]/a[2]/div/strong",
        )

        if store_name is None:
            store_name = _find_element_with_text(
                driver=driver,
                by="xpath",
                value="//*[@id='ct']/div[2]/ul/li/div[1]/a[2]/div/strong",
            )

        if store_name is None:
            return "unknown", "unknown", "unknown", 0.0, 0

        address_all, address_road_name = _get_address(
            driver=driver,
            by="xpath",
            value="//*[@id='ct']/div[2]/ul/li/div[1]/div[1]/div/a",
        )

        # 새 url 획득 - 네이버 평점 리뷰의 경우, 리뷰 아이콘을 클릭했을 때 나타나는 url을 입력 / 21년 10월 이전 리뷰 결과에 대해서만 확인 가능
        visitor_url = f"https://m.place.naver.com/restaurant/{store_id}/review/visitor"
        _get_from_driver(driver=driver, url=visitor_url)
        time.sleep(0.5)
        review_rate, review_cnt = _get_review_info(
            driver=driver,
            by="xpath",
            value_rate="//*[@id='app-root']/div/div/div/div[7]/div[2]/div[1]/div/div/div[3]/span[1]",
            value_cnt="//*[@id='app-root']/div/div/div/div[7]/div[2]/div[1]/div/div/div[3]/span[2]",
        )

        return address_all, address_road_name, store_name, review_rate, review_cnt, url
