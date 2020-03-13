FROM python:3.7
COPY Database.py ptt_scrapy.py ./
ADD requirements.txt ./
RUN pip install -r requirements.txt
CMD python ptt_scrapy.py