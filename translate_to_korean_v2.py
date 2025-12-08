#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON 파일 내의 모든 중국어 텍스트를 한국어로 번역하는 개선된 스크립트
"""

import json
import re
import sys
import time
from deep_translator import GoogleTranslator

def contains_chinese(text):
    """텍스트에 중국어 문자가 포함되어 있는지 확인"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]+', text))

def translate_to_korean(text, max_retries=3):
    """중국어가 포함된 텍스트를 한국어로 번역 (재시도 로직 포함)"""
    if not contains_chinese(text):
        return text
    
    # 매우 긴 텍스트는 분할하여 처리
    if len(text) > 5000:
        # JSON 문자열인 경우 특별 처리
        if text.strip().startswith('{') and text.strip().endswith('}'):
            return translate_json_string(text, max_retries)
        else:
            # 일반 텍스트는 문장 단위로 분할
            return translate_long_text(text, max_retries)
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            print(f"✓ 번역 완료 ({len(text)}자): {text[:30]}...")
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"⚠ 번역 재시도 {attempt + 1}/{max_retries} ({wait_time}초 후)...")
                time.sleep(wait_time)
            else:
                print(f"✗ 번역 실패: {str(e)[:50]}")
                return text

def translate_json_string(json_str, max_retries=3):
    """JSON 문자열 내부의 중국어를 번역"""
    try:
        # JSON 파싱 시도
        data = json.loads(json_str)
        translated_data = translate_recursive(data)
        return json.dumps(translated_data, ensure_ascii=False, indent=2)
    except:
        # JSON이 아닌 경우 직접 번역
        return translate_to_korean(json_str, max_retries)

def translate_long_text(text, max_retries=3):
    """긴 텍스트를 문장 단위로 나누어 번역"""
    # 문장 구분자로 분할 (줄바꿈, 마침표 등)
    sentences = re.split(r'([。！？\n])', text)
    translated_parts = []
    
    current_chunk = ""
    for part in sentences:
        if len(current_chunk + part) < 4000:
            current_chunk += part
        else:
            if current_chunk:
                translated_parts.append(translate_to_korean(current_chunk, max_retries))
            current_chunk = part
    
    if current_chunk:
        translated_parts.append(translate_to_korean(current_chunk, max_retries))
    
    return ''.join(translated_parts)

def translate_recursive(obj):
    """재귀적으로 객체를 탐색하며 중국어를 한국어로 번역"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # 키도 중국어가 있으면 번역
            if isinstance(key, str) and contains_chinese(key):
                new_key = translate_to_korean(key)
                result[new_key] = translate_recursive(value)
            else:
                result[key] = translate_recursive(value)
        return result
    elif isinstance(obj, list):
        return [translate_recursive(item) for item in obj]
    elif isinstance(obj, str):
        if contains_chinese(obj):
            # JSON 문자열인지 확인
            if (obj.strip().startswith('{') or obj.strip().startswith('[')) and len(obj) > 100:
                try:
                    # JSON으로 파싱 가능하면 재귀 처리
                    parsed = json.loads(obj)
                    translated = translate_recursive(parsed)
                    return json.dumps(translated, ensure_ascii=False)
                except:
                    pass
            return translate_to_korean(obj)
        else:
            return obj
    else:
        return obj

def main():
    input_file = 'data/prompts.json'
    output_file = 'data/prompts.json'
    
    print(f"📖 파일 읽는 중: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        sys.exit(1)
    
    total_items = data.get('total', 0)
    print(f"📊 총 {total_items}개의 항목을 처리합니다...")
    
    # 중국어 항목 개수 확인
    chinese_count = 0
    def count_chinese(obj):
        nonlocal chinese_count
        if isinstance(obj, str) and contains_chinese(obj):
            chinese_count += 1
        elif isinstance(obj, dict):
            for v in obj.values():
                count_chinese(v)
        elif isinstance(obj, list):
            for item in obj:
                count_chinese(item)
    
    count_chinese(data)
    print(f"🔍 중국어 텍스트 {chinese_count}개 발견")
    
    # 번역 시작
    print("🚀 번역 시작...")
    start_time = time.time()
    
    translated_data = translate_recursive(data)
    
    elapsed_time = time.time() - start_time
    print(f"⏱ 번역 완료! 소요 시간: {elapsed_time:.1f}초")
    
    # 결과 저장
    print(f"💾 결과 저장 중: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        print("✅ 완료!")
    except Exception as e:
        print(f"❌ 파일 저장 오류: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

