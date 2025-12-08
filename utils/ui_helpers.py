"""
UI 헬퍼 함수
Tkinter UI 관련 유틸리티 함수를 제공합니다.
"""

import tkinter as tk
from typing import Callable


def bind_mousewheel_to_canvas(canvas: tk.Canvas, frame: tk.Frame):
    """
    Canvas와 모든 자식 위젯에 마우스 휠 이벤트 바인딩

    Args:
        canvas: 스크롤할 Canvas 위젯
        frame: Canvas 내부의 Frame 위젯
    """
    def on_mousewheel(event):
        # Windows와 Linux 모두 지원
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, 'delta') and event.delta < 0):
            canvas.yview_scroll(1, "units")
        return "break"

    def bind_to_widget(widget):
        # Windows
        widget.bind("<MouseWheel>", on_mousewheel)
        # Linux
        widget.bind("<Button-4>", on_mousewheel)
        widget.bind("<Button-5>", on_mousewheel)
        # 모든 자식 위젯에도 재귀적으로 바인딩
        for child in widget.winfo_children():
            bind_to_widget(child)

    # Canvas와 Frame에 모두 바인딩
    canvas.bind("<MouseWheel>", on_mousewheel)
    canvas.bind("<Button-4>", on_mousewheel)
    canvas.bind("<Button-5>", on_mousewheel)
    canvas.bind("<Enter>", lambda e: canvas.focus_set())
    bind_to_widget(frame)


def center_window(window: tk.Tk, width: int = None, height: int = None):
    """
    윈도우를 화면 중앙에 배치

    Args:
        window: Tkinter 윈도우
        width: 윈도우 너비 (None이면 현재 크기 유지)
        height: 윈도우 높이 (None이면 현재 크기 유지)
    """
    window.update_idletasks()

    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def create_scrollable_frame(parent: tk.Widget) -> tuple[tk.Canvas, tk.Frame, tk.Scrollbar]:
    """
    스크롤 가능한 프레임 생성

    Args:
        parent: 부모 위젯

    Returns:
        (canvas, frame, scrollbar) 튜플
    """
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 마우스 휠 바인딩
    bind_mousewheel_to_canvas(canvas, scrollable_frame)

    return canvas, scrollable_frame, scrollbar


def show_auto_close_dialog(parent: tk.Tk, title: str, message: str, auto_close_seconds: int = 5):
    """
    자동으로 닫히는 다이얼로그 표시

    Args:
        parent: 부모 윈도우
        title: 다이얼로그 제목
        message: 표시할 메시지
        auto_close_seconds: 자동으로 닫힐 시간 (초)
    """
    import tkinter.ttk as ttk

    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("400x150")
    dialog.transient(parent)
    dialog.grab_set()

    # 중앙에 배치
    center_window(dialog, 400, 150)

    # 메시지 표시
    msg_label = ttk.Label(
        dialog,
        text=message,
        font=("맑은 고딕", 10),
        wraplength=380,
        justify=tk.CENTER
    )
    msg_label.pack(pady=20, padx=20)

    # 남은 시간 표시
    time_label = ttk.Label(
        dialog,
        text=f"{auto_close_seconds}초 후 자동으로 닫힙니다...",
        font=("맑은 고딕", 9),
        foreground="gray"
    )
    time_label.pack(pady=5)

    # 확인 버튼
    ok_button = ttk.Button(
        dialog,
        text="확인",
        command=dialog.destroy
    )
    ok_button.pack(pady=10)

    # 자동 닫기 로직
    def countdown(remaining):
        if remaining > 0:
            time_label.config(text=f"{remaining}초 후 자동으로 닫힙니다...")
            dialog.after(1000, lambda: countdown(remaining - 1))
        else:
            dialog.destroy()

    # 카운트다운 시작
    dialog.after(1000, lambda: countdown(auto_close_seconds - 1))
