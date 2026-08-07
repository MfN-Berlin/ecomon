#!/bin/bash

find . -maxdepth 1 -type d -name 'MGB*' | sort | while read -r dir; do
    dirname=$(basename "$dir")
    date_part="${dirname#*_}"
    wav_count=$(find "$dir" -type f -name "*.wav" | wc -l)
    echo "$dir: $wav_count"
done
