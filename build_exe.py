"""
PyInstaller를 사용하여 exe 파일을 생성하는 스크립트
"""
import subprocess
import os
import sys

def build_exe():
    """exe 파일 생성"""
    print("=" * 60)
    print("🚀 EXE 파일 생성 시작")
    print("=" * 60)
    
    # PyInstaller 명령어 구성
    cmd = [
        "pyinstaller",
        "--onefile",                    # 단일 exe 파일로 생성
        "--windowed",                   # 콘솔 창 숨기기 (GUI 앱)
        "--name=BlogTitleAnalyzer",     # exe 파일 이름
        "--clean",                      # 빌드 전 캐시 정리
        "--noconfirm",                  # 기존 파일 덮어쓰기
        "gui_app.py"                    # 메인 스크립트
    ]
    
    print("\n📦 빌드 명령어:")
    print(" ".join(cmd))
    print("\n⏳ 빌드 중... (몇 분 정도 걸릴 수 있습니다)\n")
    
    try:
        # PyInstaller 실행
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 60)
        print("✅ EXE 파일 생성 완료!")
        print("=" * 60)
        print(f"\n📁 생성된 파일 위치: dist\\BlogTitleAnalyzer.exe")
        print("\n⚠️  중요: .env 파일을 exe 파일과 같은 폴더에 넣어주세요!")
        print("   (API 키가 필요하기 때문입니다)\n")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 빌드 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()


