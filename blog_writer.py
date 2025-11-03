import customtkinter as ctk
import os
import re
import threading
from tkinter import messagebox, filedialog
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

# CustomTkinter 테마 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def get_blog_writing_prompt(title, keyword):
    """
    SEO 최적화된 블로그 글 작성 프롬프트
    
    Args:
        title (str): 블로그 글 제목
        keyword (str): 핵심 키워드
    
    Returns:
        str: 블로그 글 작성 프롬프트
    """
    return f"""당신은 전문 블로그 작가이자 SEO 전문가입니다. 아래 제목으로 SEO와 독자 참여에 최적화된 블로그 글을 작성해주세요.

# 블로그 제목
{title}

# 핵심 키워드
{keyword}

# 작성 요구사항

## 1. SEO 최적화
- 제목에 핵심 키워드 포함
- 본문에 핵심 키워드를 자연스럽게 5-8회 반복
- 관련 키워드와 LSI 키워드 활용
- 부제목(H2, H3)에 키워드 변형 포함
- 메타 설명에 적합한 첫 문단 작성

## 2. 구글 검색 최적화 (SEO)
- 검색 의도에 맞는 구체적이고 실용적인 정보 제공
- 명확한 구조 (서론-본론-결론)
- 단락별로 명확한 소제목 사용
- 불렛 포인트나 번호 목록 활용
- 2,000-3,000자 분량

## 3. 독자 참여 요소
- 흥미로운 도입부로 시작
- 실용적인 정보와 팁 제공
- 구체적인 예시나 사례 포함
- 행동 유도 문구(CTA) 포함
- 친근하고 읽기 쉬운 문체

## 4. 구조
다음 구조로 작성해주세요:

### 서론
- 독자의 관심을 끄는 도입
- 글의 목적과 가치 제시
- 문제 상황이나 질문 제기

### 본론
- 소제목으로 구분된 여러 섹션
- 각 섹션마다 구체적인 정보
- 실용적인 팁과 방법
- 예시와 사례

### 결론
- 핵심 내용 요약
- 실천 방안 제시
- 독자 행동 유도

## 5. 추가 요구사항
- 마크다운 형식으로 작성하지 말고 일반 텍스트로 작성
- 이모지는 사용하지 않음
- 자연스러운 한국어 사용
- 전문적이면서도 친근한 톤

블로그 글을 작성해주세요."""


class BlogWriterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title("✍️ AI 블로그 글 작성기")
        self.geometry("1200x800")
        
        # 데이터 저장
        self.titles = []
        self.keyword = ""
        self.save_path = ""
        self.current_index = 0
        
        # UI 초기화
        self.create_widgets()
        
    def create_widgets(self):
        # 메인 컨테이너 (좌우 2분할)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=7)
        self.grid_rowconfigure(0, weight=1)
        
        # ========== 왼쪽 패널 (입력 및 설정) ==========
        left_panel = ctk.CTkFrame(self, corner_radius=15)
        left_panel.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        # 타이틀
        title_label = ctk.CTkLabel(
            left_panel,
            text="✍️ AI 블로그\n글 작성기",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        title_label.pack(pady=(30, 20))
        
        # 구분선
        separator1 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator1.pack(fill="x", padx=20, pady=10)
        
        # 저장 경로 설정
        path_label = ctk.CTkLabel(
            left_panel,
            text="📁 저장 경로",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        path_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.path_entry = ctk.CTkEntry(
            left_panel,
            placeholder_text="저장할 폴더를 선택하세요",
            height=40,
            font=ctk.CTkFont(size=12),
            state="readonly"
        )
        self.path_entry.pack(pady=(0, 5), padx=20, fill="x")
        
        self.browse_button = ctk.CTkButton(
            left_panel,
            text="📂 폴더 선택",
            command=self.browse_folder,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=("#2d6a4f", "#52b788"),
            hover_color=("#1b4332", "#40916c")
        )
        self.browse_button.pack(pady=(0, 10), padx=20, fill="x")
        
        # 구분선
        separator2 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator2.pack(fill="x", padx=20, pady=15)
        
        # 키워드 입력
        keyword_label = ctk.CTkLabel(
            left_panel,
            text="🔍 핵심 키워드",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        keyword_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.keyword_entry = ctk.CTkEntry(
            left_panel,
            placeholder_text="예: 파이썬 웹 크롤링",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.keyword_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # 제목 입력 (텍스트박스)
        titles_label = ctk.CTkLabel(
            left_panel,
            text="📝 블로그 제목들 (한 줄에 하나씩)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        titles_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.titles_textbox = ctk.CTkTextbox(
            left_panel,
            height=200,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.titles_textbox.pack(pady=(0, 10), padx=20, fill="x")
        
        # 구분선
        separator3 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator3.pack(fill="x", padx=20, pady=15)
        
        # 작성 시작 버튼
        self.write_button = ctk.CTkButton(
            left_panel,
            text="✍️ 블로그 글 작성 시작",
            command=self.start_writing,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f538d", "#4a9eff"),
            hover_color=("#174270", "#3a7ed1")
        )
        self.write_button.pack(pady=10, padx=20, fill="x")
        
        # 프로그레스 바
        self.progress_bar = ctk.CTkProgressBar(left_panel)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)
        
        # 상태 레이블
        self.status_label = ctk.CTkLabel(
            left_panel,
            text="대기 중...",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        self.status_label.pack(pady=(5, 20))
        
        # ========== 오른쪽 패널 (미리보기) ==========
        right_panel = ctk.CTkFrame(self, corner_radius=15)
        right_panel.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        
        # 헤더
        preview_label = ctk.CTkLabel(
            right_panel,
            text="📄 작성 중인 글 미리보기",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        preview_label.pack(pady=20)
        
        # 현재 제목 표시
        self.current_title_label = ctk.CTkLabel(
            right_panel,
            text="",
            font=ctk.CTkFont(size=14),
            wraplength=800
        )
        self.current_title_label.pack(pady=10, padx=20)
        
        # 미리보기 텍스트박스
        self.preview_textbox = ctk.CTkTextbox(
            right_panel,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.preview_textbox.pack(fill="both", expand=True, padx=20, pady=20)
        self.preview_textbox.insert("1.0", "작성된 블로그 글이 여기에 표시됩니다...")
        self.preview_textbox.configure(state="disabled")
    
    def browse_folder(self):
        """폴더 선택 다이얼로그"""
        folder_path = filedialog.askdirectory(title="블로그 글을 저장할 폴더를 선택하세요")
        if folder_path:
            self.save_path = folder_path
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_path)
            self.path_entry.configure(state="readonly")
    
    def start_writing(self):
        """블로그 글 작성 시작"""
        # 유효성 검사
        if not self.save_path:
            messagebox.showwarning("경고", "저장 경로를 먼저 선택해주세요!")
            return
        
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("경고", "핵심 키워드를 입력해주세요!")
            return
        
        titles_text = self.titles_textbox.get("1.0", "end").strip()
        if not titles_text:
            messagebox.showwarning("경고", "블로그 제목을 입력해주세요!")
            return
        
        # 제목 파싱
        self.titles = [line.strip() for line in titles_text.split("\n") if line.strip()]
        
        # 번호 제거 (예: "1. 제목" -> "제목")
        self.titles = [re.sub(r'^\d+\.\s*', '', title) for title in self.titles]
        # " - " 이후 설명 제거
        self.titles = [title.split(' - ')[0].strip() for title in self.titles]
        
        if not self.titles:
            messagebox.showwarning("경고", "유효한 제목이 없습니다!")
            return
        
        self.keyword = keyword
        self.current_index = 0
        
        # 버튼 비활성화
        self.write_button.configure(state="disabled")
        
        # 진행
        result = messagebox.askyesno(
            "확인",
            f"{len(self.titles)}개의 블로그 글을 작성합니다.\n계속하시겠습니까?"
        )
        
        if result:
            # 스레드로 작성 실행
            thread = threading.Thread(target=self.write_blogs)
            thread.daemon = True
            thread.start()
        else:
            self.write_button.configure(state="normal")
    
    def write_blogs(self):
        """모든 블로그 글 작성"""
        try:
            # OpenAI API 클라이언트 초기화
            api_key = os.getenv("OPEN_AI_API_KEY")
            if not api_key:
                self.update_status("❌ OpenAI API 키가 없습니다.", 0)
                messagebox.showerror("오류", "OpenAI API 키가 .env 파일에 없습니다.")
                self.write_button.configure(state="normal")
                return
            
            client = OpenAI(api_key=api_key)
            
            total = len(self.titles)
            
            for idx, title in enumerate(self.titles, 1):
                self.current_index = idx
                progress = (idx - 1) / total
                
                # 상태 업데이트
                self.update_status(f"📝 {idx}/{total}: '{title}' 작성 중...", progress)
                self.current_title_label.configure(text=f"[{idx}/{total}] {title}")
                
                # 블로그 글 작성
                prompt = get_blog_writing_prompt(title, self.keyword)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 전문 블로그 작가이자 SEO 전문가입니다. 검색 엔진 최적화와 독자 참여를 극대화하는 고품질 블로그 글을 작성합니다."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )
                
                blog_content = response.choices[0].message.content
                
                # 미리보기 업데이트
                self.update_preview(blog_content)
                
                # 파일 저장
                safe_filename = self.sanitize_filename(title)
                file_path = os.path.join(self.save_path, f"{idx:02d}_{safe_filename}.txt")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"제목: {title}\n")
                    f.write(f"키워드: {self.keyword}\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(blog_content)
                
                self.update_status(f"✅ {idx}/{total}: 저장 완료", idx / total)
            
            # 완료
            self.update_status("🎉 모든 블로그 글 작성 완료!", 1.0)
            messagebox.showinfo(
                "완료",
                f"{total}개의 블로그 글이 성공적으로 작성되었습니다!\n\n저장 위치: {self.save_path}"
            )
            
        except Exception as e:
            self.update_status("❌ 오류 발생", 0)
            messagebox.showerror("오류", f"오류가 발생했습니다:\n{str(e)}")
        
        finally:
            self.write_button.configure(state="normal")
    
    def sanitize_filename(self, filename):
        """파일명에 사용할 수 없는 문자 제거"""
        # Windows에서 사용할 수 없는 문자 제거
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # 공백을 언더스코어로 변경
        filename = filename.replace(' ', '_')
        
        # 길이 제한 (50자)
        if len(filename) > 50:
            filename = filename[:50]
        
        return filename
    
    def update_status(self, text, progress):
        """상태 텍스트 및 프로그레스 바 업데이트"""
        self.status_label.configure(text=text)
        self.progress_bar.set(progress)
    
    def update_preview(self, content):
        """미리보기 업데이트"""
        self.preview_textbox.configure(state="normal")
        self.preview_textbox.delete("1.0", "end")
        self.preview_textbox.insert("1.0", content)
        self.preview_textbox.configure(state="disabled")


def main():
    app = BlogWriterApp()
    app.mainloop()


if __name__ == "__main__":
    main()


