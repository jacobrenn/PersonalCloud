FROM python:3.12

RUN pip install --upgrade pip httpx 'pyagent-harness[api]'

RUN useradd --create-home --shell /bin/bash pyagent
USER pyagent

RUN mkdir /home/pyagent/.pyagent
COPY --chown=pyagent:pyagent ./profiles.json /home/pyagent/.pyagent/profiles.json

COPY --chown=pyagent:pyagent ./searxng.py ./searxng.py
RUN pyagent tools install ./searxng.py

WORKDIR /home/pyagent

CMD ["pyagent", "serve", "--host", "0.0.0.0", "--port", "8000"]
