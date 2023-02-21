FROM python

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade setuptools

RUN pip3 install -r requirements.txt

COPY . .

ENV TOKEN "5491017548:AAGkPfGEhk6FLf77YJMbgxuitlG1tjkIgzo"

ENV PASSWORD ";f,f"

ENV PORT 4200

VOLUME [ "/app/data" ]

CMD ["python", "main.py"]