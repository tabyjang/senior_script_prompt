"""
Word 파일을 Markdown으로 변환하는 유틸리티
mammoth 라이브러리를 사용하여 .docx 파일을 .md 파일로 변환합니다.
"""

from pathlib import Path
from typing import Optional, Tuple
import re


def convert_word_to_markdown(word_path: str, output_path: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Word 파일(.docx)을 Markdown 파일(.md)로 변환

    Args:
        word_path: Word 파일 경로
        output_path: 출력 Markdown 파일 경로 (없으면 자동 생성)

    Returns:
        Tuple[bool, str, str]: (성공 여부, 결과 메시지, 출력 파일 경로)
    """
    try:
        import mammoth
    except ImportError:
        return False, "mammoth 라이브러리가 설치되어 있지 않습니다.\npip install mammoth", ""

    word_file = Path(word_path)

    # 파일 존재 확인
    if not word_file.exists():
        return False, f"파일을 찾을 수 없습니다: {word_path}", ""

    # 확장자 확인
    if word_file.suffix.lower() not in ['.docx', '.doc']:
        return False, f"지원하지 않는 파일 형식입니다: {word_file.suffix}\n.docx 또는 .doc 파일만 지원합니다.", ""

    # .doc 파일 경고
    if word_file.suffix.lower() == '.doc':
        return False, ".doc 형식은 지원되지 않습니다.\n파일을 .docx 형식으로 저장 후 다시 시도해주세요.", ""

    # 출력 경로 결정
    if output_path:
        md_file = Path(output_path)
    else:
        md_file = word_file.with_suffix('.md')

    try:
        # Word 파일 읽기 및 변환
        with open(word_file, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            markdown_content = result.value
            messages = result.messages

        # 변환 경고 메시지 처리
        warning_msgs = []
        for msg in messages:
            if hasattr(msg, 'message'):
                warning_msgs.append(str(msg.message))

        # Markdown 후처리
        markdown_content = _post_process_markdown(markdown_content)

        # 파일 저장
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # 결과 메시지 생성
        result_msg = f"변환 완료!\n\n입력: {word_file.name}\n출력: {md_file.name}"
        if warning_msgs:
            result_msg += f"\n\n경고:\n" + "\n".join(warning_msgs[:5])
            if len(warning_msgs) > 5:
                result_msg += f"\n... 외 {len(warning_msgs) - 5}개"

        return True, result_msg, str(md_file)

    except Exception as e:
        return False, f"변환 중 오류 발생:\n{str(e)}", ""


def _post_process_markdown(content: str) -> str:
    """
    Markdown 후처리
    - 불필요한 빈 줄 정리
    - 줄바꿈 정규화
    """
    # 연속된 빈 줄을 최대 2줄로 제한
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    # 앞뒤 공백 제거
    content = content.strip()

    # 마지막에 줄바꿈 추가
    content += '\n'

    return content


def get_markdown_preview(word_path: str, max_chars: int = 2000) -> Tuple[bool, str]:
    """
    Word 파일의 Markdown 미리보기 생성 (저장하지 않음)

    Args:
        word_path: Word 파일 경로
        max_chars: 미리보기 최대 문자 수

    Returns:
        Tuple[bool, str]: (성공 여부, 미리보기 내용 또는 에러 메시지)
    """
    try:
        import mammoth
    except ImportError:
        return False, "mammoth 라이브러리가 설치되어 있지 않습니다."

    word_file = Path(word_path)

    if not word_file.exists():
        return False, f"파일을 찾을 수 없습니다: {word_path}"

    if word_file.suffix.lower() != '.docx':
        return False, f"지원하지 않는 파일 형식입니다: {word_file.suffix}"

    try:
        with open(word_file, "rb") as docx_file:
            result = mammoth.convert_to_markdown(docx_file)
            markdown_content = result.value

        markdown_content = _post_process_markdown(markdown_content)

        # 미리보기 길이 제한
        if len(markdown_content) > max_chars:
            preview = markdown_content[:max_chars] + "\n\n... (이하 생략)"
        else:
            preview = markdown_content

        return True, preview

    except Exception as e:
        return False, f"미리보기 생성 중 오류:\n{str(e)}"
