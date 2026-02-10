#!/bin/bash

# Script to sample GPU usage over time and compute average utilization
# Uses nvidia-smi to collect GPU metrics and awk for processing

# Number of samples to collect (1800 = 30 minutes at 1 sample/second)
SAMPLES=1800
# Temporary file to store raw GPU samples
TMPFILE=/tmp/gpu_samples.csv

# Clear the temporary file
: > $TMPFILE

# Collect GPU samples
for i in $(seq 1 $SAMPLES); do
  # Query GPU index, utilization percentage, and memory usage (in MiB)
  # Output format: CSV without header or units
  nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader,nounits >> $TMPFILE
  sleep 1
done

# Process collected samples to compute averages
awk -F', ' '{
  # Accumulate GPU utilization and memory usage by GPU index
  gpu[$1]+=$2;
  mem[$1]+=$3;
  count[$1]++
}
END {
  # Print average utilization and memory usage for each GPU
  for(i in gpu) {
    printf("GPU %s: avg_util=%.1f%%, avg_mem_used=%.0f MiB (samples=%d)\n", i, gpu[i]/count[i], mem[i]/count[i], count[i])
  }
}' $TMPFILE