FROM python:3.11.3

ADD result.py .

RUN pip install jira

CMD ["python","./result.py"]
