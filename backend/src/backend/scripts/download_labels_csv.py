import requests


def main():
    """
    Downloads the Labels csv from githubg CSV file from the GitHub repository and saves it locally.

    The raw URL is used to fetch the actual CSV content.
    """
    # GitHub raw URL for the CSV file
    url = "https://raw.githubusercontent.com/MfN-Berlin/BirdID-Model-Zoo/main/LabelsMfnDb.csv"
    local_filename = "./assets/LabelsMfnDb.csv"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if an error occurs
    except requests.exceptions.RequestException as error:
        print(f"An error occurred: {error}")
        return

    # Write the content to a file in binary mode
    with open(local_filename, "wb") as file:
        file.write(response.content)

    print(f"CSV file downloaded successfully and saved as '{local_filename}'.")


if __name__ == "__main__":
    main()
