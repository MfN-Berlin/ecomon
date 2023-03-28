from dotenv import load_dotenv
from util.db import DbWorker


ANALYZE_THREADS = 7
load_dotenv()  # load environment variables from .env
PREFIX = "BRITZ01_2022"
species_index_list = [
"grus_grus",
"ardea_cinerea",
"strix_aluco",
"dendrocoptes_medius",
"dendrocopos_major",
"lophophanes_cristatus",
"phylloscopus_sibilatrix",
"phylloscopus_trochilus",
"phylloscopus_collybita",
"locustella_luscinioides",
"sylvia_atricapilla",
"regulus_ignicapilla",
"troglodytes_troglodytes",
"turdus_merula",
"turdus_philomelos",
"turdus_viscivorus",
"erithacus_rubecula",
"luscinia_luscinia",
"phoenicurus_ochruros",
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
