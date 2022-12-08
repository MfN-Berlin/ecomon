#!/bin/python3
from dotenv import load_dotenv
import os

# - ${MDAS_DATA_DIRECTORY}:/mnt/data
# - ${MDAS_RESULT_DIRECTORY}:/mnt/result
load_dotenv()
header_str = """version: "3"
services:"""
port = 7100
result = "" + header_str
for i in range(0, 30):
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
            data=os.getenv("MDAS_DATA_DIRECTORY"),
            result=os.getenv("MDAS_RESULT_DIRECTORY"),
        )
    )

print(result)

