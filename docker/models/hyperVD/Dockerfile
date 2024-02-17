FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y wget git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/VIVIDUS-TFG/HyperVD.git .

RUN pip install --no-cache-dir pipreqs fastapi "uvicorn[standard]"
RUN pipreqs .

RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY endpoint.py /app/endpoint.py

CMD ["/app/entrypoint.sh"]