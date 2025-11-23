#!/usr/bin/env python3
"""
CLEVR 데이터셋의 questions JSON을 LLaVA 평가용 JSONL 형식으로 변환하는 스크립트
"""

import json
import argparse
from pathlib import Path


def convert_clevr_to_llava(clevr_json_path, output_jsonl_path, add_prompt=True):
    """
    CLEVR questions JSON을 LLaVA JSONL 형식으로 변환
    
    Args:
        clevr_json_path: CLEVR questions JSON 파일 경로
        output_jsonl_path: 출력 JSONL 파일 경로
        add_prompt: Short-answer 프롬프트 추가 여부
    """
    print(f"Loading CLEVR questions from: {clevr_json_path}")
    
    with open(clevr_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"Found {len(questions)} questions")
    
    # 출력 디렉토리 생성
    output_path = Path(output_jsonl_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_jsonl_path, 'w', encoding='utf-8') as f:
        for q_idx, q in enumerate(questions):
            # Question ID: question_index가 있으면 사용, 없으면 image_index 사용
            question_id = q.get('question_index', q.get('image_index', q_idx))
            
            # 질문 텍스트
            question_text = q['question']
            
            # Short-answer 형식: 프롬프트 추가 (LLaVA Evaluation.md 참고)
            if add_prompt:
                question_text = f"{question_text}\nAnswer the question using a single word or phrase."
            
            # LLaVA JSONL 형식
            jsonl_entry = {
                "question_id": question_id,
                "image": q['image_filename'],
                "text": question_text
            }
            
            f.write(json.dumps(jsonl_entry, ensure_ascii=False) + '\n')
    
    print(f"Converted {len(questions)} questions to: {output_jsonl_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert CLEVR questions JSON to LLaVA JSONL format'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input CLEVR questions JSON file path'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output JSONL file path'
    )
    parser.add_argument(
        '--no-prompt',
        action='store_true',
        help='Do not add short-answer prompt (default: add prompt)'
    )
    
    args = parser.parse_args()
    
    convert_clevr_to_llava(
        args.input,
        args.output,
        add_prompt=not args.no_prompt
    )


if __name__ == '__main__':
    main()

