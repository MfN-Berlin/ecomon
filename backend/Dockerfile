
FROM python:3.9
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN mkdir /files
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install pytz
RUN pip install pyyaml
COPY ./ /code/app
WORKDIR /code/app
ENV ROOT_PATH "/"
CMD ["./run.prod.sh"]
