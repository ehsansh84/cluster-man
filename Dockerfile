FROM python
RUN mkdir /app && mkdir /temp
# RUN mkdir /images
WORKDIR /app
# ENV PYTHONUNBUFFERED 1
ENV ANSIBLE_HOST_KEY_CHECKING=False OS_DOMAIN_NAME=default OS_DOMAIN_ID=default
RUN apt update && apt install -y ansible vim
COPY requirements.txt requirements-added.txt /app/
RUN pip install -r requirements.txt
RUN pip install -r requirements-added.txt
COPY templates/id_rsa /root/.ssh/id_rsa
COPY . /app/
CMD python boot.py
