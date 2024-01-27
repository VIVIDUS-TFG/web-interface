FROM python:3.10-slim

RUN apt-get update && apt-get install -y wget git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/VIVIDUS-TFG/video_features.git

ENV MINICONDA_VERSION 4.8.2
ENV PATH /opt/conda/bin:$PATH
RUN wget \
    "https://repo.anaconda.com/miniconda/Miniconda3-py38_${MINICONDA_VERSION}-Linux-x86_64.sh" \
    -O /miniconda.sh \
    && bash /miniconda.sh -b -p /opt/conda \
    && rm /miniconda.sh \
    && conda clean -tipsy

WORKDIR /app/video_features

RUN conda env create -f conda_env_torch_zoo.yml

RUN conda run -n torch_zoo pip install fastapi "uvicorn[standard]"

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY endpoint.py /app/endpoint.py

WORKDIR /app

CMD ["/app/entrypoint.sh"]