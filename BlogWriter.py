import customtkinter as ctk
import os
import json
import re
import threading
from tkinter import messagebox, filedialog
from dotenv import load_dotenv
from openai import OpenAI
from naversearch import search_naver_blog
from title_prompt import (
    get_analysis_prompt,
    get_analysis_system_prompt,
    get_generation_prompt,
    get_generation_system_prompt
)
from blog_content_prompt import (
    get_blog_writing_prompt,
    get_blog_writing_system_prompt
)

# .env 파일 로드
load_dotenv()

# CustomTkinter 테마 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BlogWriterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title("✍️ AI 블로그 올인원 시스템")
        self.geometry("1400x900")
        
        # 데이터 저장
        self.results = None
        self.generated_titles = []
        self.title_checkboxes = []
        self.save_path = ""
        self.phase = "title_generation"  # 'title_generation' or 'blog_writing'
        self.stop_writing_flag = False  # 작성 중단 플래그
        
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
            text="✍️ AI 블로그\n올인원 시스템",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = ctk.CTkLabel(
            left_panel,
            text="검색 → 분석 → 제목 생성 → 글 작성",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        subtitle_label.pack(pady=(0, 15))
        
        # 구분선
        separator1 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator1.pack(fill="x", padx=20, pady=10)
        
        # 키워드 입력
        keyword_label = ctk.CTkLabel(
            left_panel,
            text="🔍 분석할 키워드",
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
        
        # 구분선
        separator2 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator2.pack(fill="x", padx=20, pady=10)
        
        # 검색할 블로그 수
        search_label = ctk.CTkLabel(
            left_panel,
            text="📊 검색할 블로그 수",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.search_slider = ctk.CTkSlider(
            left_panel,
            from_=10,
            to=100,
            number_of_steps=9,
            command=self.update_search_label
        )
        self.search_slider.set(30)
        self.search_slider.pack(pady=(0, 5), padx=20, fill="x")
        
        self.search_value_label = ctk.CTkLabel(
            left_panel,
            text="30개",
            font=ctk.CTkFont(size=12)
        )
        self.search_value_label.pack(pady=(0, 10), padx=20, anchor="center")
        
        # 생성할 제목 수
        generate_label = ctk.CTkLabel(
            left_panel,
            text="✨ 생성할 제목 수",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        generate_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.generate_slider = ctk.CTkSlider(
            left_panel,
            from_=5,
            to=20,
            number_of_steps=3,
            command=self.update_generate_label
        )
        self.generate_slider.set(10)
        self.generate_slider.pack(pady=(0, 5), padx=20, fill="x")
        
        self.generate_value_label = ctk.CTkLabel(
            left_panel,
            text="10개",
            font=ctk.CTkFont(size=12)
        )
        self.generate_value_label.pack(pady=(0, 15), padx=20, anchor="center")
        
        # 구분선
        separator3 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator3.pack(fill="x", padx=20, pady=10)
        
        # 제목 생성 시작 버튼
        self.title_gen_button = ctk.CTkButton(
            left_panel,
            text="🚀 제목 생성 시작",
            command=self.start_title_generation,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f538d", "#4a9eff"),
            hover_color=("#174270", "#3a7ed1")
        )
        self.title_gen_button.pack(pady=10, padx=20, fill="x")
        
        # 블로그 글 작성 시작 버튼 (초기에는 비활성화)
        self.blog_write_button = ctk.CTkButton(
            left_panel,
            text="✍️ 블로그 글 작성 시작",
            command=self.start_blog_writing,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#2d6a4f", "#52b788"),
            hover_color=("#1b4332", "#40916c"),
            state="disabled"
        )
        self.blog_write_button.pack(pady=10, padx=20, fill="x")
        
        # 작성 중단 버튼 (초기에는 숨김)
        self.stop_button = ctk.CTkButton(
            left_panel,
            text="⛔ 작성 중단",
            command=self.stop_writing,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#d32f2f", "#ef5350"),
            hover_color=("#b71c1c", "#d32f2f")
        )
        # 초기에는 pack하지 않음 (숨김)
        
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
        
        # ========== 오른쪽 패널 (결과 표시) ==========
        right_panel = ctk.CTkFrame(self, corner_radius=15)
        right_panel.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        
        # 탭뷰
        self.tabview = ctk.CTkTabview(right_panel, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 탭 생성
        self.tabview.add("📊 검색 결과")
        self.tabview.add("🔍 분석 결과")
        self.tabview.add("✨ 생성된 제목")
        self.tabview.add("⚙️ 글 작성 설정")
        self.tabview.add("📝 작성 중인 글")
        
        # 탭 1: 검색 결과
        self.search_textbox = ctk.CTkTextbox(
            self.tabview.tab("📊 검색 결과"),
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.search_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.search_textbox.insert("1.0", "검색 결과가 여기에 표시됩니다...")
        self.search_textbox.configure(state="disabled")
        
        # 탭 2: 분석 결과
        self.analysis_textbox = ctk.CTkTextbox(
            self.tabview.tab("🔍 분석 결과"),
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.analysis_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.analysis_textbox.insert("1.0", "분석 결과가 여기에 표시됩니다...")
        self.analysis_textbox.configure(state="disabled")
        
        # 탭 3: 생성된 제목 (체크박스로 선택 가능)
        titles_tab = self.tabview.tab("✨ 생성된 제목")
        
        titles_header = ctk.CTkFrame(titles_tab, fg_color="transparent")
        titles_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            titles_header,
            text="💡 원하는 제목만 선택하세요 (체크 해제 시 제외됨)",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10)
        
        self.select_all_button = ctk.CTkButton(
            titles_header,
            text="전체 선택",
            command=self.select_all_titles,
            width=100,
            height=30
        )
        self.select_all_button.pack(side="right", padx=5)
        
        self.deselect_all_button = ctk.CTkButton(
            titles_header,
            text="전체 해제",
            command=self.deselect_all_titles,
            width=100,
            height=30
        )
        self.deselect_all_button.pack(side="right", padx=5)
        
        self.titles_scrollable = ctk.CTkScrollableFrame(
            titles_tab,
            fg_color="transparent"
        )
        self.titles_scrollable.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # 다음 버튼 (초기에는 숨김)
        self.next_to_settings_button = ctk.CTkButton(
            titles_tab,
            text="✅ 선택 완료 → 글 작성 설정으로 이동",
            command=self.go_to_settings,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#2d6a4f", "#52b788"),
            hover_color=("#1b4332", "#40916c")
        )
        # 초기에는 pack하지 않음 (숨김)
        
        # 탭 4: 글 작성 설정
        settings_tab = self.tabview.tab("⚙️ 글 작성 설정")
        
        # 모델 선택
        model_label = ctk.CTkLabel(
            settings_tab,
            text="🤖 GPT 모델 선택",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        model_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        self.model_var = ctk.StringVar(value="gpt-4o-mini")
        
        models = [
            ("GPT-4o-mini (빠르고 경제적)", "gpt-4o-mini"),
            ("GPT-4o (고품질, 느림)", "gpt-4o"),
            ("GPT-4-turbo (균형잡힌)", "gpt-4-turbo")
        ]
        
        for text, value in models:
            ctk.CTkRadioButton(
                settings_tab,
                text=text,
                variable=self.model_var,
                value=value,
                font=ctk.CTkFont(size=13)
            ).pack(pady=5, padx=40, anchor="w")
        
        # 구분선
        separator_settings = ctk.CTkFrame(settings_tab, height=2, fg_color=("#cccccc", "#333333"))
        separator_settings.pack(fill="x", padx=20, pady=20)
        
        # 글자 수 설정
        chars_label = ctk.CTkLabel(
            settings_tab,
            text="📏 글자 수 범위 설정",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        chars_label.pack(pady=(10, 10), padx=20, anchor="w")
        
        # 최소 글자 수
        min_chars_label = ctk.CTkLabel(
            settings_tab,
            text="최소 글자 수",
            font=ctk.CTkFont(size=14)
        )
        min_chars_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.min_chars_slider = ctk.CTkSlider(
            settings_tab,
            from_=500,
            to=5000,
            number_of_steps=18,
            command=self.update_min_chars_label
        )
        self.min_chars_slider.set(2000)
        self.min_chars_slider.pack(pady=(0, 5), padx=20, fill="x")
        
        self.min_chars_value_label = ctk.CTkLabel(
            settings_tab,
            text="최소: 2000자",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        self.min_chars_value_label.pack(pady=(0, 15), padx=20, anchor="center")
        
        # 최대 글자 수
        max_chars_label = ctk.CTkLabel(
            settings_tab,
            text="최대 글자 수",
            font=ctk.CTkFont(size=14)
        )
        max_chars_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.max_chars_slider = ctk.CTkSlider(
            settings_tab,
            from_=1000,
            to=10000,
            number_of_steps=18,
            command=self.update_max_chars_label
        )
        self.max_chars_slider.set(3000)
        self.max_chars_slider.pack(pady=(0, 5), padx=20, fill="x")
        
        self.max_chars_value_label = ctk.CTkLabel(
            settings_tab,
            text="최대: 3000자",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#d32f2f", "#ef5350")
        )
        self.max_chars_value_label.pack(pady=(0, 15), padx=20, anchor="center")
        
        # 탭 5: 작성 중인 글
        blog_tab = self.tabview.tab("📝 작성 중인 글")
        
        self.current_blog_label = ctk.CTkLabel(
            blog_tab,
            text="",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.current_blog_label.pack(pady=10, padx=20)
        
        # 진행률 표시
        self.blog_progress_frame = ctk.CTkFrame(blog_tab, fg_color="transparent")
        self.blog_progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.blog_progress_label = ctk.CTkLabel(
            self.blog_progress_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.blog_progress_label.pack(pady=5)
        
        self.blog_progress_bar = ctk.CTkProgressBar(self.blog_progress_frame)
        self.blog_progress_bar.pack(fill="x", pady=5)
        self.blog_progress_bar.set(0)
        
        self.blog_textbox = ctk.CTkTextbox(
            blog_tab,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.blog_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.blog_textbox.insert("1.0", "작성 중인 블로그 글이 여기에 표시됩니다...")
        self.blog_textbox.configure(state="disabled")
    
    def update_search_label(self, value):
        """검색할 블로그 수 레이블 업데이트"""
        self.search_value_label.configure(text=f"{int(value)}개")
    
    def update_generate_label(self, value):
        """생성할 제목 수 레이블 업데이트"""
        self.generate_value_label.configure(text=f"{int(value)}개")
    
    def update_min_chars_label(self, value):
        """최소 글자 수 레이블 업데이트"""
        min_val = int(value)
        self.min_chars_value_label.configure(text=f"최소: {min_val}자")
    
    def update_max_chars_label(self, value):
        """최대 글자 수 레이블 업데이트"""
        max_val = int(value)
        self.max_chars_value_label.configure(text=f"최대: {max_val}자")
    
    def start_title_generation(self):
        """제목 생성 시작"""
        keyword = self.keyword_entry.get().strip()
        
        if not keyword:
            messagebox.showwarning("경고", "키워드를 입력해주세요!")
            return
        
        # 버튼 비활성화
        self.title_gen_button.configure(state="disabled")
        
        # 프로그레스 바 초기화
        self.progress_bar.set(0)
        self.status_label.configure(text="제목 생성 프로세스 시작...")
        
        # 스레드로 실행
        num_search = int(self.search_slider.get())
        num_generate = int(self.generate_slider.get())
        
        thread = threading.Thread(
            target=self.run_title_generation,
            args=(keyword, num_search, num_generate)
        )
        thread.daemon = True
        thread.start()
    
    def run_title_generation(self, keyword, num_search, num_generate):
        """제목 생성 프로세스 실행"""
        try:
            # OpenAI API 클라이언트 초기화
            api_key = os.getenv("OPEN_AI_API_KEY")
            if not api_key:
                self.update_status("❌ OpenAI API 키가 없습니다.", 0)
                messagebox.showerror("오류", "OpenAI API 키가 .env 파일에 없습니다.")
                self.title_gen_button.configure(state="normal")
                return
            
            client = OpenAI(api_key=api_key)
            
            # 1단계: 네이버 블로그 검색
            self.update_status("🔍 1/3: 네이버 블로그 검색 중...", 0.1)
            blog_titles = search_naver_blog(keyword, display=num_search)
            
            if not blog_titles:
                self.update_status("❌ 검색 결과 없음", 0)
                messagebox.showerror("오류", "검색 결과가 없습니다.")
                self.title_gen_button.configure(state="normal")
                return
            
            self.update_status(f"✅ {len(blog_titles)}개 블로그 제목 수집 완료", 0.3)
            
            # 검색 결과 표시
            search_result = f"'{keyword}' 검색 결과 ({len(blog_titles)}개)\n\n"
            search_result += "=" * 60 + "\n\n"
            for idx, title in enumerate(blog_titles, 1):
                search_result += f"{idx}. {title}\n\n"
            self.update_textbox(self.search_textbox, search_result)
            
            # 2단계: AI 분석
            self.update_status("🤖 2/3: ChatGPT로 제목 분석 중...", 0.4)
            
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
            self.update_status("✅ 분석 완료!", 0.6)
            self.update_textbox(self.analysis_textbox, analysis_result)
            
            # 3단계: 새로운 제목 생성
            self.update_status(f"✨ 3/3: 새로운 제목 {num_generate}개 생성 중...", 0.7)
            
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
            
            generated_titles_text = generation_response.choices[0].message.content
            self.update_status("✅ 제목 생성 완료!", 1.0)
            self.update_textbox(self.analysis_textbox, analysis_result)
            
            # 제목 파싱
            self.generated_titles = self.parse_titles(generated_titles_text)
            
            # 제목 체크박스 생성
            self.create_title_checkboxes()
            
            # 완료
            self.update_status("🎉 제목 생성이 완료되었습니다!", 1.0)
            
            # 블로그 글 생성 여부 묻기
            self.after(500, self.ask_blog_writing)
            
        except Exception as e:
            self.update_status("❌ 오류 발생", 0)
            messagebox.showerror("오류", f"오류가 발생했습니다:\n{str(e)}")
        
        finally:
            self.title_gen_button.configure(state="normal")
    
    def create_title_checkboxes(self):
        """생성된 제목 체크박스 생성"""
        # 기존 체크박스 제거
        for widget in self.titles_scrollable.winfo_children():
            widget.destroy()
        
        self.title_checkboxes = []
        
        for idx, title in enumerate(self.generated_titles, 1):
            # 프레임 생성
            title_frame = ctk.CTkFrame(
                self.titles_scrollable,
                fg_color=("gray90", "gray20"),
                corner_radius=10
            )
            title_frame.pack(fill="x", padx=10, pady=5)
            
            # 체크박스 변수
            var = ctk.BooleanVar(value=True)
            
            # 체크박스
            checkbox = ctk.CTkCheckBox(
                title_frame,
                text=f"{idx}. {title}",
                variable=var,
                font=ctk.CTkFont(size=13)
            )
            checkbox.pack(side="left", padx=15, pady=15, fill="x", expand=True)
            
            self.title_checkboxes.append((title, var))
    
    def select_all_titles(self):
        """모든 제목 선택"""
        for _, var in self.title_checkboxes:
            var.set(True)
    
    def deselect_all_titles(self):
        """모든 제목 선택 해제"""
        for _, var in self.title_checkboxes:
            var.set(False)
    
    def ask_blog_writing(self):
        """블로그 글 생성 여부 확인"""
        result = messagebox.askyesno(
            "블로그 글 작성",
            "생성된 제목으로 블로그 글을 작성하시겠습니까?"
        )
        
        if result:
            # 제목 생성 버튼 숨기기
            self.title_gen_button.pack_forget()
            # 생성된 제목 탭으로 이동
            self.tabview.set("✨ 생성된 제목")
            # 다음 버튼 표시
            self.next_to_settings_button.pack(fill="x", padx=10, pady=(5, 10))
            messagebox.showinfo(
                "안내",
                "1. ✨ 현재 탭에서 원하는 제목만 선택하세요.\n"
                "2. 하단의 '✅ 선택 완료' 버튼을 클릭하세요.\n"
                "3. 글 작성 설정을 완료한 후 작성을 시작하세요!"
            )
    
    def go_to_settings(self):
        """글 작성 설정 탭으로 이동"""
        # 선택된 제목 확인
        selected_titles = [title for title, var in self.title_checkboxes if var.get()]
        
        if not selected_titles:
            messagebox.showwarning("경고", "최소 1개 이상의 제목을 선택해주세요!")
            return
        
        # 블로그 글 작성 버튼 활성화
        self.blog_write_button.configure(state="normal")
        # 설정 탭으로 이동
        self.tabview.set("⚙️ 글 작성 설정")
        messagebox.showinfo(
            "안내",
            f"✅ {len(selected_titles)}개의 제목이 선택되었습니다!\n\n"
            "이제 GPT 모델과 글자 수 범위를 설정한 후\n"
            "왼쪽의 '✍️ 블로그 글 작성 시작' 버튼을 클릭하세요."
        )
    
    def start_blog_writing(self):
        """블로그 글 작성 시작"""
        # 선택된 제목만 추출
        selected_titles = [title for title, var in self.title_checkboxes if var.get()]
        
        if not selected_titles:
            messagebox.showwarning("경고", "최소 1개 이상의 제목을 선택해주세요!")
            return
        
        # 글자 수 검증
        min_chars = int(self.min_chars_slider.get())
        max_chars = int(self.max_chars_slider.get())
        
        if min_chars > max_chars:
            messagebox.showerror(
                "오류", 
                f"최소 글자 수({min_chars}자)가 최대 글자 수({max_chars}자)보다 큽니다!\n\n"
                "⚙️ 글 작성 설정 탭에서 글자 수 범위를 올바르게 설정해주세요."
            )
            self.tabview.set("⚙️ 글 작성 설정")
            return
        
        # 저장 경로 선택
        save_path = filedialog.askdirectory(title="블로그 글을 저장할 폴더를 선택하세요")
        if not save_path:
            return
        
        self.save_path = save_path
        
        # 중단 플래그 초기화
        self.stop_writing_flag = False
        
        # 버튼 전환
        self.blog_write_button.pack_forget()
        self.stop_button.pack(pady=10, padx=20, fill="x")
        self.title_gen_button.configure(state="disabled")
        
        # 작성 중인 글 탭으로 이동
        self.tabview.set("📝 작성 중인 글")
        
        # 스레드로 실행
        keyword = self.keyword_entry.get().strip()
        model = self.model_var.get()
        
        thread = threading.Thread(
            target=self.run_blog_writing,
            args=(selected_titles, keyword, model, min_chars, max_chars)
        )
        thread.daemon = True
        thread.start()
    
    def stop_writing(self):
        """블로그 글 작성 중단"""
        result = messagebox.askyesno(
            "작성 중단",
            "정말로 블로그 글 작성을 중단하시겠습니까?\n\n"
            "※ 현재까지 작성된 글은 저장됩니다."
        )
        
        if result:
            self.stop_writing_flag = True
            self.update_status("⛔ 사용자가 작성을 중단했습니다.", 0)
            messagebox.showinfo("중단", "작성이 중단되었습니다.\n현재까지 작성된 글은 저장되었습니다.")
    
    def run_blog_writing(self, titles, keyword, model, min_chars, max_chars):
        """블로그 글 작성 프로세스 실행"""
        try:
            api_key = os.getenv("OPEN_AI_API_KEY")
            client = OpenAI(api_key=api_key)
            
            total_blogs = len(titles)
            completed = 0
            
            for idx, title in enumerate(titles, 1):
                # 중단 플래그 확인
                if self.stop_writing_flag:
                    break
                
                # 진행률 계산
                progress = idx / total_blogs
                progress_percent = int(progress * 100)
                
                self.update_blog_progress(
                    f"📝 [{idx}/{total_blogs}] '{title}' 작성 중... ({progress_percent}%)",
                    progress
                )
                self.current_blog_label.configure(text=f"[{idx}/{total_blogs}] {title}")
                
                # 블로그 글 작성
                blog_prompt = get_blog_writing_prompt(title, keyword, min_chars, max_chars)
                
                blog_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": get_blog_writing_system_prompt()},
                        {"role": "user", "content": blog_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                blog_content = blog_response.choices[0].message.content
                
                # 마크다운 볼드체 제거 (**내용** -> 내용)
                blog_content = re.sub(r'\*\*(.*?)\*\*', r'\1', blog_content)
                
                # 미리보기 업데이트
                self.update_textbox(self.blog_textbox, blog_content)
                
                # 파일 저장
                safe_filename = self.sanitize_filename(title)
                file_path = os.path.join(self.save_path, f"{idx:02d}_{safe_filename}.txt")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"제목: {title}\n")
                    f.write(f"키워드: {keyword}\n")
                    f.write(f"글자 수: {len(blog_content)}자\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(blog_content)
                
                completed = idx
                
                self.update_blog_progress(
                    f"✅ [{idx}/{total_blogs}] 저장 완료: {safe_filename}.txt ({progress_percent}%)",
                    progress
                )
            
            # 완료 또는 중단
            if self.stop_writing_flag:
                self.update_blog_progress(f"⛔ 작성 중단됨 ({completed}/{total_blogs}개 완료)", completed / total_blogs)
                self.update_status(f"⛔ 작성 중단: {completed}개 완료", 0)
            else:
                self.update_blog_progress(f"🎉 모든 블로그 글 작성 완료! (100%)", 1.0)
                self.update_status("🎉 모든 작업이 완료되었습니다!", 1.0)
                
                messagebox.showinfo(
                    "완료",
                    f"블로그 글 작성이 완료되었습니다!\n\n"
                    f"- 작성된 글: {total_blogs}개\n"
                    f"- 저장 위치: {self.save_path}"
                )
            
        except Exception as e:
            self.update_status("❌ 오류 발생", 0)
            messagebox.showerror("오류", f"오류가 발생했습니다:\n{str(e)}")
        
        finally:
            # 버튼 복구
            self.stop_button.pack_forget()
            self.blog_write_button.pack(pady=10, padx=20, fill="x")
            self.blog_write_button.configure(state="normal")
            self.title_gen_button.configure(state="normal")
    
    def parse_titles(self, text):
        """생성된 제목 텍스트에서 제목만 추출"""
        titles = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # "1. 제목 - 설명" 형식에서 제목만 추출
            line = re.sub(r'^\d+\.\s*', '', line)
            if ' - ' in line:
                line = line.split(' - ')[0].strip()
            line = line.replace('**', '').strip()
            
            if line and len(line) > 5:
                titles.append(line)
        
        return titles[:int(self.generate_slider.get())]
    
    def sanitize_filename(self, filename):
        """파일명에 사용할 수 없는 문자 제거"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        filename = filename.replace(' ', '_')
        if len(filename) > 50:
            filename = filename[:50]
        return filename
    
    def update_status(self, text, progress):
        """상태 텍스트 및 프로그레스 바 업데이트"""
        self.status_label.configure(text=text)
        self.progress_bar.set(progress)
    
    def update_blog_progress(self, text, progress):
        """블로그 작성 진행률 업데이트"""
        self.blog_progress_label.configure(text=text)
        self.blog_progress_bar.set(progress)
    
    def update_textbox(self, textbox, content):
        """텍스트박스 내용 업데이트"""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")


def main():
    app = BlogWriterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
