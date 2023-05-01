FROM python:3.11.3-slim-buster

WORKDIR /spreadcalc/

ADD ./Services/SpreadCalculator/SpreadCalculator.py /spreadcalc/
ADD ./Core/RESTClients/ /spreadcalc/Core/RESTClients/
ADD ./Core/Tools/ /spreadcalc/Core/Tools/
ADD ./.env /spreadcalc/
ADD ./Services/SpreadCalculator/requirements.txt /spreadcalc/

# RUN apt-get update && apt-get upgrade -y && apt-get install gcc -y
RUN pip install --upgrade setuptools pip wheel
RUN pip install --no-cache-dir -r /spreadcalc/requirements.txt

CMD [ "python", "SpreadCalculator.py" ]