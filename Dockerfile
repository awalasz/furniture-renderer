FROM python:3.8.10
RUN apt-get update

RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /usr/src/app
COPY render_furniture /usr/src/app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "render_furniture.wsgi"]
