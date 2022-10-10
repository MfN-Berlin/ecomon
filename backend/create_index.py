from time import sleep
import threading, queue
import yaml
import glob
from dotenv import load_dotenv
from worker.analyze import analyze_loop_factory
from worker.store import store_loop_factory
from util.db import init_db
from pytz import timezone
from util.db import connect_to_db, DbWorker

from util.tools import (
    load_config,
    load_files_list,
    load_json,
    load_files_list,
)

ANALYZE_THREADS = 7
load_dotenv()  # load environment variables from .env
PREFIX = "BRITZ01_2022"
species_index_list = [
    "grus_grus",
    "ardea_cinerea",
    "dendrocopos_medius",
    "dendrocopos_major",
    "lophophanes_cristatus",
    "phylloscopus_trochilus",
    "phylloscopus_collybita",
    "locustella_luscinioides",
    "sylvia_atricapilla",
    "regulus_ignicapilla",
    "turdus_merula",
    "turdus_viscivorus",
    "erithacus_rubecula",
    "luscinia_luscinia",
    "phoenicurus_phoenicurus",
    "fringilla_coelebs",
]


db_worker = DbWorker(PREFIX)
for species in species_index_list:
    print("Adding index to {}".format(species))
    try:
        db_worker.add_index(PREFIX, species)
        print("Finished adding index to species columns")
    except Exception as e:
        print(e)
        db_worker.rollback()
