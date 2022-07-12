FROM python:3.9.7

WORKDIR /project_amazon


ADD . /project_amazon

RUN pip install -r  requirements.txt

CMD ["python","/main.py"]