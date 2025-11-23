# CLEVR_CoGenT 데이터셋으로 LLaVA 모델 평가 가이드

CLEVR_CoGenT 데이터셋을 사용하여 LLaVA 모델의 Compositional Generalization 능력을 평가하는 전체 프로세스입니다.

## 📋 목차

- [개요](#개요)
- [필요한 파일 구조](#필요한-파일-구조)
- [단계별 실행 방법](#단계별-실행-방법)
- [출력 결과 형식](#출력-결과-형식)
- [문제 해결](#문제-해결)

## 🎯 개요

### CLEVR_CoGenT 평가의 목적

CLEVR_CoGenT는 **Compositional Generalization** 능력을 테스트하기 위한 데이터셋입니다:

- **valA/testA**: 학습과 유사한 색상 조합 → 일반 성능 측정
- **valB/testB**: 학습과 다른 색상 조합 → Compositional Generalization 능력 측정
- **성능 차이 (valA - valB)**: 모델의 일반화 능력 지표

### 평가 프로세스

```
1. 데이터 변환 (CLEVR JSON → LLaVA JSONL)
   ↓
2. 모델 예측 생성 (멀티 GPU 병렬 처리)
   ↓
3. 정확도 계산 (평가 스크립트 실행)
   ↓
4. 결과 분석
```

## 📁 필요한 파일 구조

```
LLaVA/
├── Dataset/CLEVR_CoGenT_v1.0/
│   ├── images/
│   │   ├── trainA/
│   │   ├── valA/
│   │   ├── valB/
│   │   ├── testA/
│   │   └── testB/
│   └── questions/
│       ├── CLEVR_trainA_questions.json
│       ├── CLEVR_valA_questions.json
│       ├── CLEVR_valB_questions.json
│       ├── CLEVR_testA_questions.json
│       └── CLEVR_testB_questions.json
│
├── playground/data/eval/clevr_cogent/
│   ├── clevr_valA_questions.jsonl      # 변환된 질문 파일
│   ├── clevr_valB_questions.jsonl
│   ├── clevr_testA_questions.jsonl
│   ├── clevr_testB_questions.jsonl
│   ├── answers/
│   │   └── llava-v1.5-7b_valA/
│   │       ├── 4_0.jsonl                # GPU 0 결과
│   │       ├── 4_1.jsonl                # GPU 1 결과
│   │       ├── 4_2.jsonl                # GPU 2 결과
│   │       ├── 4_3.jsonl                # GPU 3 결과
│   │       └── merge.jsonl              # 병합된 결과
│   └── logs/
│       └── valA.log                     # 실행 로그
│
├── scripts/
│   ├── convert_clevr_to_llava.py       # 데이터 변환 스크립트
│   └── v1_5/eval/
│       └── clevr_cogent.sh             # 평가 실행 스크립트
└── llava/eval/
    └── eval_clevr.py                    # 평가 스크립트 (정확도 계산)
```

## 🚀 단계별 실행 방법

### 1단계: 데이터 변환

CLEVR questions JSON을 LLaVA JSONL 형식으로 변환합니다.

#### 모든 split 변환

```bash
cd /home/hdseo0388/class/bigdata_computing/PRO-V1/LLaVA

# 출력 디렉토리 생성
mkdir -p playground/data/eval/clevr_cogent

# 각 split 변환
python scripts/convert_clevr_to_llava.py \
    --input Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valA_questions.json \
    --output playground/data/eval/clevr_cogent/clevr_valA_questions.jsonl

python scripts/convert_clevr_to_llava.py \
    --input Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valB_questions.json \
    --output playground/data/eval/clevr_cogent/clevr_valB_questions.jsonl

python scripts/convert_clevr_to_llava.py \
    --input Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_testA_questions.json \
    --output playground/data/eval/clevr_cogent/clevr_testA_questions.jsonl

python scripts/convert_clevr_to_llava.py \
    --input Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_testB_questions.json \
    --output playground/data/eval/clevr_cogent/clevr_testB_questions.jsonl
```

#### 변환 스크립트 옵션

```bash
python scripts/convert_clevr_to_llava.py --help
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--input` | CLEVR questions JSON 파일 경로 | (필수) |
| `--output` | 출력 JSONL 파일 경로 | (필수) |
| `--no-prompt` | Short-answer 프롬프트 추가 안 함 | False |

### 2단계: 모델 예측 생성 (멀티 GPU)

멀티 GPU를 사용하여 병렬로 모델 예측을 생성합니다.

#### 실행 방법

```bash
# valA split 평가
bash scripts/v1_5/eval/clevr_cogent.sh valA

# valB split 평가
bash scripts/v1_5/eval/clevr_cogent.sh valB

# testA split 평가
bash scripts/v1_5/eval/clevr_cogent.sh testA

# testB split 평가
bash scripts/v1_5/eval/clevr_cogent.sh testB
```

#### 백그라운드 실행

```bash
# 로그와 함께 백그라운드 실행
nohup bash scripts/v1_5/eval/clevr_cogent.sh valA > playground/data/eval/clevr_cogent/logs/valA.log 2>&1 &

# 프로세스 ID 확인
echo $!
```

#### GPU 개수 조정

기본적으로 4개 GPU를 사용합니다. 다른 개수를 사용하려면:

```bash
# 2개 GPU만 사용
CUDA_VISIBLE_DEVICES=0,1 bash scripts/v1_5/eval/clevr_cogent.sh valA

# 8개 GPU 사용
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash scripts/v1_5/eval/clevr_cogent.sh valA
```

#### 실행 시간 예상

- **단일 GPU**: 약 8-9시간 (150,000개 질문)
- **4개 GPU 병렬**: 약 1.5-2시간
- **속도**: 약 6-7 질문/초 (GPU당)

### 3단계: 진행 상황 확인

#### 로그 확인

```bash
# 실시간 로그 확인
tail -f playground/data/eval/clevr_cogent/logs/valA.log

# 최근 50줄 확인
tail -50 playground/data/eval/clevr_cogent/logs/valA.log
```

#### GPU 사용률 확인

```bash
# GPU 사용률 실시간 모니터링
watch -n 1 nvidia-smi

# 간단한 확인
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv
```

#### 생성된 파일 확인

```bash
# 각 GPU별 결과 파일 확인
ls -lh playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/

# 파일 크기로 진행 상황 추정
du -sh playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/*
```

#### 프로세스 확인

```bash
# 실행 중인 프로세스 확인
ps aux | grep "model_vqa" | grep -v grep

# 각 GPU별 프로세스 확인
nvidia-smi
```

### 4단계: 결과 병합 확인

스크립트가 자동으로 결과를 병합합니다:

```bash
# 병합된 결과 파일 확인
ls -lh playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/merge.jsonl

# 결과 파일 개수 확인
wc -l playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/merge.jsonl
```

예상: 150,000줄 (각 줄이 하나의 질문에 대한 예측)

### 5단계: 정확도 계산 (평가 스크립트)

평가 스크립트(`eval_clevr.py`)를 사용하여 모델 예측 결과의 정확도를 계산합니다.

#### 기본 사용법

```bash
python -m llava.eval.eval_clevr \
    --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valA_questions.json \
    --result-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/merge.jsonl \
    --output-file playground/data/eval/clevr_cogent/results/valA_evaluation.json
```

**참고**: `--output-file` 옵션을 생략하면 결과가 콘솔에만 출력됩니다.

#### 상세 결과 저장

상세한 평가 결과를 JSON 파일로 저장하려면 `--output-file` 옵션을 사용합니다:

```bash
python -m llava.eval.eval_clevr \
    --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valA_questions.json \
    --result-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/merge.jsonl \
    --output-file playground/data/eval/clevr_cogent/results/valA_evaluation.json
```

#### 디렉토리 내 모든 파일 평가

디렉토리 내의 모든 JSONL 파일을 평가하려면:

```bash
python -m llava.eval.eval_clevr \
    --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valA_questions.json \
    --result-dir playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA
```

#### 모든 Split 평가

각 split에 대해 평가를 실행합니다:

```bash
# valA 평가
python -m llava.eval.eval_clevr \
    --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valA_questions.json \
    --result-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/merge.jsonl \
    --output-file playground/data/eval/clevr_cogent/results/valA_evaluation.json

# valB 평가
python -m llava.eval.eval_clevr \
    --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valB_questions.json \
    --result-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valB/merge.jsonl \
    --output-file playground/data/eval/clevr_cogent/results/valB_evaluation.json

# testA 평가
python -m llava.eval.eval_clevr \
    --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_testA_questions.json \
    --result-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_testA/merge.jsonl \
    --output-file playground/data/eval/clevr_cogent/results/testA_evaluation.json

# testB 평가
python -m llava.eval.eval_clevr \
    --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_testB_questions.json \
    --result-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_testB/merge.jsonl \
    --output-file playground/data/eval/clevr_cogent/results/testB_evaluation.json
```

## 📊 출력 결과 형식

### 1단계: 모델 예측 생성 결과

**파일 형식**: JSONL (각 줄이 하나의 JSON 객체)

**예시**:
```json
{"question_id": 0, "prompt": "How many blue cubes are there?\nAnswer the question using a single word or phrase.", "text": "2", "answer_id": "...", "model_id": "llava-v1.5-7b", "metadata": {}}
{"question_id": 1, "prompt": "Are there more red spheres than blue cubes?", "text": "Yes", "answer_id": "...", "model_id": "llava-v1.5-7b", "metadata": {}}
```

**특징**:
- `text` 필드: 모델이 생성한 텍스트 답변
- 수치 없음: 정확도는 평가 스크립트에서 계산

### 2단계: 평가 결과

**출력 예시**:
```
============================================================
CLEVR Evaluation Results
============================================================
Total Questions: 150000
Correct: 120000
Incorrect: 30000
Missing: 0
Accuracy: 80.00%

By Question Family:
  Family 0: 85.23% (12345/14478)
  Family 1: 78.45% (9876/12567)
  Family 2: 82.10% (11234/13689)
  ...

By Program Length:
  Length 1: 90.12% (45123/50000)
  Length 2: 88.45% (44225/50000)
  Length 3: 82.34% (41170/50000)
  Length 4: 75.67% (37835/50000)
  Length 5: 70.23% (35115/50000)
  Length 6: 65.45% (32725/50000)
  ...
============================================================
```

**상세 결과 JSON 파일 구조** (`--output-file`로 저장된 파일):

```json
{
  "summary": {
    "total": 150000,
    "correct": 120000,
    "incorrect": 30000,
    "missing": 0,
    "accuracy": 80.0
  },
  "by_family": {
    "0": {
      "total": 14478,
      "correct": 12345,
      "accuracy": 85.23
    },
    ...
  },
  "by_program_length": {
    "1": {
      "total": 50000,
      "correct": 45123,
      "accuracy": 90.24
    },
    ...
  },
  "results": {
    "correct": [...],
    "incorrect": [...],
    "missing": [...]
  }
}
```

### 3단계: Excel 변환

평가 결과 JSON 파일을 Excel로 변환하여 더 쉽게 분석할 수 있습니다.

#### 기본 사용법

```bash
python scripts/convert_eval_results_to_excel.py \
    --input-json playground/data/eval/clevr_cogent/results/valA_evaluation.json \
    --output-excel playground/data/eval/clevr_cogent/results/valA_evaluation.xlsx
```

#### 상세 결과 포함

정답/오답/누락된 질문의 상세 정보를 포함하려면 `--include-details` 옵션을 사용합니다:

```bash
python scripts/convert_eval_results_to_excel.py \
    --input-json playground/data/eval/clevr_cogent/results/valA_evaluation.json \
    --output-excel playground/data/eval/clevr_cogent/results/valA_evaluation.xlsx \
    --include-details \
    --max-details 10000
```

**옵션 설명**:
- `--input-json`: 입력 평가 결과 JSON 파일 경로
- `--output-excel`: 출력 Excel 파일 경로 (생략 시 입력 파일과 같은 이름에 .xlsx 확장자)
- `--include-details`: 상세 결과 시트 포함 (정답/오답/누락된 질문 목록)
- `--max-details`: 상세 결과 시트의 최대 행 수 (기본값: 10000)

#### Excel 파일 구조

변환된 Excel 파일은 다음 시트로 구성됩니다:

1. **Summary**: 전체 요약 통계
   - Total Questions
   - Correct
   - Incorrect
   - Missing
   - Accuracy (%)

2. **By Family**: 질문 패밀리별 정확도
   - Family Index
   - Total
   - Correct
   - Incorrect
   - Accuracy (%)

3. **By Program Length**: 프로그램 길이별 정확도
   - Program Length
   - Total
   - Correct
   - Incorrect
   - Accuracy (%)

4. **Correct Results** (선택적): 정답인 질문 목록
   - question_id
   - question
   - ground_truth
   - prediction

5. **Incorrect Results** (선택적): 오답인 질문 목록
   - question_id
   - question
   - ground_truth
   - prediction

6. **Missing Results** (선택적): 누락된 질문 목록
   - question_id
   - question
   - ground_truth
   - prediction

## 🔍 실행 상태 모니터링

### 진행 상황 확인

```bash
# 1. 로그에서 진행률 확인
tail -20 playground/data/eval/clevr_cogent/logs/valA.log | grep -E "[0-9]+%|it/s"

# 2. 생성된 파일 크기로 추정
ls -lh playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/4_*.jsonl

# 3. 각 파일의 줄 수 확인
wc -l playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/4_*.jsonl
```

### 예상 출력

각 GPU별로 다음과 같은 진행률이 표시됩니다:
```
  0%|          | 0/37500 [00:00<?, ?it/s]
  10%|█         | 3750/37500 [00:10<01:30, 6.5it/s]
  20%|██        | 7500/37500 [00:20<01:20, 6.7it/s]
  ...
  100%|██████████| 37500/37500 [01:30<00:00, 6.8it/s]
```

## ⚙️ 스크립트 설정

### `clevr_cogent.sh` 주요 설정

```bash
# GPU 설정 (기본값: 0,1,2,3)
gpu_list="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"

# 모델 경로
MODEL_PATH="liuhaotian/llava-v1.5-7b"

# 데이터 경로
BASE_DIR="./playground/data/eval/clevr_cogent"
DATASET_DIR="./Dataset/CLEVR_CoGenT_v1.0"
```

### 생성 파라미터

- `--temperature 0`: 결정적 생성 (재현 가능)
- `--conv-mode llava_v1`: 대화 모드
- `--num-chunks`: GPU 개수에 따라 자동 설정
- `--chunk-idx`: 각 GPU별로 0부터 시작

## 🔧 문제 해결

### GPU 메모리 부족

```bash
# GPU 메모리 확인
nvidia-smi

# 더 적은 GPU 사용
CUDA_VISIBLE_DEVICES=0,1 bash scripts/v1_5/eval/clevr_cogent.sh valA
```

### 프로세스가 중단된 경우

```bash
# 실행 중인 프로세스 확인
ps aux | grep "model_vqa" | grep -v grep

# 특정 chunk만 다시 실행
CUDA_VISIBLE_DEVICES=0 python -m llava.eval.model_vqa \
    --model-path liuhaotian/llava-v1.5-7b \
    --question-file playground/data/eval/clevr_cogent/clevr_valA_questions.jsonl \
    --image-folder Dataset/CLEVR_CoGenT_v1.0/images/valA \
    --answers-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/4_0.jsonl \
    --num-chunks 4 \
    --chunk-idx 0 \
    --temperature 0 \
    --conv-mode llava_v1
```

### 결과 파일이 불완전한 경우

```bash
# 각 chunk 파일의 줄 수 확인
wc -l playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/4_*.jsonl

# 예상: 각 파일 약 37,500줄
# 부족한 chunk만 다시 실행
```

### 로그 파일 확인

```bash
# 에러 확인
grep -i error playground/data/eval/clevr_cogent/logs/valA.log

# 경고 확인
grep -i warning playground/data/eval/clevr_cogent/logs/valA.log
```

## 📈 전체 평가 워크플로우

### 모든 split 평가 (순차 실행)

```bash
# 1. 모든 split 변환 (이미 완료)
# 2. 각 split 평가 (병렬 또는 순차)

# valA 평가
bash scripts/v1_5/eval/clevr_cogent.sh valA

# valB 평가 (valA 완료 후)
bash scripts/v1_5/eval/clevr_cogent.sh valB

# testA 평가
bash scripts/v1_5/eval/clevr_cogent.sh testA

# testB 평가
bash scripts/v1_5/eval/clevr_cogent.sh testB
```

### 병렬 실행 (주의: GPU 메모리 확인 필요)

```bash
# 여러 split을 동시에 실행 (각각 다른 GPU 사용)
CUDA_VISIBLE_DEVICES=0,1 bash scripts/v1_5/eval/clevr_cogent.sh valA &
CUDA_VISIBLE_DEVICES=2,3 bash scripts/v1_5/eval/clevr_cogent.sh valB &
wait
```

## 📝 다음 단계

### 평가 스크립트 작성 필요

현재는 모델 예측만 생성됩니다. 정확도 수치를 얻으려면 평가 스크립트가 필요합니다:

1. `llava/eval/eval_clevr.py` 작성
   - 정답과 예측 비교
   - 정확도 계산
   - 질문 유형별 분석

2. 평가 실행
   ```bash
   python -m llava.eval.eval_clevr \
       --annotation-file Dataset/CLEVR_CoGenT_v1.0/questions/CLEVR_valA_questions.json \
       --result-file playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/merge.jsonl
   ```

## 💡 팁

1. **작은 샘플로 먼저 테스트**: 전체 실행 전에 작은 샘플로 테스트
   ```bash
   head -100 playground/data/eval/clevr_cogent/clevr_valA_questions.jsonl > test.jsonl
   ```

2. **로그 파일 모니터링**: 실시간으로 진행 상황 확인
   ```bash
   tail -f playground/data/eval/clevr_cogent/logs/valA.log
   ```

3. **결과 파일 백업**: 완료된 결과는 백업 권장
   ```bash
   cp -r playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA/ \
       playground/data/eval/clevr_cogent/answers/llava-v1.5-7b_valA_backup/
   ```

## 📚 참고 자료

- [CLEVR 데이터셋 공식 사이트](https://cs.stanford.edu/people/jcjohns/clevr/)
- [CLEVR 논문](https://arxiv.org/abs/1612.06890)
- [CLEVR-CoGenT 논문](https://arxiv.org/abs/1707.05475)
- [LLaVA Evaluation 가이드](docs/Evaluation.md)

