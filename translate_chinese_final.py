#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 중국어를 효율적으로 한국어로 번역
"""

import re
import time
from deep_translator import GoogleTranslator

def contains_chinese(text):
    """텍스트에 중국어 문자가 포함되어 있는지 확인 (일본어 한자 제외)"""
    if not isinstance(text, str):
        return False
    # 일본어 특수 문자 패턴은 제외
    japanese_patterns = ['向ぎ见', '见下ろし', '見下ろし']
    for pattern in japanese_patterns:
        if pattern in text:
            # 일본어 부분을 임시로 제거하고 검사
            text = text.replace(pattern, '')
    return bool(re.search(r'[\u4e00-\u9fff]+', text))

def translate_text(text, max_retries=3, delay=0.3):
    """중국어 텍스트를 한국어로 번역"""
    if not contains_chinese(text):
        return text
    
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
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]}")
                return text

def translate_chinese_in_content(content):
    """콘텐츠 내의 중국어를 번역"""
    lines = content.split('\n')
    translated_lines = []
    changed_count = 0
    
    skip_patterns = [
        (r'^```', '코드 블록'),
        (r'^\|', '표'),
        (r'^<div', 'div 태그'),
    ]
    
    for i, line in enumerate(lines):
        # 건너뛸 패턴 확인
        should_skip = False
        skip_reason = ''
        for pattern, reason in skip_patterns:
            if re.match(pattern, line):
                should_skip = True
                skip_reason = reason
                break
        
        # 이미지 alt 텍스트는 건너뛰기 (선택적)
        if '<img' in line and 'alt=' in line:
            # alt 속성 내의 중국어만 번역
            def translate_alt(match):
                alt_content = match.group(1)
                if contains_chinese(alt_content):
                    translated_alt = translate_text(alt_content, delay=0.2)
                    return f'alt="{translated_alt}"'
                return match.group(0)
            
            line = re.sub(r'alt="([^"]+)"', translate_alt, line)
            translated_lines.append(line)
            if line != lines[i]:
                changed_count += 1
            continue
        
        if should_skip:
            translated_lines.append(line)
            continue
        
        if contains_chinese(line):
            translated = translate_text(line, delay=0.3)
            if translated != line:
                changed_count += 1
                if changed_count <= 30 or changed_count % 50 == 0:
                    print(f"✓ [{i+1}/{len(lines)}] {line[:60].strip()}...")
            translated_lines.append(translated)
        else:
            translated_lines.append(line)
        
        if (i + 1) % 500 == 0:
            progress = ((i + 1) / len(lines)) * 100
            print(f"📈 진행: {i + 1}/{len(lines)}줄 ({progress:.1f}%), {changed_count}개 변경...")
    
    return '\n'.join(translated_lines), changed_count

def main():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 파일 크기: {len(content):,}자")
    
    # 중국어 문자 개수 확인
    chinese_count = len(re.findall(r'[\u4e00-\u9fff]', content))
    print(f"🔍 중국어 문자: {chinese_count:,}개 발견")
    
    print("\n🚀 번역 시작...")
    translated_content, changed_count = translate_chinese_in_content(content)
    
    print(f"\n💾 저장 중... (총 {changed_count}개 줄 변경)")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(translated_content)
    
    # 남은 중국어 확인
    remaining = len(re.findall(r'[\u4e00-\u9fff]', translated_content))
    print(f"✅ 완료! (남은 중국어: {remaining}개)")

if __name__ == '__main__':
    main()
