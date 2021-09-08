FROM python
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
RUN mkdir /images
WORKDIR /app
#RUN cat "host_key_checking = False" >> /etc/ansible/ansible.cfg
COPY templates/id_rsa /root/.ssh/id_rsa
ENV ANSIBLE_HOST_KEY_CHECKING=False
ENV OS_DOMAIN_NAME=default
ENV OS_DOMAIN_ID=default
# RUN export ANSIBLE_HOST_KEY_CHECKING=False
# RUN export OS_DOMAIN_NAME=default
# RUN export OS_DOMAIN_ID=default
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
RUN apt update
RUN apt install -y ansible
CMD python boot.py
