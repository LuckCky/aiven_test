FROM python:3.9.1
COPY . /app
WORKDIR /app
ENV PYTHONPATH=/app
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD python producer/main.py 2>&1