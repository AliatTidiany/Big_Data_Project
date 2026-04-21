FROM apache/airflow:2.7.1-python3.10

USER root

# On copie le fichier en restant root pour être sûr d'avoir les droits

COPY requirements.txt /requirements.txt

# ON REPASSE SUR L'UTILISATEUR AIRFLOW AVANT LE PIP INSTALL
USER airflow

RUN pip install --no-cache-dir -r /requirements.txt