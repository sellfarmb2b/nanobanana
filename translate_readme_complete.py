#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 모든 중국어를 한국어로 번역하는 완전한 스크립트
"""

import re
import time
from deep_translator import GoogleTranslator

def contains_chinese(text):
    """텍스트에 중국어 문자가 포함되어 있는지 확인"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]+', text))

def translate_to_korean(text, max_retries=3, delay=0.5):
    """중국어가 포함된 텍스트를 한국어로 번역"""
    if not contains_chinese(text):
        return text
    
    # 코드 블록, 이미지 태그, 표는 건너뛰기
    if '```' in text or '<img' in text or text.strip().startswith('|') or text.strip().startswith('<div'):
        return text
    
    # 매우 긴 텍스트는 분할
    if len(text) > 4000:
        return translate_long_text(text, max_retries, delay)
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            time.sleep(delay)  # API 호출 제한 방지
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⚠ 재시도 {attempt + 1}/{max_retries} ({wait_time}초 후)...")
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]}")
                return text

def translate_long_text(text, max_retries=3, delay=0.5):
    """긴 텍스트를 문장 단위로 나누어 번역"""
    sentences = re.split(r'([。！？\n])', text)
    translated_parts = []
    current_chunk = ""
    
    for part in sentences:
        if len(current_chunk + part) < 3500:
            current_chunk += part
        else:
            if current_chunk:
                translated_parts.append(translate_to_korean(current_chunk, max_retries, delay))
            current_chunk = part
    
    if current_chunk:
        translated_parts.append(translate_to_korean(current_chunk, max_retries, delay))
    
    return ''.join(translated_parts)

def translate_line(line):
    """한 줄을 번역 (특수 케이스 처리 포함)"""
    if not contains_chinese(line):
        return line
    
    # 코드 블록 시작/끝은 건너뛰기
    if line.strip().startswith('```'):
        return line
    
    # 이미 번역된 목차는 건너뛰기 (이미 한국어로 되어 있음)
    if line.strip().startswith('*   [사례'):
        return line
    
    # 사례 제목 형식: ## 案例 XXX：제목 (来源 ...) 模型：...
    case_title_match = re.match(r'^(##\s+案例\s+\d+：)(.+?)(\s*\(来源\s+)(.+?)(\)\s+模型：)(.+?)$', line)
    if case_title_match:
        prefix = case_title_match.group(1)
        title = case_title_match.group(2)
        source_prefix = case_title_match.group(3)
        source = case_title_match.group(4)
        model_prefix = case_title_match.group(5)
        model = case_title_match.group(6)
        
        # 제목만 번역
        translated_title = translate_to_korean(title, delay=0.3)
        translated_source_prefix = translate_to_korean("来源", delay=0.1)  # "출처"
        translated_model_prefix = translate_to_korean("模型", delay=0.1)  # "모델"
        
        return f"## 사례 {case_title_match.group(1).split('案例')[1].split('：')[0]}：{translated_title} ({translated_source_prefix} {source}) {translated_model_prefix}：{model}"
    
    # 일반 사례 제목 (간단한 형식)
    simple_case_match = re.match(r'^(##\s+案例\s+\d+：)(.+)$', line)
    if simple_case_match:
        case_num = re.search(r'\d+', simple_case_match.group(1)).group()
        title = simple_case_match.group(2)
        translated_title = translate_to_korean(title, delay=0.3)
        return f"## 사례 {case_num}：{translated_title}"
    
    # 링크가 포함된 경우
    if '](' in line:
        # 링크 텍스트만 번역
        def translate_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            if contains_chinese(link_text):
                translated = translate_to_korean(link_text, delay=0.2)
                return f"[{translated}]({link_url})"
            return match.group(0)
        
        line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', translate_link, line)
        
        # 링크 외의 텍스트도 번역
        if contains_chinese(line):
            return translate_to_korean(line, delay=0.3)
        return line
    
    # 일반 텍스트 번역
    return translate_to_korean(line, delay=0.3)

def translate_readme_complete():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 총 {len(lines)}줄 처리 중...")
    
    translated_lines = []
    chinese_count = 0
    translated_count = 0
    
    for i, line in enumerate(lines):
        if contains_chinese(line):
            chinese_count += 1
            translated = translate_line(line)
            if translated != line:
                translated_count += 1
                print(f"✓ [{i+1}/{len(lines)}] 번역: {line[:50].strip()}... -> {translated[:50].strip()}...")
            translated_lines.append(translated)
        else:
            translated_lines.append(line)
        
        # 진행 상황 표시
        if (i + 1) % 100 == 0:
            progress = ((i + 1) / len(lines)) * 100
            print(f"📈 진행: {i + 1}/{len(lines)}줄 ({progress:.1f}%), 중국어 {chinese_count}개 발견, {translated_count}개 번역 완료...")
    
    print(f"\n💾 저장 중... (총 {chinese_count}개 중국어 텍스트 발견, {translated_count}개 번역 완료)")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_readme_complete()
