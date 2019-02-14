FROM python:3.7.1-stretch

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt 
WORKDIR /app 
RUN pip install -r requirements.txt

COPY synchronize.sh /app
RUN chmod +x /app/synchronize.sh

COPY pkg /app/pkg

CMD ["/app/synchronize.sh"]
