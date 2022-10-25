from navermap_crawler import navermap_crawling
from kakaomap_crawler import kakaomap_crawling
from googlemap_api import googlemap_api
import telegram
from telegram.ext import *
from telegram import ParseMode
import gspread
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import dataframe_image as dfi

from multiprocessing import Process, Queue
import time

from datetime import datetime
import pytz
from pyvirtualdisplay import Display

plt.rc("font", family="NanumGothic")

json_address = "구글스프레드시트 JSON 키파일"
display = Display(visible=0, size=(1920, 1080))
display.start()

# 코드 실행 시간을 가져옵니다. KST기준
def _get_loadingtime():
    KST = pytz.timezone("Asia/seoul")
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")


# 구글 클라이언트를 생성합니다.
def _get_google_client(json_address: str):
    return gspread.service_account(filename=json_address)


# 구글 시트를 판다스 데이터프레임으로 만들어 줍니다.
def _sheet_to_df(*, json_address: str, file_name: str, sheet_name="시트1"):
    google_client = _get_google_client(json_address=json_address)
    sheet = google_client.open(file_name).worksheet(sheet_name)
    return pd.DataFrame(sheet.get_all_values()[1:], columns=sheet.get_all_values()[0])


# 기존 시트에 가게 정보가 있는지 체크합니다.
def _check_store_exist(
    *, json_address: str, file_name: str, sheet_name="시트1", check_value: str
) -> bool:
    sheet_df = _sheet_to_df(
        json_address=json_address, file_name=file_name, sheet_name=sheet_name
    )
    return check_value in sheet_df["가게명"].tolist()


# 시트를 업데이트 합니다.
def _sheet_update(
    *, json_address: str, file_name: str, sheet_name="시트1", update_list: list
):
    google_client = _get_google_client(json_address=json_address)
    sheet = google_client.open(file_name).worksheet(sheet_name)
    sheet.append_row(update_list + [_get_loadingtime()])


# 식당이 상위 몇%인지 출력합니다.
def _get_percentile_value(csv_name: str, get_value):
    temp_df = pd.DataFrame(
        pd.read_csv(csv_name).iloc[:, 0].tolist() + [get_value], columns=["temp_col"]
    )
    temp_df["rank_pct"] = temp_df["temp_col"].rank(pct=True, ascending=False)
    percentile = temp_df.loc[(temp_df["temp_col"] == get_value), "rank_pct"].tolist()[0]
    cnt = temp_df.shape[0]
    return cnt, percentile


# 카카오맵에서 정보를 얻어옵니다.
def get_info_from_kakao(search_word: str):
    kakao_list = ["카카오맵"] + list(kakaomap_crawling(search_name=search_word))
    url = kakao_list[-1]
    review_cnt = kakao_list[-2]
    review_rate = kakao_list[-3]
    address = kakao_list[1]
    platform = kakao_list[0]
    store_name = kakao_list[3]

    # 리뷰가 없으면 패스합니다.
    if review_cnt == 0 or review_rate == 0:
        return None
    else:
        pass
    cnt, percentile_review_cnt = _get_percentile_value(
        csv_name="kakao_review_table_latest_review_cnt.csv", get_value=review_cnt
    )
    _, percentile_review_rate = _get_percentile_value(
        csv_name="kakao_review_table_latest_review_rate.csv", get_value=review_rate
    )
    info_list = [
        platform,
        cnt,
        address,
        review_rate,
        percentile_review_rate,
        review_cnt,
        percentile_review_cnt,
        url,
    ]

    # 만약 버퍼테이블에 검색 결과가 없는 경우 버퍼테이블에 검색 결과를 추가합니다.
    if (
        _check_store_exist(
            json_address=json_address, file_name="buffer", check_value=store_name
        )
        == False
    ):
        _sheet_update(
            json_address=json_address, file_name="buffer", update_list=kakao_list
        )

    return info_list


# 네이버 지도에서 정보를 얻어옵니다.
def get_info_from_naver(search_word: str):
    naver_list = ["네이버지도"] + list(navermap_crawling(search_name=search_word))
    url = naver_list[-1]
    review_cnt = naver_list[-2]
    review_rate = naver_list[-3]
    address = naver_list[1]
    platform = naver_list[0]
    store_name = naver_list[3]

    if review_cnt == 0 or review_rate == 0:
        return None
    else:
        pass
    cnt, percentile_review_cnt = _get_percentile_value(
        csv_name="naver_review_table_latest_review_cnt.csv", get_value=review_cnt
    )
    _, percentile_review_rate = _get_percentile_value(
        csv_name="naver_review_table_latest_review_rate.csv", get_value=review_rate
    )
    info_list = [
        platform,
        cnt,
        address,
        review_rate,
        percentile_review_rate,
        review_cnt,
        percentile_review_cnt,
        url,
    ]

    if (
        _check_store_exist(
            json_address=json_address, file_name="buffer", check_value=store_name
        )
        == False
    ):
        _sheet_update(
            json_address=json_address, file_name="buffer", update_list=naver_list
        )

    return info_list


