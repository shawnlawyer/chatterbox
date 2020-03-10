FROM fedora:28
WORKDIR /var/www/html
EXPOSE 443

ARG tensorflow_installed=1
RUN dnf -y update && dnf clean all

RUN dnf install -y \
    nginx \
    screen \
    unzip \
    wget \
    nodejs \
    && dnf clean all \
    && npm update -g \
    && npm install -g n \
    && npm cache clean -f \
    && n stable

RUN pip3 install --no-cache-dir \
    envs \
    flask \
    flask-ask \
    ask-sdk \
    flask-ask-sdk \
    flask-admin \
    requests \
    pyap \
    peewee \
    wtf-peewee \
    psycopg2-binary \
    cryptography==2.0 \
    pytemperature \
    geopy \
    pymysql \
    address-parser \
    street-address \
    phonetics \
    pytz \
    python-slugify \
    numpy \
    flask-admin \
    flask-security-too \
    pusher


RUN if [ $tensorflow_installed -gt 0 ]; then pip3 install --no-cache-dir tensorflow pandas nltk; fi

#RUN pip3 install tflite_runtime-1.14.0-cp36-cp36m-linux_x86_64.whl

#RUN pip3 install \
#    pandas

#RUN pip3 install \
#    nltk

RUN npm install -g \
    ask-cli

COPY . /var/www/html
COPY ./docker/nginx.conf /etc/nginx/
COPY ./jupyter/nltk_data/ /usr/share/nltk_data/
RUN ln -sf /dev/stdout /var/www/html/access.log && ln -sf /dev/stderr /var/www/html/error.log
RUN echo "screen -r" > /root/.bash_history

ENTRYPOINT ["/var/www/html/start.sh"]

