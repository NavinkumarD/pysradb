import os
import requests
import gzip
import csv
import argparse


def download_geo_matrix(accession):
    """
    Download and decompress the GEO Matrix file from the NCBI GEO repository.

    Parameters:
    accession (str): GEO accession number (e.g., 'GSE10072').

    Returns:
    str: Path to the decompressed GEO Matrix file.
    """
    base_url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{accession[:5]}nnn/{accession}/matrix/"
    file_name = f"{accession}_series_matrix.txt.gz"
    file_url = base_url + file_name

    print(f"Attempting to download from: {file_url}")

    try:
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(file_name, 'wb') as gz_file:
                gz_file.write(response.content)
            print(f"Downloaded: {file_name}")

            decompressed_file = file_name.replace('.gz', '')
            with gzip.open(file_name, 'rb') as compressed_file, open(decompressed_file, 'wb') as output_file:
                output_file.write(compressed_file.read())
            print(f"Decompressed: {decompressed_file}")

            os.remove(file_name)
            print(f"Cleaned up: {file_name}")
            return decompressed_file
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def parse_geo_matrix_to_tsv(input_file, output_file):
    """
    Parse the GEO Matrix file and convert it into a .tsv file.

    Parameters:
    input_file (str): Path to the decompressed GEO Matrix file.
    output_file (str): Path to the output .tsv file.
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            for line in infile:
                if not line.startswith('!'):  # Skip metadata lines starting with '!'
                    row = line.strip().split('\t')
                    writer.writerow(row)
        print(f"Parsed and saved as: {output_file}")
    except Exception as e:
        print(f"Error parsing file: {e}")


def main():
    """
    Main function to handle CLI commands for downloading and parsing GEO Matrix files.
    """
    parser = argparse.ArgumentParser(description="Download and parse GEO Matrix files.")
    parser.add_argument('--accession', type=str, required=True, help="GEO accession number (e.g., GSE10072).")
    parser.add_argument('--to-tsv', type=str, required=True, help="Output .tsv file path.")
    args = parser.parse_args()

    accession = args.accession
    tsv_file = args.to_tsv

    decompressed_file = download_geo_matrix(accession)
    if decompressed_file:
        parse_geo_matrix_to_tsv(decompressed_file, tsv_file)


if __name__ == "__main__":
    main()