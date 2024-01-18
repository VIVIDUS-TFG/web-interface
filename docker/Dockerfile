from python:3.10-alpine

RUN apk add --no-cache git

WORKDIR /code

RUN git clone https://github.com/VIVIDUS-TFG/web-interface.git .
RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
