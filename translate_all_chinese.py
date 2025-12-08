#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 모든 중국어를 한국어로 번역하는 스크립트
"""

import re
import time
from deep_translator import GoogleTranslator

def contains_chinese(text):
    """텍스트에 중국어 문자가 포함되어 있는지 확인"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]+', text))

def translate_text(text, max_retries=3, delay=0.5):
    """중국어 텍스트를 한국어로 번역"""
    if not contains_chinese(text):
        return text
    
    # 빈 텍스트나 공백만 있는 경우
    if not text.strip():
        return text
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            time.sleep(delay)
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⚠ 재시도 {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]}")
                return text

def translate_all_chinese():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 총 {len(lines)}줄 확인 중...")
    
    translated_lines = []
    chinese_lines = []
    total_chinese_count = 0
    
    # 먼저 중국어가 포함된 줄들을 찾기
    for i, line in enumerate(lines):
        if contains_chinese(line):
            chinese_lines.append((i, line))
            total_chinese_count += len(re.findall(r'[\u4e00-\u9fff]', line))
    
    print(f"🔍 중국어가 포함된 줄: {len(chinese_lines)}개 (총 {total_chinese_count}개 문자)")
    
    # 각 줄 처리
    changed_count = 0
    skip_patterns = [
        r'^```',  # 코드 블록
        r'<img',  # 이미지 태그
        r'^\|',   # 표
        r'^<div', # div 태그
    ]
    
    for i, line in enumerate(lines):
        should_skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line):
                should_skip = True
                break
        
        if should_skip:
            translated_lines.append(line)
            continue
        
        if contains_chinese(line):
            # 중국어 부분만 추출하여 번역
            chinese_parts = re.findall(r'[\u4e00-\u9fff]+', line)
            
            if chinese_parts:
                # 전체 줄을 번역
                translated = translate_text(line, delay=0.3)
                if translated != line:
                    changed_count += 1
                    if changed_count <= 20 or changed_count % 50 == 0:
                        print(f"✓ [{i+1}/{len(lines)}] {line[:50].strip()}... -> {translated[:50].strip()}...")
                translated_lines.append(translated)
            else:
                translated_lines.append(line)
        else:
            translated_lines.append(line)
        
        if (i + 1) % 1000 == 0:
            progress = ((i + 1) / len(lines)) * 100
            print(f"📈 진행: {i + 1}/{len(lines)}줄 ({progress:.1f}%), {changed_count}개 번역 완료...")
    
    print(f"\n💾 저장 중... (총 {changed_count}개 줄 번역 완료)")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_all_chinese()
