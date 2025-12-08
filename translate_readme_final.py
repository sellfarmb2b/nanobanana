#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 중국어를 한국어로 번역하는 최종 스크립트
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
    
    # 코드 블록이나 이미지 태그는 건너뛰기
    if '```' in text or '<img' in text or text.strip().startswith('|'):
        return text
    
    # 매우 긴 텍스트는 분할
    if len(text) > 4000:
        parts = re.split(r'([。！？\n])', text)
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
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            print(f"✓ 번역: {text[:40]}...")
            time.sleep(0.5)  # API 호출 제한 방지
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"⚠ 재시도 {attempt + 1}/{max_retries} ({wait_time}초 후)...")
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]}")
                return text

def translate_readme():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📊 총 {len(lines)}줄 처리 중...")
    
    translated_lines = []
    chinese_count = 0
    
    for i, line in enumerate(lines):
        if contains_chinese(line):
            # 목차 링크의 경우 링크 텍스트만 번역
            if line.strip().startswith('*') and '](' in line:
                # [案例 XXX：제목](#prompt-XXX) 형식 처리
                match = re.match(r'(\*\s*\[)([^\]]+)(\]\([^\)]+\))(.*)', line)
                if match:
                    prefix = match.group(1)
                    link_text = match.group(2)
                    link_url = match.group(3)
                    suffix = match.group(4) if len(match.groups()) > 3 else ''
                    
                    if contains_chinese(link_text):
                        try:
                            translator = GoogleTranslator(source='zh-CN', target='ko')
                            translated_text = translator.translate(link_text)
                            translated_lines.append(f"{prefix}{translated_text}{link_url}{suffix}")
                            print(f"✓ 목차 번역: {link_text[:40]}...")
                            time.sleep(0.3)
                            continue
                        except:
                            pass
            
            # 일반 텍스트 번역
            translated_lines.append(translate_to_korean(line))
            chinese_count += 1
        else:
            translated_lines.append(line)
        
        # 진행 상황 표시
        if (i + 1) % 500 == 0:
            print(f"진행: {i + 1}/{len(lines)}줄 ({((i+1)/len(lines)*100):.1f}%), 중국어 {chinese_count}개 발견...")
    
    print(f"💾 저장 중... (총 {chinese_count}개 중국어 텍스트 번역)")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_readme()

