FROM python
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
RUN mkdir /temp
RUN mkdir /images
WORKDIR /app
ENV ANSIBLE_HOST_KEY_CHECKING=False
ENV OS_DOMAIN_NAME=default
ENV OS_DOMAIN_ID=default
RUN apt update
RUN apt install -y ansible
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY templates/id_rsa /root/.ssh/id_rsa
COPY . /app/
CMD python boot.py
