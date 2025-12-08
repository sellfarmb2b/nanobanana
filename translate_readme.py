#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 중국어를 한국어로 번역하는 스크립트
"""

import re
import time
from deep_translator import GoogleTranslator

def contains_chinese(text):
    """텍스트에 중국어 문자가 포함되어 있는지 확인"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]+', text))

def translate_to_korean(text, max_retries=3):
    """중국어가 포함된 텍스트를 한국어로 번역"""
    if not contains_chinese(text):
        return text
    
    # 매우 긴 텍스트는 분할
    if len(text) > 4000:
        return translate_long_text(text, max_retries)
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            print(f"✓ 번역 완료: {text[:50]}...")
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⚠ 재시도 {attempt + 1}/{max_retries} ({wait_time}초 후)...")
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]}")
                return text

def translate_long_text(text, max_retries=3):
    """긴 텍스트를 문장 단위로 나누어 번역"""
    # 마크다운 링크나 코드 블록을 보존하면서 분할
    sentences = re.split(r'([。！？\n])', text)
    translated_parts = []
    
    current_chunk = ""
    for part in sentences:
        if len(current_chunk + part) < 3500:
            current_chunk += part
        else:
            if current_chunk:
                translated_parts.append(translate_to_korean(current_chunk, max_retries))
            current_chunk = part
    
    if current_chunk:
        translated_parts.append(translate_to_korean(current_chunk, max_retries))
    
    return ''.join(translated_parts)

def translate_readme():
    input_file = 'README.md'
    output_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 총 {len(lines)}줄 처리 중...")
    
    translated_lines = []
    current_paragraph = ""
    
    for i, line in enumerate(lines):
        # 마크다운 링크나 코드 블록은 그대로 유지
        if line.strip().startswith('```') or line.strip().startswith('|') or '`' in line:
            # 현재 단락이 있으면 먼저 번역
            if current_paragraph and contains_chinese(current_paragraph):
                translated_lines.append(translate_to_korean(current_paragraph))
                current_paragraph = ""
            translated_lines.append(line)
            continue
        
        # 중국어가 포함된 줄인지 확인
        if contains_chinese(line):
            # 단락이 계속되는 경우
            if line.strip() and not line.strip().startswith('#'):
                current_paragraph += line
            else:
                # 현재 단락 번역
                if current_paragraph and contains_chinese(current_paragraph):
                    translated_lines.append(translate_to_korean(current_paragraph))
                    current_paragraph = ""
                # 헤더나 빈 줄은 바로 번역
                translated_lines.append(translate_to_korean(line))
        else:
            # 현재 단락이 있으면 먼저 번역
            if current_paragraph and contains_chinese(current_paragraph):
                translated_lines.append(translate_to_korean(current_paragraph))
                current_paragraph = ""
            translated_lines.append(line)
        
        # 진행 상황 표시
        if (i + 1) % 100 == 0:
            print(f"진행: {i + 1}/{len(lines)}줄...")
    
    # 마지막 단락 처리
    if current_paragraph and contains_chinese(current_paragraph):
        translated_lines.append(translate_to_korean(current_paragraph))
    
    print(f"💾 저장 중: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_readme()

