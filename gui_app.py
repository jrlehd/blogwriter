import customtkinter as ctk
import os
import json
import threading
from tkinter import messagebox, filedialog
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

# CustomTkinter 테마 설정
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BlogTitleAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title("🚀 AI 블로그 제목 분석 & 생성")
        self.geometry("1200x800")
        
        # 결과 데이터 저장
        self.results = None
        
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
            text="🚀 AI 블로그 제목\n분석 & 생성",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f538d", "#4a9eff")
        )
        title_label.pack(pady=(30, 20))
        
        # 구분선
        separator1 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator1.pack(fill="x", padx=20, pady=10)
        
        # 키워드 입력
        keyword_label = ctk.CTkLabel(
            left_panel,
            text="🔍 분석할 키워드",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        keyword_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.keyword_entry = ctk.CTkEntry(
            left_panel,
            placeholder_text="예: 파이썬 웹 크롤링",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.keyword_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # 구분선
        separator2 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator2.pack(fill="x", padx=20, pady=15)
        
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
        self.generate_value_label.pack(pady=(0, 20), padx=20, anchor="center")
        
        # 구분선
        separator3 = ctk.CTkFrame(left_panel, height=2, fg_color=("#cccccc", "#333333"))
        separator3.pack(fill="x", padx=20, pady=15)
        
        # 분석 시작 버튼
        self.analyze_button = ctk.CTkButton(
            left_panel,
            text="🚀 분석 시작",
            command=self.start_analysis,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f538d", "#4a9eff"),
            hover_color=("#174270", "#3a7ed1")
        )
        self.analyze_button.pack(pady=10, padx=20, fill="x")
        
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
        
        # JSON 저장 버튼
        self.save_button = ctk.CTkButton(
            left_panel,
            text="💾 JSON 파일 저장",
            command=self.save_json,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=("#2d6a4f", "#52b788"),
            hover_color=("#1b4332", "#40916c"),
            state="disabled"
        )
        self.save_button.pack(pady=(0, 20), padx=20, fill="x")
        
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
        
        # 각 탭에 텍스트박스 추가
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
        
        # 탭 3: 생성된 제목
        self.generated_textbox = ctk.CTkTextbox(
            self.tabview.tab("✨ 생성된 제목"),
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.generated_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.generated_textbox.insert("1.0", "생성된 제목이 여기에 표시됩니다...")
        self.generated_textbox.configure(state="disabled")
    
    def update_search_label(self, value):
        """검색할 블로그 수 레이블 업데이트"""
        self.search_value_label.configure(text=f"{int(value)}개")
    
    def update_generate_label(self, value):
        """생성할 제목 수 레이블 업데이트"""
        self.generate_value_label.configure(text=f"{int(value)}개")
    
    def start_analysis(self):
        """분석 시작"""
        keyword = self.keyword_entry.get().strip()
        
        if not keyword:
            messagebox.showwarning("경고", "키워드를 입력해주세요!")
            return
        
        # 버튼 비활성화
        self.analyze_button.configure(state="disabled")
        self.save_button.configure(state="disabled")
        
        # 프로그레스 바 초기화
        self.progress_bar.set(0)
        self.status_label.configure(text="분석 준비 중...")
        
        # 스레드로 분석 실행 (UI 블로킹 방지)
        num_search = int(self.search_slider.get())
        num_generate = int(self.generate_slider.get())
        
        thread = threading.Thread(
            target=self.analyze_and_generate,
            args=(keyword, num_search, num_generate)
        )
        thread.daemon = True
        thread.start()
    
    def analyze_and_generate(self, keyword, num_search, num_generate):
        """블로그 제목 분석 및 생성"""
        try:
            # OpenAI API 클라이언트 초기화
            api_key = os.getenv("OPEN_AI_API_KEY")
            if not api_key:
                self.update_status("❌ OpenAI API 키가 없습니다.", 0)
                messagebox.showerror("오류", "OpenAI API 키가 .env 파일에 없습니다.")
                self.analyze_button.configure(state="normal")
                return
            
            client = OpenAI(api_key=api_key)
            
            # 1단계: 네이버 블로그 검색
            self.update_status("🔍 네이버 블로그 검색 중...", 0.1)
            blog_titles = search_naver_blog(keyword, display=num_search)
            
            if not blog_titles:
                self.update_status("❌ 검색 결과 없음", 0)
                messagebox.showerror("오류", "검색 결과가 없습니다.")
                self.analyze_button.configure(state="normal")
                return
            
            self.update_status(f"✅ {len(blog_titles)}개 블로그 제목 수집 완료", 0.3)
            
            # 검색 결과 표시
            search_result = f"'{keyword}' 검색 결과 ({len(blog_titles)}개)\n\n"
            search_result += "=" * 50 + "\n\n"
            for idx, title in enumerate(blog_titles, 1):
                search_result += f"{idx}. {title}\n\n"
            
            self.update_textbox(self.search_textbox, search_result)
            
            # 2단계: GPT 분석
            self.update_status("🤖 ChatGPT로 제목 분석 중...", 0.4)
            
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
            
            # 분석 결과 표시
            self.update_textbox(self.analysis_textbox, analysis_result)
            
            # 3단계: 새로운 제목 생성
            self.update_status(f"✨ 새로운 제목 {num_generate}개 생성 중...", 0.7)
            
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
            self.update_status("✅ 제목 생성 완료!", 0.9)
            
            # 생성된 제목 표시
            self.update_textbox(self.generated_textbox, generated_titles)
            
            # 결과 저장
            self.results = {
                "keyword": keyword,
                "original_titles": blog_titles,
                "analysis": analysis_result,
                "generated_titles": generated_titles
            }
            
            # 완료
            self.update_status("🎉 모든 작업 완료!", 1.0)
            self.save_button.configure(state="normal")
            messagebox.showinfo("완료", "분석이 완료되었습니다!\n각 탭에서 결과를 확인하세요.")
            
        except Exception as e:
            self.update_status(f"❌ 오류 발생", 0)
            messagebox.showerror("오류", f"오류가 발생했습니다:\n{str(e)}")
        
        finally:
            self.analyze_button.configure(state="normal")
    
    def update_status(self, text, progress):
        """상태 텍스트 및 프로그레스 바 업데이트"""
        self.status_label.configure(text=text)
        self.progress_bar.set(progress)
    
    def update_textbox(self, textbox, content):
        """텍스트박스 내용 업데이트"""
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", content)
        textbox.configure(state="disabled")
    
    def save_json(self):
        """JSON 파일 저장"""
        if not self.results:
            messagebox.showwarning("경고", "저장할 결과가 없습니다!")
            return
        
        # 파일 저장 다이얼로그
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"blog_analysis_{self.results['keyword']}.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("성공", f"파일이 저장되었습니다!\n{file_path}")
            except Exception as e:
                messagebox.showerror("오류", f"파일 저장 중 오류 발생:\n{str(e)}")


def main():
    app = BlogTitleAnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()

