FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

WORKDIR /app

RUN sed -i 's|http://archive.ubuntu.com|https://archive.ubuntu.com|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com|https://security.ubuntu.com|g' /etc/apt/sources.list

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends \
    git curl ffmpeg libgl1 libglib2.0-0 tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U openmim

RUN mim install mmengine mmcv==2.1.0 --timeout 1000

RUN git clone --depth 1 https://github.com/open-mmlab/mmaction2.git
WORKDIR /app/mmaction2
RUN pip install -e .

RUN pip install importlib_metadata

WORKDIR /app

COPY ml-service/worker/ worker/
COPY ml-service/requirements.txt requirements.txt
COPY vigil-tasks /app/vigil-tasks

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install /app/vigil-tasks

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "-Q", "ml"]