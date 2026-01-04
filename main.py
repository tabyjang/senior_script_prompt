#!/usr/bin/env python3
"""
프로젝트 뷰어/에디터 - 메인 진입점
prompts 폴더 기반 프로젝트 선택 시스템
"""

import os
import sys

# TensorFlow 경고 메시지 숨기기
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tkinter as tk
from pathlib import Path
import argparse

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


def find_prompts_folder() -> Path:
    """prompts 폴더 찾기"""
    # 현재 스크립트 위치 기준으로 prompts 폴더 찾기
    current_file = Path(__file__).resolve()
    current_dir = current_file.parent

    # 1. 현재 폴더에 prompts가 있는 경우
    prompts_here = current_dir / "prompts"
    if prompts_here.exists():
        return prompts_here

    # 2. 상위 폴더에서 찾기
    for parent in current_dir.parents:
        prompts_in_parent = parent / "prompts"
        if prompts_in_parent.exists():
            return prompts_in_parent

    # 3. 현재 작업 디렉토리에서 찾기
    cwd_prompts = Path.cwd() / "prompts"
    if cwd_prompts.exists():
        return cwd_prompts

    # 찾지 못하면 현재 폴더에 prompts 폴더 생성
    prompts_here.mkdir(parents=True, exist_ok=True)
    return prompts_here


def main():
    """메인 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description="시니어 콘텐츠 에디터")
    parser.add_argument(
        '--prompts',
        default=None,
        help='prompts 폴더 경로 (지정하지 않으면 자동 탐색)'
    )
    args = parser.parse_args()

    # 설정 관리자 생성
    config_manager = ConfigManager()

    # prompts 폴더 경로 결정
    if args.prompts:
        prompts_path = Path(args.prompts)
    else:
        prompts_path = find_prompts_folder()

    print(f"[시작] prompts 폴더: {prompts_path}")

    # 초기 프로젝트 경로 (빈 경로로 시작, MainWindow에서 선택)
    initial_project_path = prompts_path

    # 프로젝트 데이터 모델 생성
    project_data = ProjectData(str(initial_project_path))

    # 파일 서비스 생성
    file_service = FileService(initial_project_path)

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
        prompts_path,  # prompts 폴더 경로 전달
        config_manager,
        project_data,
        file_service,
        content_generator
    )

    # 메인 루프 실행
    root.mainloop()


if __name__ == "__main__":
    main()
