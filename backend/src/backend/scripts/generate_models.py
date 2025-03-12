#!/usr/bin/env python3
# scripts/generate_models.py
import os
from dotenv import load_dotenv
import subprocess


def main():
    # Load environment variables from .env file
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

    # Define the output file for the generated models
    output_file = "./src/backend/shared/models/db/models.py"

    print(DATABASE_URL)
    # Run sqlacodegen-v2 to generate the models
    try:
        result = subprocess.run(
            ["poetry", "run", "sqlacodegen_v2", DATABASE_URL, "--outfile", output_file],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)
        print(f"Models generated and saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print("An error occurred while generating models:")
        print(e.stderr)


if __name__ == "__main__":
    main()
