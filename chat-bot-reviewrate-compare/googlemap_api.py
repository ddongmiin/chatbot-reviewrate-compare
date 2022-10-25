from roadname_translate import roadname_translate
import googlemaps


def _get_client(api_key: str):
    googlemaps_client = googlemaps.Client(key=api_key)
    return googlemaps_client if googlemaps_client else None


def googlemap_api(search_name: str):

    """구글맵 API

        구글 지도 API를 호출하는 함수입니다.

    Args:
        search_name(str): 시 + 구 + 동 + 상호명

    Return:
        address_replace(str): 전체주소
        address_road_name(str): 도로명 주소
        store_name(str): 가게명
        review_rate(float): 평점 결과
        review_cnt(int): 평점 응답 참여 유저수

    Example:
        address_all, address_road_name, store_name, review_rate, review_cnt = googlemap_api("경기도 용인시 기흥구 보정동 백채김치찌개")

    Note:
        개인 블로그에 API 사용법을 기재해 두었습니다.
        https://gibles-deepmind.tistory.com/146
    """

    googlemaps_client = _get_client("AIzaSyCyti8SqbK-pclQ6WZFtdeecszO65vbedY")
    search_result_all = googlemaps_client.places(query=search_name, language="ko")
    place_id = search_result_all["results"][0]["place_id"]
    url = googlemaps_client.place(place_id=place_id)["result"]["url"]

    if search_result_all["status"] == "ZERO_RESULTS":
        return "unknown", "unknown", "unknown", 0, 0
    search_result_use = search_result_all["results"][0]
    # 전체 주소
    address_origin = search_result_use["formatted_address"]
    # 국가명 제거
    address_replace = address_origin.replace("대한민국 ", "")
    # 도로명/지번 주소 - 당근 마켓 기술 블로그 참조
    address_road_name = roadname_translate(address_replace)
    review_rate = search_result_use["rating"] if search_result_use["rating"] else 0
    review_cnt = (
        search_result_use["user_ratings_total"]
        if search_result_use["user_ratings_total"]
        else 0
    )
    # 가게이름
    store_name = search_result_use["name"]
    return address_replace, address_road_name, store_name, review_rate, review_cnt, url
