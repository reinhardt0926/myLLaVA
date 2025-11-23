#!/usr/bin/env python3
"""
CLEVR 데이터셋 평가 스크립트

모델 예측 결과와 정답을 비교하여 정확도를 계산합니다.
질문 패밀리별, 프로그램 길이별 분석도 제공합니다.
"""

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path


def normalize_answer(answer):
    """
    답변을 정규화합니다 (대소문자, 공백 제거)
    
    Args:
        answer: 원본 답변 문자열
        
    Returns:
        정규화된 답변 문자열
    """
    if answer is None:
        return ""
    # 문자열로 변환하고 소문자로 변환, 앞뒤 공백 제거
    return str(answer).lower().strip()


def load_annotations(annotation_file):
    """
    CLEVR questions JSON 파일을 로드하고 question_id를 키로 하는 딕셔너리로 변환
    
    Args:
        annotation_file: CLEVR questions JSON 파일 경로
        
    Returns:
        {question_id: question_data} 딕셔너리
    """
    print(f"Loading annotations from: {annotation_file}")
    with open(annotation_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"Found {len(questions)} questions in annotation file")
    
    # question_index를 키로 하는 딕셔너리 생성
    annotations = {}
    for q in questions:
        question_id = q.get('question_index')
        if question_id is not None:
            annotations[question_id] = q
    
    print(f"Loaded {len(annotations)} annotations")
    return annotations


def load_predictions(result_file):
    """
    모델 예측 결과 JSONL 파일을 로드
    
    Args:
        result_file: 모델 예측 결과 JSONL 파일 경로
        
    Returns:
        {question_id: prediction_data} 딕셔너리
    """
    print(f"Loading predictions from: {result_file}")
    predictions = {}
    
    if not os.path.exists(result_file):
        print(f"Warning: Result file not found: {result_file}")
        return predictions
    
    with open(result_file, 'rb') as f:
        # null 바이트나 공백 문자 건너뛰기
        content = f.read()
        # null 바이트 제거
        content = content.replace(b'\x00', b'')
        # 텍스트로 디코딩
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # UTF-8 디코딩 실패 시 latin-1로 시도
            text = content.decode('latin-1', errors='ignore')
        
        # 줄 단위로 처리
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                pred = json.loads(line)
                question_id = pred.get('question_id')
                if question_id is not None:
                    predictions[question_id] = pred
            except json.JSONDecodeError as e:
                # JSON 파싱 에러는 무시하고 계속 진행
                print(f"Warning: Failed to parse line (skipping): {line[:100]}... Error: {e}")
                continue
    
    print(f"Loaded {len(predictions)} predictions")
    return predictions


