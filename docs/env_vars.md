
## USE_GPU

**USE_GPU=None**

No GPU will be used, model runs on CPU.

**USE_GPU=X**

Attemp to use GPU. USE_GPU=0 will attempt to use the first GPU etc.
If the GPU can't be used, the model will generally fallback to CPU.


**USE_GPU=all**

This will start the model with GPU 0, then the next run will be on GPU 1, then back to 0. Used for running multiple models in parallel. Note that the default behaviour of the GPU scheduler that comes with nvidia will attempt to distribute processing among all GPUs. This is different, as the default behavior causes problems with some models.

You can check GPU usgae by calling `bash sample_gpu_usage.sh` This wil sample GPU usage over 1/2 hour and print the average for each GPU.

Currently, this is
```
GPU 0: avg_util=25.6%, avg_mem_used=5317 MiB (samples=1800)
GPU 1: avg_util=27.8%, avg_mem_used=5069 MiB (samples=1800)
```

You can also do `watch -n 0.5 nvidia-smi` for a quick check of memory usage and energy consumption.
