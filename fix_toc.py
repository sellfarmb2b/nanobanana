#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
목차 부분 수정: 첫 항목 번역 및 빈 줄 제거
"""

import re
from deep_translator import GoogleTranslator

def translate_first_item():
    input_file = 'README.md'
    
    print(f"📖 파일 읽는 중: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 첫 번째 항목 번역
    first_item_match = re.search(r'(\*   \[사례 705：)(赛博朋克美学风格卡片 )(\]\(#prompt-705\)\n)', content)
    if first_item_match:
        translator = GoogleTranslator(source='zh-CN', target='ko')
        translated_text = translator.translate("赛博朋克美学风格卡片")
        new_first_item = f"{first_item_match.group(1)}{translated_text}{first_item_match.group(3)}"
        content = content.replace(first_item_match.group(0), new_first_item)
        print(f"✓ 첫 항목 번역: {translated_text}")
    
    # 불필요한 빈 줄 제거 (목차 섹션에서만)
    # 목차 시작과 끝 찾기
    toc_start_idx = content.find('## 📖 사례 목차')
    if toc_start_idx != -1:
        # 목차 다음 섹션 시작 찾기
        toc_end_idx = content.find('\n---\n', toc_start_idx)
        if toc_end_idx == -1:
            toc_end_idx = content.find('\n## [点击', toc_start_idx)
        
        if toc_end_idx != -1:
            toc_section = content[toc_start_idx:toc_end_idx]
            
            # 연속된 빈 줄을 하나로
            toc_section_fixed = re.sub(r'\n\n+(\*   )', r'\n\1', toc_section)
            toc_section_fixed = re.sub(r'\n\n+\n', r'\n\n', toc_section_fixed)
            
            content = content[:toc_start_idx] + toc_section_fixed + content[toc_end_idx:]
            print("✓ 빈 줄 제거 완료")
    
    print(f"💾 저장 중: {input_file}")
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 완료!")

if __name__ == '__main__':
    translate_first_item()
