#!/usr/bin/env python3
"""
CLEVR 데이터셋의 scenes와 questions JSON 파일을 엑셀 파일로 변환하는 스크립트
"""

import json
import os
import pandas as pd
from pathlib import Path
import argparse
import glob
import re


def load_json_file(file_path):
    """JSON 파일을 로드합니다."""
    print(f"Loading {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def convert_scenes_to_excel(scenes_data, output_path):
    """Scenes 데이터를 엑셀로 변환합니다."""
    print("Converting scenes to Excel...")
    
    scenes_list = []
    objects_list = []
    
    for scene_idx, scene in enumerate(scenes_data['scenes']):
        # Scene 기본 정보
        scene_row = {
            'scene_index': scene_idx,
            'image_index': scene.get('image_index', ''),
            'image_filename': scene.get('image_filename', ''),
            'split': scene.get('split', ''),
            'num_objects': len(scene.get('objects', []))
        }
        
        # Directions 정보를 문자열로 변환
        directions = scene.get('directions', {})
        for direction, coords in directions.items():
            scene_row[f'direction_{direction}'] = str(coords) if coords else ''
        
        # Relations 정보를 요약
        relations = scene.get('relations', {})
        for relation_type, adj_list in relations.items():
            scene_row[f'relations_{relation_type}_count'] = sum(len(x) for x in adj_list) if adj_list else 0
        
        scenes_list.append(scene_row)
        
        # Objects를 별도 리스트로 저장
        for obj_idx, obj in enumerate(scene.get('objects', [])):
            obj_row = {
                'scene_index': scene_idx,
                'image_index': scene.get('image_index', ''),
                'image_filename': scene.get('image_filename', ''),
                'object_index': obj_idx,
                'color': obj.get('color', ''),
                'size': obj.get('size', ''),
                'material': obj.get('material', ''),
                'shape': obj.get('shape', ''),
                'rotation': obj.get('rotation', ''),
                '3d_coords': str(obj.get('3d_coords', [])),
                'pixel_coords': str(obj.get('pixel_coords', []))
            }
            objects_list.append(obj_row)
    
    # DataFrame 생성
    scenes_df = pd.DataFrame(scenes_list)
    objects_df = pd.DataFrame(objects_list)
    
    # 엑셀 파일로 저장 (여러 시트)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        scenes_df.to_excel(writer, sheet_name='Scenes', index=False)
        objects_df.to_excel(writer, sheet_name='Objects', index=False)
    
    print(f"Scenes Excel saved to: {output_path}")
    print(f"  - Scenes sheet: {len(scenes_df)} rows")
    print(f"  - Objects sheet: {len(objects_df)} rows")
    
    return scenes_df, objects_df


def convert_questions_to_excel(questions_data, output_path):
    """Questions 데이터를 엑셀로 변환합니다."""
    print("Converting questions to Excel...")
    
    questions_list = []
    
    for q_idx, question in enumerate(questions_data['questions']):
        # Program을 문자열로 변환
        program_str = ''
        if 'program' in question and question['program']:
            program_parts = []
            for func in question['program']:
                func_name = func.get('function', '')
                inputs = func.get('inputs', [])
                value_inputs = func.get('value_inputs', [])
                func_str = f"{func_name}({', '.join(map(str, inputs))}"
                if value_inputs:
                    func_str += f", values: {', '.join(value_inputs)}"
                func_str += ")"
                program_parts.append(func_str)
            program_str = " -> ".join(program_parts)
        
        question_row = {
            'question_index': q_idx,
            'image_index': question.get('image_index', ''),
            'image_filename': question.get('image_filename', ''),
            'split': question.get('split', ''),
            'question': question.get('question', ''),
            'answer': question.get('answer', ''),
            'question_family_index': question.get('question_family_index', ''),
            'program': program_str,
            'program_length': len(question.get('program', []))
        }
        
        questions_list.append(question_row)
    
    # DataFrame 생성
    questions_df = pd.DataFrame(questions_list)
    
    # 엑셀 파일로 저장
    questions_df.to_excel(output_path, index=False, engine='openpyxl')
    
    print(f"Questions Excel saved to: {output_path}")
    print(f"  - Questions: {len(questions_df)} rows")
    
    return questions_df


def find_matching_files(directory, pattern_prefix, split):
    """
    디렉토리에서 split과 매칭되는 파일을 찾습니다.
    예: split='val' -> 'CLEVR_val_scenes.json', 'CLEVR_valA_scenes.json', 'CLEVR_valB_scenes.json' 등
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    
    # 패턴: CLEVR_{split}로 시작하는 파일 (뒤에 A, B 등이 올 수 있음)
    pattern = f'CLEVR_{split}*.json'
    matching_files = list(directory.glob(pattern))
    
    # 정확히 split으로 끝나는 파일 우선, 그 다음 A, B 등
    def sort_key(path):
        name = path.name
        # CLEVR_{split}_scenes.json 형태가 가장 우선
        if name == f'CLEVR_{split}_scenes.json' or name == f'CLEVR_{split}_questions.json':
            return (0, name)
        # CLEVR_{split}A_scenes.json 형태는 다음
        match = re.search(rf'CLEVR_{split}([A-Z]?)_(scenes|questions)\.json', name)
        if match:
            suffix = match.group(1) if match.group(1) else ''
            return (1, suffix, name)
        return (2, name)
    
    matching_files.sort(key=sort_key)
    return matching_files


def main():
    parser = argparse.ArgumentParser(description='Convert CLEVR JSON files to Excel')
    parser.add_argument('--dataset_dir', type=str, 
                       default='Dataset/CLEVR_v1.0',
                       help='Path to CLEVR dataset directory')
    parser.add_argument('--output_dir', type=str,
                       default='Dataset/CLEVR_v1.0/excel',
                       help='Output directory for Excel files')
    parser.add_argument('--split', type=str, 
                       default='train',
                       help='Dataset split to convert (default: train). Can be train, val, test, or specific like valA, valB')
    parser.add_argument('--scenes-only', action='store_true',
                       help='Convert only scenes files')
    parser.add_argument('--questions-only', action='store_true',
                       help='Convert only questions files')
    parser.add_argument('--all-splits', action='store_true',
                       help='Convert all available splits automatically')
    
    args = parser.parse_args()
    
    # 경로 설정
    dataset_dir = Path(args.dataset_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scenes_dir = dataset_dir / 'scenes'
    questions_dir = dataset_dir / 'questions'
    
    # 모든 split 자동 처리
    if args.all_splits:
        # scenes 디렉토리에서 모든 split 찾기
        all_scene_files = list(scenes_dir.glob('CLEVR_*_scenes.json')) if scenes_dir.exists() else []
        all_question_files = list(questions_dir.glob('CLEVR_*_questions.json')) if questions_dir.exists() else []
        
        # split 추출 (예: CLEVR_valA_scenes.json -> valA)
        splits = set()
        for file in all_scene_files + all_question_files:
            match = re.search(r'CLEVR_(.+?)_(scenes|questions)\.json', file.name)
            if match:
                splits.add(match.group(1))
        
        print(f"Found splits: {sorted(splits)}")
        for split in sorted(splits):
            print(f"\n{'='*60}")
            print(f"Processing split: {split}")
            print(f"{'='*60}")
            args.split = split
            
            # Scenes 파일 변환
            if not args.questions_only:
                scene_files = find_matching_files(scenes_dir, 'CLEVR', split)
                for scene_file in scene_files:
                    print(f"\nProcessing scenes file: {scene_file.name}")
                    scenes_data = load_json_file(scene_file)
                    # 출력 파일명에 원본 파일의 suffix 포함
                    suffix = scene_file.stem.replace(f'CLEVR_{split}_scenes', '')
                    output_name = f'CLEVR_{split}{suffix}_scenes.xlsx' if suffix else f'CLEVR_{split}_scenes.xlsx'
                    scenes_output = output_dir / output_name
                    convert_scenes_to_excel(scenes_data, scenes_output)
            
            # Questions 파일 변환
            if not args.scenes_only:
                question_files = find_matching_files(questions_dir, 'CLEVR', split)
                for question_file in question_files:
                    print(f"\nProcessing questions file: {question_file.name}")
                    questions_data = load_json_file(question_file)
                    # 출력 파일명에 원본 파일의 suffix 포함
                    suffix = question_file.stem.replace(f'CLEVR_{split}_questions', '')
                    output_name = f'CLEVR_{split}{suffix}_questions.xlsx' if suffix else f'CLEVR_{split}_questions.xlsx'
                    questions_output = output_dir / output_name
                    convert_questions_to_excel(questions_data, questions_output)
        
        return
    
    # 단일 split 처리
    # Scenes 파일 변환
    if not args.questions_only:
        scene_files = find_matching_files(scenes_dir, 'CLEVR', args.split)
        if scene_files:
            for scene_file in scene_files:
                print(f"\nProcessing scenes file: {scene_file.name}")
                scenes_data = load_json_file(scene_file)
                # 출력 파일명에 원본 파일의 suffix 포함
                suffix = scene_file.stem.replace(f'CLEVR_{args.split}_scenes', '')
                output_name = f'CLEVR_{args.split}{suffix}_scenes.xlsx' if suffix else f'CLEVR_{args.split}_scenes.xlsx'
                scenes_output = output_dir / output_name
                convert_scenes_to_excel(scenes_data, scenes_output)
        else:
            print(f"No scenes files found for split '{args.split}' in {scenes_dir}")
    
    # Questions 파일 변환
    if not args.scenes_only:
        question_files = find_matching_files(questions_dir, 'CLEVR', args.split)
        if question_files:
            for question_file in question_files:
                print(f"\nProcessing questions file: {question_file.name}")
                questions_data = load_json_file(question_file)
                # 출력 파일명에 원본 파일의 suffix 포함
                suffix = question_file.stem.replace(f'CLEVR_{args.split}_questions', '')
                output_name = f'CLEVR_{args.split}{suffix}_questions.xlsx' if suffix else f'CLEVR_{args.split}_questions.xlsx'
                questions_output = output_dir / output_name
                convert_questions_to_excel(questions_data, questions_output)
        else:
            print(f"No questions files found for split '{args.split}' in {questions_dir}")


if __name__ == '__main__':
    main()

