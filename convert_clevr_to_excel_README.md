# CLEVR 데이터셋 Excel 변환 도구

CLEVR 데이터셋의 scenes와 questions JSON 파일을 엑셀 파일로 변환하는 Python 스크립트입니다.

## 📋 목차

- [기능](#기능)
- [요구사항](#요구사항)
- [설치](#설치)
- [사용 방법](#사용-방법)
- [출력 형식](#출력-형식)
- [예제](#예제)
- [주의사항](#주의사항)

## ✨ 기능

### Scenes 변환
- **Scenes 시트**: 각 scene의 기본 정보 (이미지 인덱스, 파일명, 객체 개수 등)
- **Objects 시트**: 각 scene에 포함된 모든 객체의 상세 정보 (색상, 크기, 재질, 모양, 위치 등)

### Questions 변환
- 각 질문을 행으로 표시
- 질문, 답변, 프로그램 정보 포함
- 프로그램을 읽기 쉬운 문자열 형식으로 변환

## 📦 요구사항

- Python 3.8 이상
- pandas
- openpyxl

## 🔧 설치

```bash
# 필요한 패키지 설치
pip install pandas openpyxl
```

또는 conda 환경에서:

```bash
conda activate llava  # 또는 사용 중인 환경
pip install pandas openpyxl
```

## 🚀 사용 방법

### 기본 사용법

```bash
# train 데이터 변환 (기본값)
python convert_clevr_to_excel.py
```

### 명령줄 옵션

```bash
python convert_clevr_to_excel.py [옵션]
```

#### 주요 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--dataset_dir` | CLEVR 데이터셋 디렉토리 경로 | `Dataset/CLEVR_v1.0` |
| `--output_dir` | 엑셀 파일 출력 디렉토리 | `Dataset/CLEVR_v1.0/excel` |
| `--split` | 변환할 데이터셋 split (train/val/test 또는 valA/valB 등) | `train` |
| `--all-splits` | 모든 split을 자동으로 찾아서 변환 | - |
| `--scenes-only` | scenes 파일만 변환 | - |
| `--questions-only` | questions 파일만 변환 | - |

### 사용 예제

#### 1. 특정 split 변환

```bash
# validation 데이터 변환
python convert_clevr_to_excel.py --split val

# test 데이터 변환
python convert_clevr_to_excel.py --split test
```

#### 2. Scenes만 변환

```bash
python convert_clevr_to_excel.py --split train --scenes-only
```

#### 3. Questions만 변환

```bash
python convert_clevr_to_excel.py --split train --questions-only
```

#### 4. 커스텀 경로 지정

```bash
# 데이터셋 경로와 출력 경로 지정
python convert_clevr_to_excel.py \
    --dataset_dir /path/to/CLEVR_v1.0 \
    --output_dir /path/to/output/excel
```

#### 5. 모든 split 자동 변환 (권장)

```bash
# 모든 split을 자동으로 찾아서 변환 (CLEVR_CoGenT의 valA, valB 등도 자동 처리)
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0 --output_dir Dataset/CLEVR_CoGenT_v1.0/excel --all-splits
```

#### 6. CLEVR_CoGenT 데이터셋 변환

CLEVR_CoGenT는 `valA`, `valB`, `testA`, `testB` 등 여러 split을 포함합니다:

```bash
# 특정 split 변환 (예: valA)
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0 --split valA

# 모든 split 자동 변환 (권장)
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0 --output_dir Dataset/CLEVR_CoGenT_v1.0/excel --all-splits
```

#### 7. 범용 데이터셋 지원

이 스크립트는 다양한 CLEVR 데이터셋 형식을 자동으로 인식합니다:
- `CLEVR_v1.0`: `CLEVR_train_scenes.json`, `CLEVR_val_scenes.json`
- `CLEVR_CoGenT_v1.0`: `CLEVR_trainA_scenes.json`, `CLEVR_valA_scenes.json`, `CLEVR_valB_scenes.json` 등
- 기타 변형: 파일명 패턴을 자동으로 감지하여 처리

## 📊 출력 형식

### Scenes Excel 파일 구조

#### Scenes 시트
| 컬럼명 | 설명 |
|--------|------|
| scene_index | Scene 인덱스 |
| image_index | 이미지 인덱스 |
| image_filename | 이미지 파일명 |
| split | 데이터셋 split (train/val/test) |
| num_objects | 객체 개수 |
| direction_left | 왼쪽 방향 벡터 [x, y, z] |
| direction_right | 오른쪽 방향 벡터 [x, y, z] |
| direction_front | 앞쪽 방향 벡터 [x, y, z] |
| direction_behind | 뒤쪽 방향 벡터 [x, y, z] |
| direction_below | 아래쪽 방향 벡터 [x, y, z] |
| direction_above | 위쪽 방향 벡터 [x, y, z] |
| relations_left_count | 왼쪽 관계 개수 |
| relations_right_count | 오른쪽 관계 개수 |
| relations_front_count | 앞쪽 관계 개수 |
| relations_behind_count | 뒤쪽 관계 개수 |

#### Objects 시트
| 컬럼명 | 설명 |
|--------|------|
| scene_index | Scene 인덱스 |
| image_index | 이미지 인덱스 |
| image_filename | 이미지 파일명 |
| object_index | 객체 인덱스 |
| color | 색상 (gray, blue, brown, yellow, red, green, purple, cyan) |
| size | 크기 (small, large) |
| material | 재질 (rubber, metal) |
| shape | 모양 (cube, sphere, cylinder) |
| rotation | 회전 각도 (도) |
| 3d_coords | 3D 좌표 [x, y, z] |
| pixel_coords | 픽셀 좌표 [x, y, z] |

### Questions Excel 파일 구조

| 컬럼명 | 설명 |
|--------|------|
| question_index | 질문 인덱스 |
| image_index | 이미지 인덱스 |
| image_filename | 이미지 파일명 |
| split | 데이터셋 split |
| question | 질문 텍스트 |
| answer | 답변 (test 데이터에는 없음) |
| question_family_index | 질문 패밀리 인덱스 |
| program | 프로그램 문자열 (함수 시퀀스) |
| program_length | 프로그램 길이 |

## 📁 출력 파일 위치

### CLEVR_v1.0 데이터셋

기본적으로 다음 위치에 엑셀 파일이 생성됩니다:

```
Dataset/CLEVR_v1.0/excel/
├── CLEVR_train_scenes.xlsx
├── CLEVR_train_questions.xlsx
├── CLEVR_val_scenes.xlsx
├── CLEVR_val_questions.xlsx
├── CLEVR_test_questions.xlsx
```

### CLEVR_CoGenT_v1.0 데이터셋

CLEVR_CoGenT는 여러 split을 포함하므로 더 많은 파일이 생성됩니다:

```
Dataset/CLEVR_CoGenT_v1.0/excel/
├── CLEVR_trainA_scenes.xlsx
├── CLEVR_trainA_questions.xlsx
├── CLEVR_valA_scenes.xlsx
├── CLEVR_valA_questions.xlsx
├── CLEVR_valB_scenes.xlsx
├── CLEVR_valB_questions.xlsx
├── CLEVR_testA_questions.xlsx
└── CLEVR_testB_questions.xlsx
```

## 💡 예제

### 예제 1: CLEVR_CoGenT 모든 split 자동 변환

```bash
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0 --output_dir Dataset/CLEVR_CoGenT_v1.0/excel --all-splits
```

**출력:**
```
Found splits: ['testA', 'testB', 'trainA', 'valA', 'valB']

============================================================
Processing split: testA
============================================================

Processing questions file: CLEVR_testA_questions.json
Loading Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_testA_questions.json...
Converting questions to Excel...
Questions Excel saved to: Dataset/CLEVR_CoGenT_v1.0/excel/CLEVR_testA_questions.xlsx
  - Questions: 150000 rows

============================================================
Processing split: testB
============================================================
...
```

### 예제 2: 특정 split 변환 (CLEVR_CoGenT)

```bash
# valA split만 변환
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0 --split valA
```

**출력:**
```
Processing scenes file: CLEVR_valA_scenes.json
Loading Dataset/CLEVR_CoGenT_v1.0/scenes/CLEVR_valA_scenes.json...
Converting scenes to Excel...
Scenes Excel saved to: Dataset/CLEVR_CoGenT_v1.0/excel/CLEVR_valA_scenes.xlsx
  - Scenes sheet: 15000 rows
  - Objects sheet: 150000 rows

Processing questions file: CLEVR_valA_questions.json
Loading Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valA_questions.json...
Converting questions to Excel...
Questions Excel saved to: Dataset/CLEVR_CoGenT_v1.0/excel/CLEVR_valA_questions.xlsx
  - Questions: 150000 rows
```

### 예제 3: CLEVR_v1.0 Validation 데이터 변환

```bash
python convert_clevr_to_excel.py --split val
```

**출력:**
```
Processing scenes file: CLEVR_val_scenes.json
Loading Dataset/CLEVR_v1.0/scenes/CLEVR_val_scenes.json...
Converting scenes to Excel...
Scenes Excel saved to: Dataset/CLEVR_v1.0/excel/CLEVR_val_scenes.xlsx
  - Scenes sheet: 15000 rows
  - Objects sheet: 150000 rows

Processing questions file: CLEVR_val_questions.json
Loading Dataset/CLEVR_v1.0/questions/CLEVR_val_questions.json...
Converting questions to Excel...
Questions Excel saved to: Dataset/CLEVR_v1.0/excel/CLEVR_val_questions.xlsx
  - Questions: 150000 rows
```

### 예제 4: Scenes만 변환

```bash
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0 --all-splits --scenes-only
```

## ⚠️ 주의사항

1. **파일 크기**: 
   - Train 데이터는 약 70,000개의 scene과 수십만 개의 질문이 있어 변환에 시간이 오래 걸릴 수 있습니다.
   - 생성되는 엑셀 파일도 매우 클 수 있습니다.

2. **메모리 사용량**:
   - 큰 JSON 파일을 메모리에 로드하므로 충분한 RAM이 필요합니다.
   - Train 데이터의 경우 수 GB의 메모리가 필요할 수 있습니다.

3. **실행 시간**:
   - Train 데이터: 수 분 ~ 수십 분 소요 가능
   - Val/Test 데이터: 수 초 ~ 수 분 소요

4. **엑셀 파일 크기 제한**:
   - Excel 2007 이상 버전은 최대 1,048,576행을 지원합니다.
   - 매우 큰 데이터셋의 경우 CSV 형식으로 변환하는 것을 고려해보세요.

## 🔍 문제 해결

### ModuleNotFoundError: No module named 'openpyxl'

```bash
pip install openpyxl
```

### 메모리 부족 오류

- 더 작은 split (val 또는 test)부터 시도해보세요.
- `--scenes-only` 또는 `--questions-only` 옵션을 사용하여 한 번에 하나씩 변환하세요.

### 파일을 찾을 수 없음

데이터셋 경로가 올바른지 확인하세요:

```bash
# CLEVR_v1.0
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_v1.0

# CLEVR_CoGenT_v1.0
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0
```

### 특정 split이 인식되지 않음

`--all-splits` 옵션을 사용하여 사용 가능한 모든 split을 확인하세요:

```bash
python convert_clevr_to_excel.py --dataset_dir Dataset/CLEVR_CoGenT_v1.0 --all-splits
```

이 명령은 발견된 모든 split을 출력하고 변환합니다.

## 📝 라이선스

이 스크립트는 CLEVR 데이터셋과 동일한 라이선스(CC BY 4.0)를 따릅니다.

## 🔄 데이터셋 형식 지원

이 스크립트는 다음 CLEVR 데이터셋 형식을 지원합니다:

### CLEVR_v1.0
- 파일명 형식: `CLEVR_{split}_scenes.json`, `CLEVR_{split}_questions.json`
- Split: `train`, `val`, `test`

### CLEVR_CoGenT_v1.0
- 파일명 형식: `CLEVR_{split}A_scenes.json`, `CLEVR_{split}B_scenes.json` 등
- Split: `trainA`, `valA`, `valB`, `testA`, `testB`
- Compositional Generalization 테스트를 위한 데이터셋

### 자동 파일 탐지
스크립트는 디렉토리 내의 파일을 자동으로 스캔하여 패턴을 감지합니다:
- `CLEVR_{split}_*.json` 형식의 파일을 자동으로 찾음
- 여러 변형 (A, B 등)이 있어도 모두 처리
- `--all-splits` 옵션으로 모든 split을 한 번에 처리

## 📚 참고 자료

- [CLEVR 데이터셋 공식 사이트](https://cs.stanford.edu/people/jcjohns/clevr/)
- [CLEVR 논문](https://arxiv.org/abs/1612.06890)
- [CLEVR-CoGenT 논문](https://arxiv.org/abs/1707.05475)

