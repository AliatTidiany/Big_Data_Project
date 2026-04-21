# Import des classes pour gérer le temps (date et délai)
from datetime import datetime, timedelta

# Import de la classe principale pour créer un DAG Airflow
from airflow import DAG

# Import de l'opérateur pour exécuter des commandes bash
from airflow.operators.bash import BashOperator


# Dictionnaire des paramètres par défaut appliqués à toutes les tâches
default_args = {
    'owner': 'niakoaliou',  # Propriétaire du DAG (utile pour tracking/logs)

    'depends_on_past': False,  
    # Si True → une tâche dépend du succès de son exécution précédente
    # Ici False → chaque run est indépendant

    'start_date': datetime(2025, 4, 1),  
    # Date à partir de laquelle Airflow peut commencer à planifier le DAG

    'retries': 1,  
    # Nombre de tentatives si une tâche échoue

    'retry_delay': timedelta(minutes=5),  
    # Temps d’attente entre deux tentatives
}


# Création du DAG
dag = DAG(
    'dbt_bookshop_pipeline-DIT',  
    # Identifiant unique du DAG dans Airflow (très important)

    default_args=default_args,  
    # Applique les paramètres définis plus haut

    description='Exécute dbt run pour les couches staging, warehouse, marts',  
    # Description visible dans l’UI Airflow

    schedule_interval='@daily',  
    # Planification → exécution tous les jours

    catchup=False,  
    # Ne pas exécuter les DAGs passés (évite backlog massif)
)


# Définition du répertoire du projet dbt dans le conteneur
DBT_PROJECT_DIR = '/opt/airflow'
DBT_PROFILES_DIR = '/opt/airflow/.dbt'  


# =========================
# Task 1 : dbt staging
# =========================
run_staging = BashOperator(
    task_id='run_dbt_staging',  
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --models staging.* --profiles-dir {DBT_PROFILES_DIR}',  
    dag=dag,  
)

# =========================
# Task 2 : dbt warehouse
# =========================
run_warehouse = BashOperator(
    task_id='run_dbt_warehouse',  
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --models warehouse.* --profiles-dir {DBT_PROFILES_DIR}',  
    dag=dag,
)

# =========================
# Task 3 : dbt marts
# =========================
run_marts = BashOperator(
    task_id='run_dbt_marts',  
    bash_command=f'cd {DBT_PROJECT_DIR} && dbt run --models marts.* --profiles-dir {DBT_PROFILES_DIR}',  
    dag=dag,
)
# =========================
# Définition de l’ordre d’exécution
# =========================
run_staging >> run_warehouse >> run_marts

# Signification :
# 1. staging s’exécute en premier
# 2. puis warehouse
# 3. puis marts
# (pipeline séquentiel classique en data engineering)