# 구글 지도에서 정보를 얻어옵니다.
def get_info_from_google(search_word: str):

    google_list = ["구글맵"] + list(googlemap_api(search_name=search_word))
    url = google_list[-1]
    review_cnt = google_list[-2]
    review_rate = google_list[-3]
    address = google_list[1]
    platform = google_list[0]
    store_name = google_list[3]

    if review_cnt == 0 or review_rate == 0:
        return None
    else:
        pass
    cnt, percentile_review_cnt = _get_percentile_value(
        csv_name="google_review_table_latest_review_cnt.csv", get_value=review_cnt
    )
    _, percentile_review_rate = _get_percentile_value(
        csv_name="google_review_table_latest_review_rate.csv", get_value=review_rate
    )
    info_list = [
        platform,
        cnt,
        address,
        review_rate,
        percentile_review_rate,
        review_cnt,
        percentile_review_cnt,
        url,
    ]

    if (
        _check_store_exist(
            json_address=json_address, file_name="buffer", check_value=store_name
        )
        == False
    ):
        _sheet_update(
            json_address=json_address, file_name="buffer", update_list=google_list
        )

    return info_list


# 챗봇 행동함수 - /start 입력시 어떤 행동을 할지 정의합니다.
def _start_message(update, context):
    start_message = """안녕하세요. 식당 평점 비교 봇입니다.
사용법은 아래와 같습니다. 
</search OO시 00구 00동 00식당>
    """
    update.message.reply_text(start_message)


# 메인 메시지 - 식당 검색 결과 핸들링 함수
def _message_handler(update, context):
    search_word = update.message.text
    # /search까지 한번에 검색어로 받기 때문에 제거해 주어야 합니다.
    search_word_replace = search_word.replace("/search ", "")
    update.message.reply_text(text=f"{search_word_replace} 에 대한 검색을 시작합니다.")
    kakao_list = get_info_from_kakao(search_word_replace)
    naver_list = get_info_from_naver(search_word_replace)
    google_list = get_info_from_google(search_word_replace)

    info_list = []
    url_list = []
    for val in [kakao_list, naver_list, google_list]:
        if val is not None:
            info_list.append(val[:-1])
            url_list.append(val[-1])

    # 각 맵에서 얻은 정보를 데이터 프레임으로 만들어줍니다.
    sample_df = pd.DataFrame(
        data=info_list,
        columns=["플랫폼", "가게수(리뷰수10개이상)", "주소", "평점", "평점-상위N%", "리뷰수", "리뷰수-상위N%"],
    )
    sample_df = sample_df.set_index("플랫폼")
    sample_df.index.name = None

    # 수집 결과가 없는 경우 수집 결과가 없다고 노출합니다.
    if len(info_list) == 0:
        update.message.reply_text("카카오맵/네이버지도/구글맵 3곳 모두 리뷰 결과를 찾지 못했습니다.")
    else:
        # 데이터프레임 형태로 내보낼 수 있도록 pandas style을 이용해 튜닝했습니다.
        df_with_style = (
            sample_df.style.format(
                {
                    "평점-상위N%": "{:,.1%}".format,
                    "리뷰수-상위N%": "{:,.1%}".format,
                    "평점": "{:,.3}".format,
                }
            )
            .set_properties(**{"text-align": "left", "width": "80px"})
            .bar(
                subset=["평점-상위N%", "리뷰수-상위N%"],
                width=100,
                align="left",
                vmin=1,
                vmax=0,
                color="mistyrose",
            )
            .set_table_styles(
                [
                    {
                        "selector": "thead",
                        "props": [
                            ("background-color", "dodgerblue"),
                            ("color", "white"),
                        ],
                    },
                    {
                        "selector": "tbody td",
                        "props": [("border", "1px solid grey"), ("font-size", "20px")],
                    },
                    {
                        "selector": "th",
                        "props": [("border", "1px solid grey"), ("font-size", "20px")],
                    },
                ]
            )
        )
        # 챗봇으로 이미지를 전송합니다.
        dfi.export(df_with_style, "search_img_to_bot.png")
        update.message.reply_photo(
            photo=open("search_img_to_bot.png", "rb"),
            caption=f"{search_word_replace}에 대한 검색 결과입니다.",
        )

        for url, platform in zip(url_list, sample_df.index.tolist()):
            update.message.reply_text(
                text=f"""<a href='{url}'>{search_word_replace} {platform}</a>""",
                parse_mode=telegram.ParseMode.HTML,
            )

        update.message.reply_text(text="다음 요청 수행까지 5초 간의 대기 시간이 있습니다.")


# 에러메시지 헨들링 함수입니다.
def _error(update, context):
    print(f"다음과 같은 에러가 발생했습니다. {context.error}")


# 챗봇 실행 함수입니다.
def search_bot(token: str):
    # 업데이트 클래스 생성
    updater = Updater(token=token, use_context=True)
    # dispatcher - 행동 함수 실행
    dispatcher = updater.dispatcher

    # 행동함수 추가
    dispacher.add_handler(CommandHandler("start", _start_message))
    dispacher.add_handler(CommandHandler("search", _message_handler))
    dispacher.add_error_handler(_error)

    # 풀링 방식 통신 실행 - 앱과 사용자 상호작용
    updater.start_polling(poll_interval=5)
    # 특정 시그널이 있기 전까지 while문 실행
    updater.idle()
