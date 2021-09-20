FROM python
RUN mkdir /app && mkdir /temp
WORKDIR /app
RUN apt update && apt install -y ansible vim cron
COPY requirements.txt requirements-added.txt /app/
ENV ANSIBLE_HOST_KEY_CHECKING=False OS_DOMAIN_NAME=default OS_DOMAIN_ID=default TZ="Asia/Tehran"
RUN pip install -r requirements.txt
RUN pip install -r requirements-added.txt
#COPY templates/id_rsa /root/.ssh/id_rsa
COPY . /app/
RUN crontab /app/daemons/crontab
CMD python boot.py
