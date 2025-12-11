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
    if project_path is None or not project_path.exists():
        default_path = Path("../001_gym_romance")
        if default_path.exists():
            project_path = default_path
            print(f"[프로젝트 로드] 기본 프로젝트 사용: {project_path}")
        else:
            # 기본 경로도 없으면 현재 디렉토리 기준으로 상대 경로 생성
            import os
            current_dir = Path(os.getcwd())
            # editors_app에서 실행 중이면 상위 폴더로
            if current_dir.name == "editors_app":
                project_path = current_dir.parent / "001_gym_romance"
            else:
                project_path = default_path
            print(f"[프로젝트 로드] 프로젝트 경로 설정: {project_path}")
    
    # 프로젝트 경로를 절대 경로로 변환
    if not project_path.is_absolute():
        import os
        project_path = (Path(os.getcwd()) / project_path).resolve()

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
