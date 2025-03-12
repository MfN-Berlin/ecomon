import random
import os
from datetime import datetime, timedelta
import sys
from pathlib import Path
from faker import Faker
from dotenv import load_dotenv

# Add the project root to Python path to import the models
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.shared.models.db.models import (
    Locations,
    Models,
    Sites,
    Records,
    SetInformations,
    Sets,
)

# Initialize Faker with German locale for German names
fake = Faker(["de_DE", "la"])  # la for Latin-like names

# List of real bird species for more realistic data
BIRD_SPECIES = [
    ("Parus major", "Kohlmeise"),
    ("Erithacus rubecula", "Rotkehlchen"),
    ("Turdus merula", "Amsel"),
    ("Cyanistes caeruleus", "Blaumeise"),
    ("Fringilla coelebs", "Buchfink"),
    ("Passer domesticus", "Haussperling"),
    ("Carduelis carduelis", "Stieglitz"),
    ("Sitta europaea", "Kleiber"),
    ("Dendrocopos major", "Buntspecht"),
    ("Columba palumbus", "Ringeltaube"),
]


def generate_version():
    """Generate a semantic version number"""
    major = random.randint(0, 3)
    minor = random.randint(0, 9)
    patch = random.randint(0, 9)
    return f"{major}.{minor}.{patch}"


def create_dummy_data(db_url: str, num_entries: int = 5):
    engine = create_engine(db_url)
    session = Session(engine)

    try:
        # Create Labels

        # Create Models
        models = []
        model_types = ["BirdNET", "OpenSoundscape", "DeepSpectrogram"]
        for _ in range(num_entries):
            name = f"{random.choice(model_types)}-v{generate_version()}"
            model = Models(
                short_name=name.lower(),
                name=name,
                endpoint=f"/api/models/{fake.slug()}",
                remarks=fake.sentence(),
            )
            models.append(model)
            session.add(model)
        session.flush()  # Flush to get IDs

        # Create Locations
        locations = []
        for _ in range(num_entries):
            location = Locations(
                name=fake.city(),
                lat=random.uniform(47.27, 55.05),  # Germany's latitude bounds
                long=random.uniform(5.87, 15.04),  # Germany's longitude bounds
                remarks=fake.text(max_nb_chars=100),
            )
            locations.append(location)
            session.add(location)
        session.flush()  # Flush to get IDs

        # Create Sites
        sites = []
        for i in range(num_entries):
            site = Sites(
                name=f"Site {fake.city()}",
                location_id=locations[i].id,  # This ensures we use a valid location_id
                sample_rate=random.choice([44100, 48000, 96000]),
                remarks=fake.text(max_nb_chars=200),
                alias=f"SITE_{fake.lexify(text='???').upper()}",
                record_regime_recording_duration=random.choice([300, 600]),
                record_regime_pause_duration=random.choice([0, 60, 300]),
            )
            sites.append(site)
            session.add(site)
        session.flush()  # Flush to get IDs

        # Create Records
        records = []
        for _ in range(num_entries * 10):  # More records for realistic data
            site = random.choice(sites)
            record_date = fake.date_time_between(start_date="-6M")
            record = Records(
                site_id=site.id,
                filepath=f"/data/{site.alias}/AudioMoth_{record_date.strftime('%Y%m%d_%H%M%S')}.wav",
                filename=f"AudioMoth_{record_date.strftime('%Y%m%d_%H%M%S')}.wav",
                record_datetime=record_date,
                duration=site.record_regime_recording_duration,
                channels="0",
                sample_rate=site.sample_rate,
                mime_type="audio/wav",
            )
            records.append(record)
            session.add(record)
        session.flush()  # Flush to get IDs

        # Create SetInformations and Sets
        for _ in range(num_entries):
            start_date = fake.date_time_between(start_date="-1y")
            end_date = fake.date_time_between(start_date=start_date)
            set_info = SetInformations(
                start_date=start_date.date(),
                end_date=end_date.date(),
                record_regime_recording_duration=300,
                record_regime_pause_duration=0,
                record_count=len(records) // num_entries,
                record_duration=(len(records) // num_entries) * 300,
                corrupted_record_count=random.randint(0, 5),
            )
            session.add(set_info)
            session.flush()  # Flush to get ID

            test_set = Sets(
                name=f"Dataset {fake.word().capitalize()} {fake.date('%Y-%m')}",
                set_information_id=set_info.id,
                remarks=fake.text(max_nb_chars=100),
            )
            session.add(test_set)

        # Create SiteDirectories
        # for site in sites:
        #     directory = SiteDirectories(
        #         site_id=site.id, directory=f"/data/{site.alias}"
        #     )
        #     session.add(directory)

        session.commit()
        print("Successfully created dummy data!")

    except Exception as e:
        print(f"Error creating dummy data: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def main():
    load_dotenv()

    # Retrieve database connection details from environment variables
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Construct the database URL
    DATABASE_URL = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    create_dummy_data(DATABASE_URL)


if __name__ == "__main__":
    main()
