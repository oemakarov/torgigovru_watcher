FROM python:3.9-slim

COPY *.py ./
COPY lib lib
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

#часовой пояс Москва
ENV TZ='Europe/Moscow'
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD [ "python", "./app.py" ] 