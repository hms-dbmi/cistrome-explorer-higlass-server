FROM continuumio/miniconda3:4.6.14

ENV PATH /opt/conda/bin:$PATH

# tini: https://github.com/krallin/tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

RUN apt-get update && apt-get install -y \
        gcc \
        nginx-full \
        supervisor \
        unzip \
        uwsgi-plugin-python3 \
        zlib1g-dev \
        libcurl4-openssl-dev \
        g++ \
        vim \
        build-essential \
        libssl-dev \
        libpng-dev \
        procps \
        git \
        fuse \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /software
RUN curl -L -o /software/goofys https://github.com/kahing/goofys/releases/latest/download/goofys
RUN chmod +x /software/goofys

RUN mkdir -p /data

ENV HTTPFS_HTTP_DIR /data/media/http
ENV HTTPFS_HTTPS_DIR /data/media/https
ENV GOOFYS_DIR /data/media/s3

WORKDIR /higlass-server
COPY environment.yml ./environment.yml
RUN conda env create -f ./environment.yml

COPY docker-context/nginx.conf /etc/nginx/
COPY docker-context/hgserver_nginx.conf /etc/nginx/sites-enabled/
RUN rm /etc/nginx/sites-*/default && grep 'listen' /etc/nginx/sites-*/*

COPY docker-context/uwsgi_params ./
COPY docker-context/default-viewconf-fixture.xml ./

COPY docker-context/supervisord.conf ./
COPY docker-context/uwsgi.ini ./

COPY docker-context/start.sh ./
RUN chmod +x ./start.sh

EXPOSE 80

ENV HIGLASS_SERVER_BASE_DIR /data
VOLUME /data
VOLUME /tmp

ARG WORKERS=2
ENV WORKERS ${WORKERS}
RUN echo "WORKERS: $WORKERS"

COPY . .

CMD ["supervisord", "-n", "-c", "/higlass-server/supervisord.conf"]
