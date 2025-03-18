from datetime import datetime
import os
import csv
import requests


def download_csv_files_from_repo():
    # API URL for the contents of the LabelToIdMappings folder on the main branch
    api_url = "https://api.github.com/repos/MfN-Berlin/BirdID-Model-Zoo/contents/LabelToIdMappings"
    params = {"ref": "main"}

    # Get the directory contents from the GitHub API
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        print(f"Error fetching directory contents: {response.status_code}")
        return

    files = response.json()

    # Create a local directory for downloads if it doesn't exist
    download_dir = "LabelToIdMappings"
    os.makedirs(download_dir, exist_ok=True)

    # Loop through each item in the folder, filtering for CSV files
    for item in files:
        if item["type"] == "file" and item["name"].endswith(".csv"):
            download_url = item["download_url"]
            file_name = item["name"]
            print(f"Downloading {file_name}...")
            file_response = requests.get(download_url)
            if file_response.status_code == 200:
                file_path = os.path.join(download_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(file_response.content)
                print(f"Downloaded {file_name} to {file_path}")
            else:
                print(
                    f"Error downloading file {file_name}: {file_response.status_code}"
                )


def create_seed_sql_file():
    """
    For every CSV file in the local LabelToIdMappings directory, extract its name (without .csv)
    to be used as the model name. Then, for each row in that CSV (ignoring the header), create an
    INSERT statement into the model_labels table using the dstLabelId.

    The SQL file is saved to `hasura/migrations/ecomon/seed_models/up.sql`.
    """
    download_dir = "LabelToIdMappings"
    seed_sql = ""

    # Process each CSV file in the directory
    for filename, index in enumerate(os.listdir(download_dir)):
        if filename.endswith(".csv"):
            # Use filename (without extension) as the model name
            model_name = filename[:-4]
            file_path = os.path.join(download_dir, filename)
            print(f"Processing seed for model: {model_name} using file: {file_path}")

            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                # Start a DO block for this model so we can capture the generated id.
                seed_sql += f"-- Seed for model: {model_name}\n"
                seed_sql += "DO $$\nDECLARE\n    model_id integer;\nBEGIN\n"
                seed_sql += f"    INSERT INTO public.models (id, name) VALUES ({index}, '{model_name}') RETURNING id INTO model_id;\n"

                for row in reader:
                    dst_label_id = row.get("dstLabelId")
                    if dst_label_id is not None and dst_label_id.strip() != "":
                        # Create an INSERT for model_labels using the captured model_id
                        seed_sql += f"    INSERT INTO public.model_labels (model_id, label_id) VALUES ({index}, {dst_label_id});\n"
                seed_sql += "END $$;\n\n"

    # Define the output directory (create it if it doesn't exist)
    output_dir = os.path.join("../", "hasura", "seeds", "ecomon")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir, f"{int(datetime.now().timestamp())}_model_seeds.sql"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(seed_sql)
    print(f"Seed SQL file created at {output_path}")


def main():
    download_csv_files_from_repo()
    create_seed_sql_file()


if __name__ == "__main__":
    main()
