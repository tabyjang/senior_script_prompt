"""
베이스 탭 클래스
모든 탭의 공통 기능을 정의합니다.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from models.project_data import ProjectData
    from services.file_service import FileService
    from services.content_generator import ContentGenerator


class BaseTab:
    """모든 탭의 베이스 클래스"""

    def __init__(
        self,
        parent: ttk.Notebook,
        project_data: "ProjectData",
        file_service: "FileService",
        content_generator: "ContentGenerator"
    ):
        """
        Args:
            parent: 부모 노트북 위젯
            project_data: ProjectData 인스턴스
            file_service: FileService 인스턴스
            content_generator: ContentGenerator 인스턴스
        """
        self.parent = parent
        self.project_data = project_data
        self.file_service = file_service
        self.content_generator = content_generator

        # 탭 프레임 생성
        self.frame = ttk.Frame(parent)
        self.parent.add(self.frame, text=self.get_tab_name())

        # UI 생성
        self.create_ui()

    def get_tab_name(self) -> str:
        """탭 이름 반환 (서브클래스에서 오버라이드)"""
        return "탭"

    def create_ui(self):
        """UI 생성 (서브클래스에서 오버라이드)"""
        pass

    def update_display(self):
        """화면 업데이트 (서브클래스에서 오버라이드)"""
        pass

    def save(self) -> bool:
        """데이터 저장 (서브클래스에서 오버라이드)"""
        return True

    def mark_unsaved(self):
        """저장되지 않은 변경사항 표시"""
        tab_id = self.__class__.__name__.lower().replace('tab', '')
        self.project_data.mark_unsaved(tab_id)
