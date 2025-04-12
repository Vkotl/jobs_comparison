FROM python:3.12-slim
WORKDIR /backend

# install google chrome
RUN apt update && apt install wget unzip -y

RUN apt update
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install ./google-chrome-stable_current_amd64.deb -y
RUN apt install -f
RUN wget https://storage.googleapis.com/chrome-for-testing-public/135.0.7049.84/linux64/chrome-linux64.zip
RUN unzip chrome-linux64.zip
RUN mv chrome-linux64 /usr/bin/chromedriver && \
    chown root:root /usr/bin/chromedriver && chmod +x /usr/bin/chromedriver


COPY ./requirements.txt .
COPY ./backend /backend/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "3000"]