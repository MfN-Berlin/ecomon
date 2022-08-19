
FROM python:3.8
RUN mkdir /files
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./ /code/app
WORKDIR /code/app
ENV ROOT_PATH "/"
CMD ["./run.prod.sh"]