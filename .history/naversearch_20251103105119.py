import os
import urllib.request
import urllib.parse
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def search_naver_blog(keyword, display=20):
    """
    네이버 블로그 검색 API를 사용하여 검색 결과를 가져옵니다.
    
    Args:
        keyword (str): 검색할 키워드
        display (int): 가져올 검색 결과 개수 (기본값: 20, 최대: 100)
    
    Returns:
        list: 블로그 제목 리스트
    """
    # 환경 변수에서 클라이언트 ID와 시크릿 가져오기
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET_KEY")
    
    if not client_id or not client_secret:
        print("오류: 네이버 API 인증 정보가 .env 파일에 없습니다.")
        return []
    
    # 검색어 URL 인코딩
    encText = urllib.parse.quote(keyword)
    
    # API URL 생성
    url = f"https://openapi.naver.com/v1/search/blog.json?query={encText}&display={display}&sort=sim"
    
    # 요청 생성
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    
    try:
        # API 호출
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))
            
            # 검색 결과에서 제목만 추출
            titles = []
            for item in data.get('items', []):
                # HTML 태그 제거 (간단한 방법)
                title = item['title']
                title = title.replace('<b>', '').replace('</b>', '')
                titles.append(title)
            
            return titles
        else:
            print(f"오류 코드: {rescode}")
            return []
            
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        return []


def main():
    """메인 함수"""
    print("=" * 60)
    print("네이버 블로그 검색")
    print("=" * 60)
    
    # 사용자로부터 검색 키워드 입력받기
    keyword = input("\n검색할 키워드를 입력하세요: ")
    
    if not keyword.strip():
        print("키워드를 입력해주세요.")
        return
    
    print(f"\n'{keyword}' 검색 중...\n")
    
    # 블로그 검색 실행
    titles = search_naver_blog(keyword, display=30)
    
    if titles:
        print(f"상위 {len(titles)}개 블로그 글 제목:\n")
        for idx, title in enumerate(titles, 1):
            print(f"{idx}. {title}")
    else:
        print("검색 결과가 없습니다.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

