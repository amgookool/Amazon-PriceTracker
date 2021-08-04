FROM python:3-slim-buster

COPY . /amz_tracker

WORKDIR /amz_tracker

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","-u", "app/tracker.py"]