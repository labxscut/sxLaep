FROM continuumio/miniconda3:latest

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    http_proxy=http://host.docker.internal:7890 \
    https_proxy=http://host.docker.internal:7890 \
    all_proxy=socks5://host.docker.internal:7891

WORKDIR /workspace


RUN conda config --add channels conda-forge && \
    conda config --set proxy_servers.http http://host.docker.internal:7890 && \
    conda config --set proxy_servers.https https://host.docker.internal:7890


RUN conda create -n sxLaep_docker python=3.11 -y && \
    conda clean -afy


COPY . /tmp/sxlaep
RUN pip install --no-cache-dir --prefer-binary /tmp/sxlaep && \
    rm -rf /tmp/sxlaep


SHELL ["conda", "run", "-n", "sxLaep_docker", "/bin/bash", "-c"]

RUN python --version

CMD ["python", "--version"]