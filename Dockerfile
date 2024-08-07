FROM python:3.10-alpine3.20


WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

##cache
RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r requirements.txt


CMD ["python3","manage.py","runserver","0:8000"]





