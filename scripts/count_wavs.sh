#!/bin/bash

find . -maxdepth 1 -type d -name 'AKWAMO*' | sort | while read -r dir; do
    dirname=$(basename "$dir")
    date_part="${dirname#*_}"
    if [ "$date_part" -ge "2026" ]; then
        wav_count=$(find "$dir" -type f -name "*.wav" | wc -l)
        echo "$dir: $wav_count"
    fi
done
