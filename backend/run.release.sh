#!/bin/bash
docker build -t ecomon/ecomon-backend:latest .
docker push ecomon/ecomon-backend:latest
