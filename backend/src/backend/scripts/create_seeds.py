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


def create_models_seed():
    """
    For every CSV file in the local LabelToIdMappings directory, extract its name (without .csv)
    to be used as the model name. Then, for each row in that CSV (ignoring the header), create an
    INSERT statement into the model_labels table using the dstLabelId.

    The SQL file for models is saved to the Hasura seeds folder.
    """
    download_dir = "LabelToIdMappings"
    seed_sql = ""

    # Process each CSV file in the directory
    for index, filename in enumerate(os.listdir(download_dir)):
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
    print(f"Model seed SQL file created at {output_path}")


def create_labels_seed_sql_file():
    """
    Reads the CSV file (assumed to be at ./assets/LabelsMfnDb.csv) and generates INSERT
    statements for the public.labels table.

    The labels seed SQL file is saved to the Hasura seeds folder.
    """
    csv_file = "./assets/LabelsMfnDb.csv"
    seed_sql = "-- Seed for labels\n\n"

    # This helper function properly quotes text and handles NULL values.
    def sql_str(val):
        if val is None or str(val).strip() == "":
            return "NULL"
        else:
            # Escape single quotes by doubling them.
            return "'" + str(val).replace("'", "''") + "'"

    try:
        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract the column values
                id_val = row.get("id")
                name = row.get("name")
                english = row.get("english")
                german = row.get("german")
                gbif = row.get("gbif")
                class_val = row.get("class")  # CSV uses the column name "class"
                order_val = row.get("order")

                # Use the CSV id if it is a digit; otherwise, set to NULL.
                id_sql = id_val if id_val and id_val.isdigit() else "NULL"

                seed_sql += (
                    f'INSERT INTO public.labels (id, name, english, german, gbif, "class", "order") VALUES '
                    f"({id_sql}, {sql_str(name)}, {sql_str(english)}, {sql_str(german)}, {sql_str(gbif)}, {sql_str(class_val)}, {sql_str(order_val)});\n"
                )
    except FileNotFoundError:
        print(f"Labels CSV file not found at {csv_file}")
        return

    # Define the output directory (create it if it doesn't exist)
    output_dir = os.path.join("../", "hasura", "seeds", "ecomon")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir, f"{int(datetime.now().timestamp())}_labels_seed.sql"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(seed_sql)
    print(f"Labels seed SQL file created at {output_path}")


def main():
    # Download mapping files from the repository.
    download_csv_files_from_repo()

    create_labels_seed_sql_file()
    # Create seed SQL for models and model_labels based on CSV files in LabelToIdMappings.
    create_models_seed()


if __name__ == "__main__":
    main()
