#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 사례 목차 부분만 번역하는 스크립트
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
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            print(f"✓ 번역: {text[:40]}... -> {translated[:40]}...")
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⚠ 재시도 {attempt + 1}/{max_retries} ({wait_time}초 후)...")
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]}")
                return text

def translate_toc():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 목차 시작 라인 찾기 (35번 라인: "## 📖 사례 목차")
    toc_start = 35  # 0-based index이므로 34
    toc_end = None
    
    # 목차 끝 찾기 (다음 섹션 시작 전까지, "---" 또는 다음 "##" 전까지)
    for i in range(toc_start, len(lines)):
        if lines[i].strip() == '---' or (lines[i].startswith('## ') and '点击' not in lines[i]):
            toc_end = i
            break
    
    if toc_end is None:
        toc_end = len(lines)
    
    print(f"📊 목차 범위: {toc_start+1}번 라인부터 {toc_end}번 라인까지")
    
    translated_lines = []
    
    # 목차 이전 부분은 그대로
    translated_lines.extend(lines[:toc_start])
    
    # 목차 헤더는 그대로
    translated_lines.append(lines[toc_start])
    
    # 목차 항목들 번역
    for i in range(toc_start + 1, toc_end):
        line = lines[i]
        
        # 링크 형식: [사례 XXX：中文内容 ](#prompt-XXX)
        match = re.match(r'^(\*   \[사례 \d+：)([^\]]+)(\]\(#prompt-\d+\)\s*)$', line)
        if match:
            prefix = match.group(1)
            chinese_text = match.group(2)
            suffix = match.group(3)
            
            if contains_chinese(chinese_text):
                translated_text = translate_to_korean(chinese_text.strip())
                translated_line = f"{prefix}{translated_text}{suffix}\n"
                translated_lines.append(translated_line)
            else:
                translated_lines.append(line)
        else:
            translated_lines.append(line)
    
    # 나머지 부분은 그대로
    translated_lines.extend(lines[toc_end:])
    
    print(f"💾 저장 중: {input_file}")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_toc()
