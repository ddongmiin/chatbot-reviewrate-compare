from typing import Optional, Tuple
import re
from datetime import datetime
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


def _get_from_driver(*, driver: WebDriver, url: str) -> None:
    driver.get(url)


def _find_element(*, driver: WebDriver, by, value: str):
    # get store id
    try:
        return driver.find_element(by=by, value=value)
    except Exception:
        return None


def _find_element_with_get_attribute(
    *, driver: WebDriver, by, value: str, attribute: str
) -> Optional[str]:
    element = _find_element(driver=driver, by=by, value=value)
    return element.get_attribute(attribute) if element else None


def _find_element_with_text(*, driver: WebDriver, by, value: str) -> Optional[str]:
    element = _find_element(driver=driver, by=by, value=value)
    return element.text if element else None


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
    review_cnt_compile = re.compile(r"(?<=\n).+(?=건)")
    review_cnt = (
        int(review_cnt_compile.search(primitive_review_cnt).group())
        if primitive_review_cnt
        else 0
    )

    return review_rate, review_cnt


def kakaomap_crawling(search_name: str):

    """카카오맵 크롤링

        카카오 지도 데이터 크롤링 하는 함수입니다.

    Args:
        search_name(str): 시 + 구 + 동 + 상호명

    Return:
        address_origin(str): 전체주소
        address_road_name(str): 도로명 주소
        store_name(str): 가게명
        review_rate(float): 평점 결과
        review_cnt(int): 평점 응답 참여 유저수

    Example:
        address_all, address_road_name, store_name, review_rate, review_cnt = kakaomap_crawling("경기도 용인시 기흥구 보정동 백채김치찌개")

    Note:
        박상철님의 블로그 코드를 참조했습니다.
        https://velog.io/@eric2057/Selenium%EC%9D%84-%EC%9D%B4%EC%9A%A9%ED%95%B4-%EC%B9%B4%EC%B9%B4%EC%98%A4%EB%A7%B5-%ED%81%AC%EB%A1%A4%EB%A7%81%ED%95%98%EA%B8%B0
    """

    with webdriver.Chrome(
        "/home/pangyooldonev2/chromedriver", chrome_options=chrome_options
    ) as driver:

        # 카카오맵 url
        kakao_map_search_url = f"https://map.kakao.com/?q={search_name}"
        _get_from_driver(driver=driver, url=kakao_map_search_url)

        url = driver.current_url

        check_value = _find_element_with_text(
            driver=driver, by="xpath", value='//*[@id="info.search.place.list"]/li[1]'
        )

        if check_value is None:
            return "unknown", "unknown", "unknown", 0.0, 0

        # 전체 주소
        address_origin = _find_element_with_text(
            driver=driver,
            by="xpath",
            value='//*[@id="info.search.place.list"]/li[1]/div[5]/div[2]/p[1]',
        )

        # 도로명 주소
        address_road_name = roadname_translate(address_origin)

        # 상호명
        store_name = _find_element_with_text(
            driver=driver,
            by="xpath",
            value='//*[@id="info.search.place.list"]/li[1]/div[3]/strong/a[2]',
        )

        review_rate, review_cnt = _get_review_info(
            driver=driver,
            by="xpath",
            value_rate="//*[@id='info.search.place.list']/li[1]/div[4]/span[1]/em",
            value_cnt="//*[@id='info.search.place.list']/li[1]/div[4]/span[1]",
        )

        return (
            address_origin,
            address_road_name,
            store_name,
            review_rate,
            review_cnt,
            url,
        )
