#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
남은 중국어만 찾아서 번역하는 스크립트
"""

import json
import re
import time
from deep_translator import GoogleTranslator

def contains_chinese(text):
    """텍스트에 중국어 문자가 포함되어 있는지 확인"""
    if not isinstance(text, str):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]+', text))

def translate_json_content(json_str, max_retries=3):
    """JSON 문자열을 파싱하여 내부 중국어만 번역"""
    try:
        # JSON 파싱
        data = json.loads(json_str)
        
        # 재귀적으로 번역
        def translate_obj(obj):
            if isinstance(obj, dict):
                return {k: translate_obj(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [translate_obj(item) for item in obj]
            elif isinstance(obj, str) and contains_chinese(obj):
                for attempt in range(max_retries):
                    try:
                        translator = GoogleTranslator(source='zh-CN', target='ko')
                        translated = translator.translate(obj)
                        print(f"  ✓ 번역: {obj[:30]}...")
                        return translated
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(2)
                        else:
                            print(f"  ✗ 번역 실패: {str(e)[:50]}")
                            return obj
            return obj
        
        translated = translate_obj(data)
        return json.dumps(translated, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  JSON 파싱 실패: {e}")
        # JSON이 아니면 직접 번역
        return translate_text(json_str, max_retries)

def translate_text(text, max_retries=3):
    """일반 텍스트 번역"""
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source='zh-CN', target='ko')
            translated = translator.translate(text)
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return text

def fix_file():
    input_file = 'data/prompts.json'
    
    print(f"📖 파일 읽는 중...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 중국어가 있는 모든 문자열 찾기 및 번역
    def fix_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                obj[key] = fix_recursive(value, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                obj[i] = fix_recursive(item, new_path)
        elif isinstance(obj, str) and contains_chinese(obj):
            print(f"\n🔍 발견 ({path}): {obj[:50]}...")
            if obj.strip().startswith('{') and obj.strip().endswith('}'):
                # JSON 문자열 처리
                print(f"  → JSON 문자열 번역 중...")
                return translate_json_content(obj)
            else:
                print(f"  → 일반 텍스트 번역 중...")
                return translate_text(obj)
        return obj
    
    print("🚀 번역 시작...")
    data = fix_recursive(data)
    
    print("\n💾 저장 중...")
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ 완료!")

if __name__ == '__main__':
    fix_file()

