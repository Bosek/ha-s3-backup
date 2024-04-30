FROM python:3

WORKDIR /home/app

COPY . .
RUN chmod 0744 main.py

RUN pip3 install --no-cache-dir -r requirements.txt

RUN apt update && apt -y install cron

ENTRYPOINT ["./entrypoint.sh"]
CMD printenv > /etc/environment && cron -f