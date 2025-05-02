FROM python:3.12-slim
WORKDIR /backend

RUN apt update && apt install wget pkg-config unzip xorg  \
    openbox xvfb python3-tk python3-dev default-libmysqlclient-dev build-essential -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install ./google-chrome-stable_current_amd64.deb -y
RUN apt install -f
RUN rm ./google-chrome-stable_current_amd64.deb

COPY requirements-prod.txt .
COPY . .

RUN pip install --no-cache-dir -r requirements-prod.txt

RUN seleniumbase get chromedriver
RUN Xvfb :99 -screen 0 1024x768x24 & export DISPLAY=:99

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "3000"]