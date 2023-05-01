FROM python:3.11.3-slim-buster

WORKDIR /calculator/

ADD ./Services/3WayCalculator/3WayCalculator.py /calculator/
ADD ./Core/RESTClients/ /calculator/Core/RESTClients/
ADD ./Core/Tools/ /calculator/Core/Tools/
ADD ./.env /calculator/
ADD ./Services/3WayCalculator/requirements.txt /calculator/

# RUN apt-get update && apt-get upgrade -y && apt-get install gcc -y
RUN pip install --upgrade setuptools pip wheel
RUN pip install --no-cache-dir -r /calculator/requirements.txt

CMD [ "python", "3WayCalculator.py" ]