#!/usr/bin/env python3
"""
프로젝트 뷰어/에디터 - 메인 진입점
모듈화된 안전하고 튼튼한 구조로 재작성된 버전
"""

import sys
import tkinter as tk
from pathlib import Path
import argparse

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
        default='../001_gym_romance',
        help='프로젝트 경로 (기본값: ../001_gym_romance)'
    )
    args = parser.parse_args()

    # 프로젝트 경로 설정
    project_path = Path(args.project)

    # 설정 관리자 생성
    config_manager = ConfigManager()

    # 프로젝트 데이터 모델 생성
    project_data = ProjectData(str(project_path))

    # 파일 서비스 생성
    file_service = FileService(project_path)

    # LLM 서비스 생성
    llm_service = LLMService(config_manager)

    # 콘텐츠 생성 서비스 생성
    content_generator = ContentGenerator(llm_service)

    # Tkinter root 생성
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
