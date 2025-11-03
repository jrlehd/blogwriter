import streamlit as st
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

# 페이지 설정
st.set_page_config(
    page_title="블로그 제목 분석 & 생성 AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS로 현대적인 디자인 적용
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 메인 컨텐츠 영역 */
    .main .block-container {
        padding: 2rem 3rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* 제목 스타일 */
    h1 {
        color: #667eea;
        font-weight: 800;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: #667eea;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        border: none;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px 15px;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* 프로그레스 바 */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 정보 박스 */
    .info-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* 성공 메시지 */
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
    }
    
    /* 리스트 아이템 */
    .blog-title-item {
        background: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* JSON 박스 */
    .json-box {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 1.5rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)


def analyze_and_generate_with_progress(keyword, num_search=30, num_generate=10):
    """
    진행률을 표시하며 블로그 제목 분석 및 생성을 수행합니다.
    """
    # 진행률 표시 컨테이너
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # OpenAI API 클라이언트 초기화
    api_key = os.getenv("OPEN_AI_API_KEY")
    if not api_key:
        st.error("⚠️ OpenAI API 키가 .env 파일에 없습니다.")
        return None
    
    client = OpenAI(api_key=api_key)
    
    try:
        # 1단계: 네이버 블로그 검색 (0-30%)
        status_text.markdown("🔍 **1단계: 네이버 블로그 검색 중...**")
        progress_bar.progress(10)
        
        blog_titles = search_naver_blog(keyword, display=num_search)
        
        if not blog_titles:
            st.error("❌ 검색 결과가 없습니다.")
            return None
        
        progress_bar.progress(30)
        status_text.markdown(f"✅ **{len(blog_titles)}개의 블로그 제목 수집 완료!**")
        
        # 2단계: GPT 분석 (30-60%)
        status_text.markdown("🤖 **2단계: ChatGPT로 제목 분석 중...**")
        progress_bar.progress(40)
        
        titles_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(blog_titles)])
        analysis_prompt = get_analysis_prompt(titles_text, keyword)
        
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
        progress_bar.progress(60)
        status_text.markdown("✅ **분석 완료!**")
        
        # 3단계: 새로운 제목 생성 (60-90%)
        status_text.markdown(f"✨ **3단계: 새로운 블로그 제목 {num_generate}개 생성 중...**")
        progress_bar.progress(70)
        
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
        progress_bar.progress(90)
        status_text.markdown("✅ **새 제목 생성 완료!**")
        
        # 완료
        progress_bar.progress(100)
        status_text.markdown("🎉 **모든 작업 완료!**")
        
        return {
            "keyword": keyword,
            "original_titles": blog_titles,
            "analysis": analysis_result,
            "generated_titles": generated_titles
        }
        
    except Exception as e:
        st.error(f"❌ 오류 발생: {str(e)}")
        return None


def main():
    # 헤더
    st.markdown("<h1>🚀 AI 블로그 제목 분석 & 생성</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 사이드바
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        st.markdown("---")
        
        num_search = st.slider(
            "검색할 블로그 수",
            min_value=10,
            max_value=100,
            value=30,
            step=10,
            help="네이버에서 검색할 블로그 글 개수를 설정합니다."
        )
        
        num_generate = st.slider(
            "생성할 제목 수",
            min_value=5,
            max_value=20,
            value=10,
            step=5,
            help="AI가 생성할 새로운 블로그 제목 개수를 설정합니다."
        )
        
        st.markdown("---")
        st.markdown("### 📖 사용 방법")
        st.markdown("""
        1. **키워드 입력**: 분석하고 싶은 주제 입력
        2. **분석 시작**: 버튼을 클릭하여 AI 분석 시작
        3. **결과 확인**: 탭에서 검색결과, 분석, 생성된 제목 확인
        4. **JSON 저장**: 필요시 JSON 파일로 다운로드
        """)
        
        st.markdown("---")
        st.markdown("### 💡 팁")
        st.info("구체적인 키워드일수록 더 정확한 분석 결과를 얻을 수 있습니다!")
    
    # 메인 컨텐츠
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        keyword = st.text_input(
            "🔍 분석할 키워드를 입력하세요",
            placeholder="예: 파이썬 웹 크롤링, 다이어트 운동, 제주도 여행",
            help="블로그 제목을 분석하고 싶은 주제나 키워드를 입력하세요."
        )
        
        analyze_button = st.button("🚀 분석 시작", use_container_width=True)
    
    st.markdown("---")
    
    # 분석 실행
    if analyze_button:
        if not keyword.strip():
            st.warning("⚠️ 키워드를 입력해주세요!")
        else:
            with st.spinner("분석 중..."):
                results = analyze_and_generate_with_progress(keyword, num_search, num_generate)
                
                if results:
                    # 세션 스테이트에 결과 저장
                    st.session_state['results'] = results
                    
                    # 성공 메시지
                    st.markdown(
                        '<div class="success-box">✅ 분석이 완료되었습니다! 아래 탭에서 결과를 확인하세요.</div>',
                        unsafe_allow_html=True
                    )
    
    # 결과 표시 (탭으로 구분)
    if 'results' in st.session_state:
        results = st.session_state['results']
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 검색 결과", 
            "🔍 분석 결과", 
            "✨ 생성된 제목", 
            "💾 JSON"
        ])
        
        # 탭 1: 검색 결과
        with tab1:
            st.markdown(f"### 📊 '{results['keyword']}' 검색 결과 ({len(results['original_titles'])}개)")
            st.markdown("---")
            
            for idx, title in enumerate(results['original_titles'], 1):
                st.markdown(
                    f'<div class="blog-title-item"><strong>{idx}.</strong> {title}</div>',
                    unsafe_allow_html=True
                )
        
        # 탭 2: 분석 결과
        with tab2:
            st.markdown("### 🔍 AI 분석 결과")
            st.markdown("---")
            st.markdown(results['analysis'])
        
        # 탭 3: 생성된 제목
        with tab3:
            st.markdown(f"### ✨ 새롭게 생성된 블로그 제목 ({num_generate}개)")
            st.markdown("---")
            st.markdown(results['generated_titles'])
        
        # 탭 4: JSON
        with tab4:
            st.markdown("### 💾 JSON 형식 데이터")
            st.markdown("---")
            
            # JSON 데이터 표시
            json_data = json.dumps(results, ensure_ascii=False, indent=2)
            st.code(json_data, language='json')
            
            # 다운로드 버튼
            st.download_button(
                label="📥 JSON 파일 다운로드",
                data=json_data,
                file_name=f"blog_analysis_{results['keyword']}.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    main()


