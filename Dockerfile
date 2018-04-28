FROM python:3.5-alpine
ADD . /app
WORKDIR /app
RUN apk add --update --no-cache g++ gcc libxml2-dev libxslt-dev py-virtualenv \
 musl-dev python3-dev libffi-dev openssl-dev zlib-dev postgresql-dev
ENV LANG ru_RU.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL ru_RU.UTF-8
RUN virtualenv --python=python3.5 /env_app
ADD ./user_path.pth /env_app/lib/python3.5/site-packages/user_path.pth
RUN source /env_app/bin/activate && /env_app/bin/pip install -r requirements.txt
RUN chmod +x /app/start_app.sh