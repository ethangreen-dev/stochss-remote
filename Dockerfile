FROM python:3.9-buster

LABEL maintainer="Ethan Green <egreen4@unca.edu>"

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PYTHONPATH="$VIRTUAL_ENV:$PYTHONPATH"
ENV PATH="$VIRTUAL_ENV:$PATH"

VOLUME [ "/opt/venv" ]

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

# VOLUME [ "/usr/src/app/env" ]

COPY . /usr/src/app


ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
    PYTHONUNBUFFERED="true"

EXPOSE 1234

EXPOSE 8786

CMD [ "python", "app.py" ]