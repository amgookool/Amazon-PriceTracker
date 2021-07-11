FROM python:3-buster

WORKDIR /amz_tracker

COPY . /amz_tracker/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python","app/tracker.py" ]