import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from naversearch import search_naver_blog
from prompt import (
    get_analysis_prompt,
    get_analysis_system_prompt,
    get_generation_prompt,
    get_generation_system_prompt
)

# .env 파일 로드
load_dotenv()

def analyze_and_generate_titles(keyword, num_search=30, num_generate=10):
    """
    네이버 블로그 제목을 분석하고 새로운 제목을 생성합니다.
    
    Args:
        keyword (str): 검색할 키워드
        num_search (int): 검색할 블로그 수 (기본값: 30)
        num_generate (int): 생성할 새 제목 수 (기본값: 10)
    
    Returns:
        dict: 분석 결과 및 생성된 제목
    """
    # OpenAI API 클라이언트 초기화
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        print("오류: OpenAI API 키가 .env 파일에 없습니다.")
        return None
    
    client = OpenAI(api_key=api_key)
    
    # 1단계: 네이버 블로그 검색
    print(f"\n[1단계] '{keyword}' 키워드로 블로그 검색 중...\n")
    blog_titles = search_naver_blog(keyword, display=num_search)
    
    if not blog_titles:
        print("검색 결과가 없습니다.")
        return None
    
    print(f"총 {len(blog_titles)}개의 블로그 제목을 수집했습니다.\n")
    print("=" * 80)
    print("수집된 블로그 제목:")
    print("=" * 80)
    for idx, title in enumerate(blog_titles, 1):
        print(f"{idx}. {title}")
    print("=" * 80)
    
    # 2단계: GPT를 사용한 블로그 제목 분석
    print("\n[2단계] ChatGPT API로 블로그 제목 분석 중...\n")
    
    # 블로그 제목 리스트를 문자열로 변환
    titles_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(blog_titles)])
    
    # prompt.py에서 분석 프롬프트 가져오기
    analysis_prompt = get_analysis_prompt(titles_text, keyword)

    try:
        # GPT-4o-mini 모델로 분석 요청
        analysis_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": get_analysis_system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        analysis_result = analysis_response.choices[0].message.content
        print("=" * 80)
        print("📊 블로그 제목 분석 결과")
        print("=" * 80)
        print(analysis_result)
        print("=" * 80)
        
        # 3단계: 분석을 바탕으로 새로운 제목 생성
        print(f"\n[3단계] 분석 결과를 바탕으로 새로운 블로그 제목 {num_generate}개 생성 중...\n")
        
        # prompt.py에서 생성 프롬프트 가져오기
        generation_prompt = get_generation_prompt(analysis_result, titles_text, keyword, num_generate)

        generation_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": get_generation_system_prompt()},
                {"role": "user", "content": generation_prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        generated_titles = generation_response.choices[0].message.content
        print("=" * 80)
        print(f"✨ 새롭게 생성된 블로그 제목 {num_generate}개")
        print("=" * 80)
        print(generated_titles)
        print("=" * 80)
        
        # 결과 반환
        return {
            "keyword": keyword,
            "original_titles": blog_titles,
            "analysis": analysis_result,
            "generated_titles": generated_titles
        }
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return None


def save_results_to_file(results, filename="blog_analysis_result.json"):
    """
    분석 및 생성 결과를 파일로 저장합니다.
    
    Args:
        results (dict): 분석 결과
        filename (str): 저장할 파일명
    """
    if results:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 결과가 '{filename}' 파일에 저장되었습니다.")
        except Exception as e:
            print(f"파일 저장 중 오류 발생: {e}")


def main():
    """메인 함수"""
    print("=" * 80)
    print("🚀 AI 기반 블로그 제목 분석 및 생성 시스템")
    print("=" * 80)
    
    # 사용자로부터 검색 키워드 입력받기
    keyword = input("\n분석할 키워드를 입력하세요: ")
    
    if not keyword.strip():
        print("키워드를 입력해주세요.")
        return
    
    # 블로그 제목 분석 및 생성
    results = analyze_and_generate_titles(keyword, num_search=30, num_generate=10)
    
    if results:
        # 결과를 JSON 파일로 저장할지 물어보기
        print("\n" + "=" * 80)
        save_option = input("결과를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower()
        
        if save_option in ['y', 'yes', 'ㅛ']:
            save_results_to_file(results)
        else:
            print("JSON 파일 저장을 건너뜁니다.")
        
        print("\n" + "=" * 80)
        print("✅ 모든 작업이 완료되었습니다!")
        print("=" * 80)
    else:
        print("\n작업을 완료할 수 없습니다.")


if __name__ == "__main__":
    main()

