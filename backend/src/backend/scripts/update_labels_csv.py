import csv
import os
import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.shared.models.db.models import Labels
from dotenv import load_dotenv

load_dotenv()
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def get_engine():
    """
    Create the SQLAlchemy engine using the DATABASE_URL environment variable.
    """
    DATABASE_URL = (
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    return create_engine(DATABASE_URL)


def read_labels_csv(file_path: str):
    """
    Reads the CSV file and returns a list of dictionaries,
    one per CSV row.
    """
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader]
    return rows


def sync_labels(csv_file: str):
    """
    Syncs the labels table with the CSV file:
    - Deletes labels that are no longer in the CSV.
    - Updates labels that already exist.
    - Inserts new labels.

    All changes are committed once at the end for speed.
    """
    # Read CSV data
    csv_rows = read_labels_csv(csv_file)
    # Build a set of label names (unique constraint) from the CSV
    csv_label_names = {row["name"].strip() for row in csv_rows if row.get("name")}

    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Delete Labels that are no longer in the CSV.
        # Using bulk delete, note that synchronize_session is disabled for speed.
        deleted_count = (
            session.query(Labels)
            .filter(~Labels.name.in_(csv_label_names))
            .delete(synchronize_session=False)
        )
        print(f"Deleted {deleted_count} labels not found in CSV.")

        # Query existing labels present in the CSV.
        existing_labels = (
            session.query(Labels).filter(Labels.name.in_(csv_label_names)).all()
        )
        existing_labels_dict = {label.name: label for label in existing_labels}

        inserted_count = 0
        updated_count = 0

        for row in csv_rows:
            name = row.get("name").strip() if row.get("name") else None
            if not name:
                continue

            # Convert CSV "id" to an integer if provided and a valid digit.
            csv_id = int(row["id"]) if row.get("id") and row["id"].isdigit() else None

            # Prepare the values using CSV column names.
            # Note: the CSV column "class" maps to the model attribute "class_"
            label_data = {
                "id": csv_id,
                "name": name,
                "english": row.get("english"),
                "german": row.get("german"),
                "gbif": row.get("gbif"),
                "class_": row.get("class"),
                "order": row.get("order"),
            }

            if name in existing_labels_dict:
                # Update existing label
                label_obj = existing_labels_dict[name]
                for key, value in label_data.items():
                    setattr(label_obj, key, value)
                updated_count += 1
            else:
                # Insert new label. If CSV provides an id and it's valid, pass it;
                # otherwise the DB might auto-generate it.
                new_label = Labels(**label_data)
                session.add(new_label)
                inserted_count += 1

        # Commit all changes at once for better performance.
        session.commit()
        print(
            f"Inserted {inserted_count} labels; updated {updated_count} labels; deleted {deleted_count} labels."
        )
    except Exception as e:
        session.rollback()
        print(f"An error occurred during label sync: {e}")
    finally:
        session.close()


def main():
    sync_labels("./assets/LabelsMfnDb.csv")


if __name__ == "__main__":
    main()
