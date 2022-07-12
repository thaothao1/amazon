FROM python:3.9.7

COPY . .

WORKDIR /amazon

ADD . /

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt


CMD [ "python" , "-m", "flask", "run", "--host=0.0.0.0" ]

EXPOSE 5000
