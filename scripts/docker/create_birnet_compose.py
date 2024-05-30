#!/bin/python3
import argparse
from dotenv import load_dotenv
import os

load_dotenv()

header_str = """version: "3"
services:"""

def generate_birdnet_config(count, output_file):
    port = 7100
    result = "" + header_str
    for i in range(0, count):
        result = (
            result
            + """
        birdnet-{number}:
          container_name: "bai-birdnet-{number}"
          image: birdnet-public-3k-v2.2:latest
          restart: always
          ipc: host
          ports:
             - "{port}:6000"
          volumes:
             - {data}:/mnt/data
             - {result}:/mnt/result
          environment:
            - OVERLAP=1
    """.format(
                number=i,
                port=port + i,
                data=os.getenv("DATA_DIRECTORY"),
                result=os.getenv("RESULT_DIRECTORY"),
            )
        )
    with open(output_file, "w") as f:
        f.write(result)
    print("Docker Compose configuration written to {}".format(output_file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('count', type=int, help='the number of BirdNET containers to create')
    parser.add_argument('output_file', help='the path of the output file to write the Docker Compose configuration to')
    args = parser.parse_args()
    generate_birdnet_config(args.count, args.output_file)
