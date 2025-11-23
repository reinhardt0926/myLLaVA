#!/bin/bash

# CLEVR_CoGenT 평가 스크립트 (멀티 GPU 병렬 처리)

gpu_list="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"
IFS=',' read -ra GPULIST <<< "$gpu_list"

CHUNKS=${#GPULIST[@]}

MODEL_PATH="liuhaotian/llava-v1.5-7b"
SPLIT="${1:-valA}"  # 기본값: valA

BASE_DIR="./playground/data/eval/clevr_cogent"
DATASET_DIR="./Dataset/CLEVR_CoGenT_v1.0"

echo "=========================================="
echo "CLEVR_CoGenT Evaluation: $SPLIT"
echo "Using $CHUNKS GPUs: ${gpu_list}"
echo "=========================================="

# 각 GPU에서 병렬로 실행
for IDX in $(seq 0 $((CHUNKS-1))); do
    echo "Starting GPU ${GPULIST[$IDX]} (chunk $IDX/$((CHUNKS-1)))..."
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python -m llava.eval.model_vqa \
        --model-path ${MODEL_PATH} \
        --question-file ${BASE_DIR}/clevr_${SPLIT}_questions.jsonl \
        --image-folder ${DATASET_DIR}/images/${SPLIT} \
        --answers-file ${BASE_DIR}/answers/${MODEL_PATH##*/}_${SPLIT}/${CHUNKS}_${IDX}.jsonl \
        --num-chunks $CHUNKS \
        --chunk-idx $IDX \
        --temperature 0 \
        --conv-mode llava_v1 &
done

echo "Waiting for all GPUs to finish..."
wait

echo "Merging results..."
output_file=${BASE_DIR}/answers/${MODEL_PATH##*/}_${SPLIT}/merge.jsonl
mkdir -p $(dirname $output_file)

# Clear out the output file if it exists.
> "$output_file"

# Loop through the indices and concatenate each file.
for IDX in $(seq 0 $((CHUNKS-1))); do
    chunk_file=${BASE_DIR}/answers/${MODEL_PATH##*/}_${SPLIT}/${CHUNKS}_${IDX}.jsonl
    if [ -f "$chunk_file" ]; then
        cat "$chunk_file" >> "$output_file"
        echo "Merged chunk $IDX"
    else
        echo "Warning: Chunk file not found: $chunk_file"
    fi
done

echo "=========================================="
echo "Prediction generation completed!"
echo "Output file: $output_file"
echo "Next step: Run evaluation script to get accuracy numbers"
echo "=========================================="