def eval_single(annotation_file, result_file, output_file=None):
    """
    단일 결과 파일에 대해 평가 수행
    
    Args:
        annotation_file: CLEVR questions JSON 파일 경로
        result_file: 모델 예측 결과 JSONL 파일 경로
        output_file: 상세 결과를 저장할 JSON 파일 경로 (선택사항)
    """
    annotations = load_annotations(annotation_file)
    predictions = load_predictions(result_file)
    
    # 평가 결과 저장
    results = {
        'correct': [],
        'incorrect': [],
        'missing': []
    }
    
    # 통계 정보
    stats = {
        'total': 0,
        'correct': 0,
        'incorrect': 0,
        'missing': 0,
        'by_family': defaultdict(lambda: {'total': 0, 'correct': 0}),
        'by_program_length': defaultdict(lambda: {'total': 0, 'correct': 0})
    }
    
    # 각 질문에 대해 평가
    for question_id, annotation in annotations.items():
        stats['total'] += 1
        
        # 정답
        gt_answer = normalize_answer(annotation.get('answer', ''))
        
        # 예측
        if question_id not in predictions:
            stats['missing'] += 1
            results['missing'].append({
                'question_id': question_id,
                'question': annotation.get('question', ''),
                'ground_truth': annotation.get('answer', ''),
                'prediction': None
            })
            continue
        
        pred_data = predictions[question_id]
        pred_answer = normalize_answer(pred_data.get('text', ''))
        
        # 질문 패밀리 및 프로그램 길이 정보
        family_idx = annotation.get('question_family_index', -1)
        program = annotation.get('program', [])
        program_length = len(program)
        
        # 통계 업데이트
        stats['by_family'][family_idx]['total'] += 1
        stats['by_program_length'][program_length]['total'] += 1
        
        # 정확도 계산
        is_correct = (gt_answer == pred_answer)
        
        if is_correct:
            stats['correct'] += 1
            stats['by_family'][family_idx]['correct'] += 1
            stats['by_program_length'][program_length]['correct'] += 1
            results['correct'].append({
                'question_id': question_id,
                'question': annotation.get('question', ''),
                'ground_truth': annotation.get('answer', ''),
                'prediction': pred_data.get('text', '')
            })
        else:
            stats['incorrect'] += 1
            results['incorrect'].append({
                'question_id': question_id,
                'question': annotation.get('question', ''),
                'ground_truth': annotation.get('answer', ''),
                'prediction': pred_data.get('text', '')
            })
    
    # 결과 출력
    print("\n" + "="*60)
    print("CLEVR Evaluation Results")
    print("="*60)
    print(f"Total Questions: {stats['total']}")
    print(f"Correct: {stats['correct']}")
    print(f"Incorrect: {stats['incorrect']}")
    print(f"Missing: {stats['missing']}")
    
    if stats['total'] > 0:
        accuracy = stats['correct'] / stats['total'] * 100
        print(f"Accuracy: {accuracy:.2f}%")
    else:
        accuracy = 0.0
        print("Accuracy: N/A (no questions found)")
    
    # 질문 패밀리별 정확도
    if stats['by_family']:
        print("\nBy Question Family:")
        for family_idx in sorted(stats['by_family'].keys()):
            family_stats = stats['by_family'][family_idx]
            if family_stats['total'] > 0:
                family_acc = family_stats['correct'] / family_stats['total'] * 100
                print(f"  Family {family_idx}: {family_acc:.2f}% ({family_stats['correct']}/{family_stats['total']})")
    
    # 프로그램 길이별 정확도
    if stats['by_program_length']:
        print("\nBy Program Length:")
        for prog_len in sorted(stats['by_program_length'].keys()):
            prog_stats = stats['by_program_length'][prog_len]
            if prog_stats['total'] > 0:
                prog_acc = prog_stats['correct'] / prog_stats['total'] * 100
                print(f"  Length {prog_len}: {prog_acc:.2f}% ({prog_stats['correct']}/{prog_stats['total']})")
    
    print("="*60)
    
    # 상세 결과 저장 (선택사항)
    if output_file:
        output_data = {
            'summary': {
                'total': stats['total'],
                'correct': stats['correct'],
                'incorrect': stats['incorrect'],
                'missing': stats['missing'],
                'accuracy': accuracy
            },
            'by_family': {
                str(k): {
                    'total': v['total'],
                    'correct': v['correct'],
                    'accuracy': v['correct'] / v['total'] * 100 if v['total'] > 0 else 0
                }
                for k, v in stats['by_family'].items()
            },
            'by_program_length': {
                str(k): {
                    'total': v['total'],
                    'correct': v['correct'],
                    'accuracy': v['correct'] / v['total'] * 100 if v['total'] > 0 else 0
                }
                for k, v in stats['by_program_length'].items()
            },
            'results': results
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to: {output_file}")
    
    return accuracy, stats


def get_args():
    parser = argparse.ArgumentParser(description='Evaluate CLEVR model predictions')
    parser.add_argument('--annotation-file', type=str, required=True,
                       help='Path to CLEVR questions JSON file (e.g., CLEVR_valA_questions.json)')
    parser.add_argument('--result-file', type=str, required=True,
                       help='Path to model prediction JSONL file (e.g., merge.jsonl)')
    parser.add_argument('--output-file', type=str, default=None,
                       help='Path to save detailed evaluation results JSON (optional)')
    parser.add_argument('--result-dir', type=str, default=None,
                       help='Evaluate all JSONL files in a directory')
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    
    if args.result_file is not None:
        eval_single(args.annotation_file, args.result_file, args.output_file)
    
    if args.result_dir is not None:
        result_dir = Path(args.result_dir)
        for result_file in sorted(result_dir.glob('*.jsonl')):
            print(f"\n{'='*60}")
            print(f"Evaluating: {result_file.name}")
            print(f"{'='*60}")
            eval_single(args.annotation_file, str(result_file))

