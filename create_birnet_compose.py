#!/bin/python3
from dotenv import load_dotenv
import os
         # - ${BAI_DATA_DIRECTORY}:/mnt/data
         # - ${BAI_RESULT_DIRECTORY}:/mnt/result
load_dotenv()
header_str ="""version: "3"
services:"""
port = 7100
result = "" + header_str
for i in range(0,30):
    result = result + """
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
""".format(number=i,port=port+i,
data=os.getenv("BAI_DATA_DIRECTORY"),
result=os.getenv("BAI_RESULT_DIRECTORY"))

print(result)

   