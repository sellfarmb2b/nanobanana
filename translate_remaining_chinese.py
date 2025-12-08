#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일에 남은 중국어를 찾아서 번역하는 스크립트
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
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            time.sleep(delay)
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]} | 원문: {text[:50]}")
                return text

def translate_remaining_chinese():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 총 {len(lines)}줄 확인 중...")
    
    translated_lines = []
    chinese_count = 0
    changed_count = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # "豆包" -> "두바오" 번역
        if '豆包' in line:
            line = line.replace('豆包', '두바오')
            changed_count += 1
            print(f"✓ [{i+1}] '豆包' -> '두바오' 변환")
        
        if contains_chinese(line):
            chinese_count += 1
            
            # 코드 블록, 이미지 태그, 표는 건너뛰기
            if '```' in line or '<img' in line or line.strip().startswith('|') or line.strip().startswith('<div'):
                translated_lines.append(line)
                continue
            
            # 일본어 한자도 포함될 수 있으므로 주의
            # "见下ろし" 같은 경우는 일본어이므로 그대로 유지
            if '见下ろし' in line or '向ぎ见' in line:
                translated_lines.append(line)
                continue
            
            # 나머지 중국어 번역
            translated = translate_text(line, delay=0.3)
            if translated != line:
                changed_count += 1
                print(f"✓ [{i+1}] 번역: {line[:60].strip()}...")
            translated_lines.append(translated)
        else:
            translated_lines.append(line)
        
        if (i + 1) % 500 == 0:
            print(f"📈 진행: {i + 1}/{len(lines)}줄... (중국어 {chinese_count}개 발견, {changed_count}개 변경)")
    
    print(f"\n💾 저장 중... (총 {chinese_count}개 중국어 발견, {changed_count}개 번역/변경)")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_remaining_chinese()
