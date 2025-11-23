#!/usr/bin/env python3
"""
CLEVR 평가 결과 JSON 파일을 Excel로 변환하는 스크립트

평가 결과를 여러 시트로 나누어 Excel 파일로 저장합니다:
- Summary: 전체 요약 통계
- By Family: 질문 패밀리별 정확도
- By Program Length: 프로그램 길이별 정확도
- Correct Results: 정답인 질문들 (선택적)
- Incorrect Results: 오답인 질문들 (선택적)
- Missing Results: 누락된 질문들 (선택적)
"""

import json
import argparse
import pandas as pd
from pathlib import Path


def convert_eval_results_to_excel(json_file, output_excel, include_details=False, max_details=10000):
    """
    평가 결과 JSON 파일을 Excel로 변환합니다.
    
    Args:
        json_file: 입력 JSON 파일 경로
        output_excel: 출력 Excel 파일 경로
        include_details: 상세 결과 시트 포함 여부
        max_details: 상세 결과 최대 행 수 (파일 크기 제한)
    """
    print(f"Loading evaluation results from: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Converting to Excel...")
    
    # Excel Writer 생성
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        
        # 1. Summary 시트
        summary = data.get('summary', {})
        summary_df = pd.DataFrame([{
            'Metric': 'Total Questions',
            'Value': summary.get('total', 0)
        }, {
            'Metric': 'Correct',
            'Value': summary.get('correct', 0)
        }, {
            'Metric': 'Incorrect',
            'Value': summary.get('incorrect', 0)
        }, {
            'Metric': 'Missing',
            'Value': summary.get('missing', 0)
        }, {
            'Metric': 'Accuracy (%)',
            'Value': round(summary.get('accuracy', 0), 2)
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        print(f"  - Summary sheet: {len(summary_df)} rows")
        
        # 2. By Family 시트
        by_family = data.get('by_family', {})
        family_list = []
        for family_idx, stats in sorted(by_family.items(), key=lambda x: int(x[0])):
            family_list.append({
                'Family Index': int(family_idx),
                'Total': stats.get('total', 0),
                'Correct': stats.get('correct', 0),
                'Incorrect': stats.get('total', 0) - stats.get('correct', 0),
                'Accuracy (%)': round(stats.get('accuracy', 0), 2)
            })
        family_df = pd.DataFrame(family_list)
        family_df.to_excel(writer, sheet_name='By Family', index=False)
        print(f"  - By Family sheet: {len(family_df)} rows")
        
        # 3. By Program Length 시트
        by_program_length = data.get('by_program_length', {})
        program_length_list = []
        for prog_len, stats in sorted(by_program_length.items(), key=lambda x: int(x[0])):
            program_length_list.append({
                'Program Length': int(prog_len),
                'Total': stats.get('total', 0),
                'Correct': stats.get('correct', 0),
                'Incorrect': stats.get('total', 0) - stats.get('correct', 0),
                'Accuracy (%)': round(stats.get('accuracy', 0), 2)
            })
        program_length_df = pd.DataFrame(program_length_list)
        program_length_df.to_excel(writer, sheet_name='By Program Length', index=False)
        print(f"  - By Program Length sheet: {len(program_length_df)} rows")
        
        # 4. 상세 결과 시트 (선택적)
        if include_details:
            results = data.get('results', {})
            
            # Correct Results
            correct_results = results.get('correct', [])
            if correct_results:
                correct_df = pd.DataFrame(correct_results[:max_details])
                correct_df.to_excel(writer, sheet_name='Correct Results', index=False)
                print(f"  - Correct Results sheet: {len(correct_df)} rows (showing first {min(len(correct_results), max_details)})")
            
            # Incorrect Results
            incorrect_results = results.get('incorrect', [])
            if incorrect_results:
                incorrect_df = pd.DataFrame(incorrect_results[:max_details])
                incorrect_df.to_excel(writer, sheet_name='Incorrect Results', index=False)
                print(f"  - Incorrect Results sheet: {len(incorrect_df)} rows (showing first {min(len(incorrect_results), max_details)})")
            
            # Missing Results
            missing_results = results.get('missing', [])
            if missing_results:
                missing_df = pd.DataFrame(missing_results[:max_details])
                missing_df.to_excel(writer, sheet_name='Missing Results', index=False)
                print(f"  - Missing Results sheet: {len(missing_df)} rows (showing first {min(len(missing_results), max_details)})")
    
    print(f"\nExcel file saved to: {output_excel}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert CLEVR evaluation results JSON to Excel format'
    )
    parser.add_argument(
        '--input-json',
        type=str,
        required=True,
        help='Path to evaluation results JSON file'
    )
    parser.add_argument(
        '--output-excel',
        type=str,
        help='Path to output Excel file (default: same as input with .xlsx extension)'
    )
    parser.add_argument(
        '--include-details',
        action='store_true',
        help='Include detailed results sheets (correct/incorrect/missing)'
    )
    parser.add_argument(
        '--max-details',
        type=int,
        default=10000,
        help='Maximum number of rows in detail sheets (default: 10000)'
    )
    
    args = parser.parse_args()
    
    # 출력 파일 경로 설정
    if args.output_excel:
        output_path = Path(args.output_excel)
    else:
        input_path = Path(args.input_json)
        output_path = input_path.with_suffix('.xlsx')
    
    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 변환 실행
    convert_eval_results_to_excel(
        args.input_json,
        str(output_path),
        include_details=args.include_details,
        max_details=args.max_details
    )


if __name__ == '__main__':
    main()

