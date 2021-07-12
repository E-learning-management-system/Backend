FROM python:latest

COPY . /app
WORKDIR /app

RUN export PYTHONDONTWRITEBYTECODE=1
RUN export PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y locales netcat-openbsd gcc gettext && \
    sed -i -e 's/# fa_IR UTF-8/fa_IR UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    apt-get clean

RUN export LANG="fa_IR.UTF-8"
RUN export LC_ALL="fa_IR.UTF-8"

RUN pip install -r requirements.txt

ENTRYPOINT [ "bash", "/app/entrypoint.sh" ]