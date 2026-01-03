#!/usr/bin/env python3
"""
프로젝트 뷰어/에디터 - 메인 진입점
모듈화된 안전하고 튼튼한 구조로 재작성된 버전
"""

import os
import sys

# TensorFlow 경고 메시지 숨기기
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tkinter as tk
from pathlib import Path
import argparse
from tkinter import filedialog, messagebox

# 드래그 앤 드롭 지원
try:
    from tkinterdnd2 import TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# 모듈 import
from config.config_manager import ConfigManager
from models.project_data import ProjectData
from services.file_service import FileService
from services.llm_service import LLMService
from services.content_generator import ContentGenerator
from gui.main_window import MainWindow


def main():
    """메인 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description="프로젝트 뷰어/에디터")
    parser.add_argument(
        '--project',
        default=None,
        help='프로젝트 경로 (지정하지 않으면 마지막 프로젝트 또는 기본값 사용)'
    )
    args = parser.parse_args()

    # 설정 관리자 생성
    config_manager = ConfigManager()

    # 프로젝트 경로 결정
    project_path = None
    
    # 1. 명령줄 인자로 프로젝트 경로가 지정된 경우
    if args.project:
        project_path = Path(args.project)
    else:
        # 2. 설정 파일에서 마지막 프로젝트 경로 읽기
        last_project_path = config_manager.get_last_project_path()
        if last_project_path:
            last_path = Path(last_project_path)
            if last_path.exists() and (last_path / "synopsis.json").exists():
                project_path = last_path
                print(f"[프로젝트 로드] 마지막 프로젝트 자동 로드: {project_path}")
    
    # 3. 프로젝트 경로가 없거나 유효하지 않은 경우 기본값 사용
    # 3. 프로젝트 경로가 없거나 유효하지 않은 경우:
    #    더 이상 임의의 기본 폴더로 저장하지 않고, 사용자가 프로젝트 폴더를 선택하도록 강제
    if project_path is None or not project_path.exists():
        # Tk 초기화(폴더 선택 다이얼로그용)
        picker_root = tk.Tk()
        picker_root.withdraw()
        picker_root.update_idletasks()

        messagebox.showinfo(
            "프로젝트 선택",
            "작업할 프로젝트 폴더를 선택해주세요.\n\n"
            "선택한 폴더 안에서만 저장/로딩이 수행됩니다."
        )

        # 처음 폴더 로딩 시 기본 위치를 01_man 폴더로 설정
        initial_dir = None
        try:
            last_project_path = config_manager.get_last_project_path()
            if last_project_path and Path(last_project_path).exists():
                # 마지막 프로젝트가 있으면 그 부모(대개 01_man)로
                initial_dir = str(Path(last_project_path).resolve().parent)
        except Exception:
            initial_dir = None

        if not initial_dir:
            try:
                # editors_app/main.py 기준: .../01_man/editors_app/main.py -> parent of editors_app is 01_man
                candidate = Path(__file__).resolve().parent.parent
                if candidate.exists():
                    initial_dir = str(candidate)
            except Exception:
                initial_dir = None

        selected_dir = filedialog.askdirectory(
            title="프로젝트 폴더 선택",
            initialdir=initial_dir
        )
        picker_root.destroy()

        if not selected_dir:
            print("[프로젝트 로드] 프로젝트 선택이 취소되었습니다. 종료합니다.")
            return

        project_path = Path(selected_dir)
        print(f"[프로젝트 로드] 사용자 선택 프로젝트: {project_path}")
        # 다음 실행을 위해 저장
        config_manager.set_last_project_path(str(project_path))
    
    # 프로젝트 경로를 절대 경로로 변환
    if not project_path.is_absolute():
        project_path = (Path(os.getcwd()) / project_path).resolve()

    # 프로젝트 데이터 모델 생성
    project_data = ProjectData(str(project_path))

    # 파일 서비스 생성
    file_service = FileService(project_path)

    # LLM 서비스 생성
    llm_service = LLMService(config_manager)

    # 콘텐츠 생성 서비스 생성
    content_generator = ContentGenerator(llm_service)

    # Tkinter root 생성 (드래그 앤 드롭 지원)
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    # 메인 윈도우 생성
    app = MainWindow(
        root,
        project_path,
        config_manager,
        project_data,
        file_service,
        content_generator
    )

    # 메인 루프 실행
    root.mainloop()


if __name__ == "__main__":
    main()
