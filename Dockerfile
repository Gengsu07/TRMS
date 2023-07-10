# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y cron python3-dev libpq-dev build-essential 


COPY . .
COPY crontab /etc/cron.d/crontab


RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt

# Give execution rights to the cron job
RUN chmod 0644 /etc/cron.d/crontab
# Apply the cron job
RUN crontab /etc/cron.d/crontab
CMD ["cron", "-f"]

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]