#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON 파일 내의 중국어 텍스트를 한국어로 번역하는 스크립트
"""

import json
import re
import sys
from deep_translator import GoogleTranslator

def contains_chinese(text):
    """텍스트에 중국어 문자가 포함되어 있는지 확인"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]+', text))

def translate_to_korean(text):
    """중국어가 포함된 텍스트를 한국어로 번역"""
    if not contains_chinese(text):
        return text
    
    try:
        # 중국어를 한국어로 번역
        translator = GoogleTranslator(source='zh-CN', target='ko')
        translated = translator.translate(text)
        print(f"번역 완료: {text[:50]}... -> {translated[:50]}...")
        return translated
    except Exception as e:
        print(f"번역 오류: {e}")
        print(f"원본 텍스트: {text[:100]}")
        return text

def translate_recursive(obj):
    """재귀적으로 객체를 탐색하며 중국어를 한국어로 번역"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if isinstance(value, str) and contains_chinese(value):
                result[key] = translate_to_korean(value)
            else:
                result[key] = translate_recursive(value)
        return result
    elif isinstance(obj, list):
        return [translate_recursive(item) for item in obj]
    elif isinstance(obj, str) and contains_chinese(obj):
        return translate_to_korean(obj)
    else:
        return obj

def main():
    input_file = 'data/prompts.json'
    output_file = 'data/prompts.json'
    
    print(f"파일 읽는 중: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        sys.exit(1)
    
    print(f"총 {data.get('total', 0)}개의 항목을 처리합니다...")
    
    # 번역 시작
    print("번역 시작...")
    translated_data = translate_recursive(data)
    
    # 결과 저장
    print(f"결과 저장 중: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        print("완료!")
    except Exception as e:
        print(f"파일 저장 오류: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

