#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README.md 파일의 중국어를 스마트하게 한국어로 번역하는 스크립트
주요 패턴을 먼저 처리하여 효율적으로 번역
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

def translate_readme_smart():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 파일 크기: {len(content)}자")
    
    # 패턴별로 번역
    translations = []
    
    # 패턴 1: 사례 제목 - ## 案例 XXX：제목 (来源 ...) 模型：...
    print("\n🔍 패턴 1: 사례 제목 번역 중...")
    case_pattern = r'(##\s+)案例\s+(\d+)：([^\n]+?)(\s*\(来源\s+[^\)]+\)\s+模型：[^\n]+)'
    
    def replace_case_title(match):
        prefix = match.group(1)
        case_num = match.group(2)
        title = match.group(3).strip()
        suffix = match.group(4)
        
        # 제목만 번역
        translated_title = translate_text(title, delay=0.3)
        
        # "来源" -> "출처", "模型" -> "모델" 번역
        suffix_translated = suffix.replace('来源', '출처').replace('模型', '모델')
        
        return f"{prefix}사례 {case_num}：{translated_title}{suffix_translated}"
    
    content = re.sub(case_pattern, replace_case_title, content)
    print("✓ 사례 제목 번역 완료")
    
    # 패턴 2: 단독 사례 제목 (간단한 형식)
    print("\n🔍 패턴 2: 단독 사례 제목 번역 중...")
    simple_case_pattern = r'(##\s+)案例\s+(\d+)：([^\n]+)$'
    
    def replace_simple_case(match):
        prefix = match.group(1)
        case_num = match.group(2)
        title = match.group(3).strip()
        
        translated_title = translate_text(title, delay=0.3)
        return f"{prefix}사례 {case_num}：{translated_title}"
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.match(simple_case_pattern, line):
            lines[i] = replace_simple_case(re.match(simple_case_pattern, line))
            print(f"  ✓ [{i+1}] {line[:60]}...")
    
    content = '\n'.join(lines)
    print("✓ 단독 사례 제목 번역 완료")
    
    # 패턴 3: "来源", "模型" 같은 키워드
    print("\n🔍 패턴 3: 키워드 번역 중...")
    content = content.replace('来源', '출처')
    content = content.replace('模型', '모델')
    print("✓ 키워드 번역 완료")
    
    # 패턴 4: 나머지 중국어 텍스트
    print("\n🔍 패턴 4: 나머지 중국어 텍스트 번역 중...")
    lines = content.split('\n')
    chinese_count = 0
    
    for i, line in enumerate(lines):
        if contains_chinese(line):
            # 이미 처리한 패턴들은 건너뛰기
            if line.strip().startswith('## 사례') or line.strip().startswith('*   ['):
                continue
            # 코드 블록, 이미지, 표는 건너뛰기
            if '```' in line or '<img' in line or line.strip().startswith('|') or line.strip().startswith('<div'):
                continue
            
            chinese_count += 1
            translated = translate_text(line, delay=0.3)
            if translated != line:
                lines[i] = translated
                if chinese_count <= 10 or chinese_count % 50 == 0:
                    print(f"  ✓ [{i+1}/{len(lines)}] {line[:50].strip()}...")
        
        if (i + 1) % 500 == 0:
            print(f"  📈 진행: {i + 1}/{len(lines)}줄...")
    
    content = '\n'.join(lines)
    print(f"✓ 나머지 중국어 번역 완료 (총 {chinese_count}개 처리)")
    
    # 파일 저장
    print(f"\n💾 저장 중: {input_file}")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_readme_smart()
