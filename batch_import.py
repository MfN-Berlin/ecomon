#!/home/mfn0480/anaconda3/envs/batch_inference/bin/python
import os
configs = [
    "backend/config/config-BIRDNET_WALLBERGE-2018.yaml",
    "backend/config/config-BIRDNET_WALLBERGE-2019.yaml",
    "backend/config/config-BIRDNET_WALLBERGE-2020.yaml",
    "backend/config/config-BIRDNET_WALLBERGE-2021.yaml",
    "backend/config/config-BIRDNET_WALLBERGE-2022.yaml",
    "backend/config/config-BIRDNET_BRITZ01-2018.yaml",
    "backend/config/config-BIRDNET_BRITZ01-2019.yaml",
    "backend/config/config-BIRDNET_BRITZ01-2020.yaml",
    "backend/config/config-BIRDNET_BRITZ01-2021.yaml",
    "backend/config/config-BIRDNET_BRITZ01-2022.yaml",
]


for config in configs:
    os.system("python3 backend/import_records.py " + config + " --create_index")