#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 중국어를 한국어로 번역하는 개선된 스크립트
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
    
    # 코드 블록이나 링크는 건너뛰기
    if '```' in text or re.search(r'\[.*?\]\(.*?\)', text):
        # 링크 텍스트만 번역
        def translate_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            if contains_chinese(link_text):
                translated_text = translate_to_korean(link_text, max_retries)
                return f"[{translated_text}]({link_url})"
            return match.group(0)
        
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', translate_link, text)
        return text
    
    # 매우 긴 텍스트는 분할
    if len(text) > 4000:
        return translate_long_text(text, max_retries)
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            print(f"✓ 번역: {text[:40]}...")
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⚠ 재시도 {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                print(f"✗ 실패: {str(e)[:50]}")
                return text

def translate_long_text(text, max_retries=3):
    """긴 텍스트를 문장 단위로 나누어 번역"""
    # 문장 구분자로 분할
    parts = re.split(r'([。！？\n]+)', text)
    translated_parts = []
    
    current_chunk = ""
    for part in parts:
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
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 파일 크기: {len(content)}자")
    
    # 중국어가 포함된 줄 찾기
    lines = content.split('\n')
    translated_lines = []
    
    for i, line in enumerate(lines):
        if contains_chinese(line):
            # 코드 블록 내부는 건너뛰기
            if line.strip().startswith('```'):
                translated_lines.append(line)
                continue
            
            # 마크다운 링크 처리
            if '](' in line:
                # 링크 텍스트만 번역
                def translate_link_text(match):
                    link_text = match.group(1)
                    link_url = match.group(2)
                    anchor = match.group(3) if match.lastindex >= 3 else ''
                    if contains_chinese(link_text):
                        try:
                            translator = GoogleTranslator(source='zh-CN', target='ko')
                            translated_text = translator.translate(link_text)
                            return f"[{translated_text}]({link_url}{anchor})"
                        except:
                            return match.group(0)
                    return match.group(0)
                
                line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)(\s*#.*?)?', translate_link_text, line)
                
                # 링크 외의 텍스트도 번역
                if contains_chinese(line):
                    translated_lines.append(translate_to_korean(line))
                else:
                    translated_lines.append(line)
            else:
                translated_lines.append(translate_to_korean(line))
        else:
            translated_lines.append(line)
        
        # 진행 상황 표시
        if (i + 1) % 200 == 0:
            print(f"진행: {i + 1}/{len(lines)}줄 ({((i+1)/len(lines)*100):.1f}%)...")
    
    print(f"💾 저장 중...")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(translated_lines))
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_readme()

