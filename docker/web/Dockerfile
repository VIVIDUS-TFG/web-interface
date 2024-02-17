from python:3.10-alpine

RUN apk add --no-cache git

WORKDIR /app

# RUN git clone https://github.com/VIVIDUS-TFG/web-interface.git .
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
