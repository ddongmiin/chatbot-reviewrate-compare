import re

def roadname_translate(address:str) -> str:
    
    """도로명/지번 주소 변환기
    
        전체 주소를 받아 도로명 또는 지번 주소와 변환하는 함수입니다.
    
    Args: 
        address(str): 전체 주소
        
    Return:
        after_translate(str): 도로명/지번 주소
        
    Example:
        road_name = roadname_translate("경기도 성남시 분당구 삼평동 대왕판교로")
        
    Note:
        당근마켓 블로그를 참조했습니다.
        https://medium.com/daangn/%EC%A3%BC%EC%86%8C-%EC%9D%B8%EC%8B%9D%EC%9D%84-%EC%9C%84%ED%95%9C-%EC%82%BD%EC%A7%88%EC%9D%98-%EA%B8%B0%EB%A1%9D-df2d8f82d25
    """ 
    
    compiler = re.compile("(([가-힣A-Za-z·\d~\-\.]{2,}(로|길).[\d|\-\d]+)|([가-힣A-Za-z·\d~\-\.]+(동|읍|리)\s)[\d|\-\d]+)")
    after_translate = compiler.search(address).group()
    if compiler.search(address).group() is not None:
        return after_translate
    else: 
        return 'unknown'
