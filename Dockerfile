FROM python

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade setuptools

RUN pip3 install -r requirements.txt

COPY . .

ENV TOKEN "YOUR TOKEN"

ENV PASSWORD "YOUR PASSWORD"

ENV PORT 4200

VOLUME [ "/app/data" ]

CMD ["python", "main.py"]