# Big Data Project - Bookshop

## Objectif du projet

Le projet consiste à prendre des données brutes de vente de livres et les transformer en une table unique optimisée pour l’analyse, appelée : OBT (One Big Table). On part de données désorganisées et brutes, et on les transforme étape par étape pour obtenir des données : propres, structurées et facile à analyser. Une pipeline Big Data

---

##  Structure du projet (VS Code)

```
Big_Data_Project/
│
├── 📁 .dbt/                        # Configuration DBT (Aliou)
│   └── profiles.yml                # Connexion DBT → Snowflake
│
├── 📁 dags/                        # Orchestration Airflow (Niako)
│   └── dbt_pipeline.py             # DAG Airflow
│
├── 📁 docker/                      # Docker Compose (Niako)
│   └── docker-compose.yml          # PostgreSQL + pgAdmin + Airflow
│
├── 📁 models/                      # Modèles DBT (Aliou)
│   ├── 📁 staging/                 # RAW → STAGGING (5 fichiers)
│   │   ├── stg_category.sql
│   │   ├── stg_books.sql
│   │   ├── stg_customers.sql
│   │   ├── stg_factures.sql
│   │   ├── stg_ventes.sql
│   │   └── sources.yml
│   ├── 📁 warehouse/               # STAGGING → WAREHOUSE (8 fichiers)
│   │   ├── dim_category.sql
│   │   ├── dim_books.sql
│   │   ├── dim_customers.sql
│   │   ├── fact_ventes.sql
│   │   ├── fact_factures.sql
│   │   ├── fact_books_annees.sql
│   │   ├── fact_books_mois.sql
│   │   └── fact_books_jour.sql
│   └── 📁 marts/                   # WAREHOUSE → MARTS (1 fichier)
│       └── obt_sales.sql
│
├── 📁 scripts/                     # Scripts d'ingestion (Niako)
│   ├── ingest_data.py              # PostgreSQL → Snowflake
│   ├── init_postgres.sql           # Création tables PostgreSQL
│   └── create_tables_snowflake.sql # Création tables RAW Snowflake
│
├── 📁 data/                        # Données de test (optionnel)
│
├── 📁 tests/                       # Tests DBT (optionnel)
│
├── dashboard.py                    # Dashboard Streamlit (Niako)
├── requirements.txt                # Dépendances Python
├── dbt_project.yml                 # Configuration DBT
├── .gitignore                      # Fichiers ignorés par Git
├── architecture.png                # Schéma architecture
├── LICENSE                         # Licence MIT
└── README.md                       # Ce fichier
```

---

##  Étape 1 : PostgreSQL avec Docker (Niako) - TERMINÉE ✅

### Objectif
Créer une base de données locale PostgreSQL avec Docker pour stocker les données brutes.

### Ce qui a été fait
- Création du fichier `docker/docker-compose.yml`
- Lancement des conteneurs :
  - **PostgreSQL 15** (port 5432)
  - **pgAdmin 4** (port 5050)
- Création des 5 tables : `category`, `books`, `customers`, `factures`, `ventes`
- Insertion des données de test (5-6 lignes par table)

### Commandes utilisées
```bash
cd docker
docker-compose up -d
docker ps
```

### Accès
| Service | URL | Identifiants |
|---------|-----|---------------|
| pgAdmin | http://localhost:5050 | email: admin@bookshop.com / mdp: admin2026 |
| PostgreSQL | localhost:5432 | user: adminan / mdp: admin2026 |

### Structure des tables (officielle - fournie par le professeur)

**category**
| Colonne | Type |
|---------|------|
| id | SERIAL PRIMARY KEY |
| intitule | VARCHAR(100) |
| created_at | TIMESTAMP |

**books**
| Colonne | Type |
|---------|------|
| id | SERIAL PRIMARY KEY |
| category_id | INTEGER (FK → category.id) |
| code | VARCHAR(50) |
| intitule | VARCHAR(200) |
| isbn_10 | VARCHAR(20) |
| isbn_13 | VARCHAR(20) |
| created_at | TIMESTAMP |

**customers**
| Colonne | Type |
|---------|------|
| id | SERIAL PRIMARY KEY |
| code | VARCHAR(50) |
| first_name | VARCHAR(100) |
| last_name | VARCHAR(100) |
| created_at | TIMESTAMP |

**factures**
| Colonne | Type |
|---------|------|
| id | SERIAL PRIMARY KEY |
| code | VARCHAR(50) |
| date_edit | VARCHAR(8) (format YYYYMMDD) |
| customers_id | INTEGER (FK → customers.id) |
| qte_totale | INTEGER |
| total_amount | DECIMAL(10,2) |
| total_paid | DECIMAL(10,2) |
| created_at | TIMESTAMP |

**ventes**
| Colonne | Type |
|---------|------|
| id | SERIAL PRIMARY KEY |
| code | VARCHAR(50) |
| date_edit | VARCHAR(8) (format YYYYMMDD) |
| factures_id | INTEGER (FK → factures.id) |
| books_id | INTEGER (FK → books.id) |
| pu | DECIMAL(10,2) |
| qte | INTEGER |
| created_at | TIMESTAMP |

---

##  Prochaines étapes

### Étape 2 : Snowflake (Aliou)
- [ ] Créer compte Snowflake (free trial)
- [ ] Créer base `BOOKSHOP`
- [ ] Créer schémas `RAW`, `STAGGING`, `WAREHOUSE`, `MARTS`
- [ ] Créer tables RAW

### Étape 3 : Ingestion (Niako)
- [ ] Script Python `ingest_data.py`
- [ ] Envoyer données PostgreSQL → Snowflake.RAW

### Étape 4 : DBT (Aliou)
- [ ] Modèles staging (RAW → STAGGING)
- [ ] Modèles warehouse (STAGGING → WAREHOUSE)
- [ ] Modèle marts (WAREHOUSE → MARTS.obt_sales)

### Étape 5 : Airflow (Niako)
- [ ] DAG pour orchestrer DBT

### Étape 6 : Visualisation (Niako + Aliou)
- [ ] Dashboard Streamlit

### Étape 7 : Livrables
- [ ] Document PDF
- [ ] PowerPoint
- [ ] Vidéo démo

---

##  Installation des dépendances

```bash
# Créer environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Installer les packages
pip install -r requirements.txt
```

### Contenu de `requirements.txt`
```txt
snowflake-connector-python>=3.0.0
dbt-core>=1.5.0
dbt-snowflake>=1.5.0
apache-airflow>=2.7.0
psycopg2-binary>=2.9.0
pandas>=2.0.0
streamlit>=1.25.0
plotly>=5.17.0
sqlalchemy>=2.0.0
```

---

##  Liens utiles

| Outil | URL |
|-------|-----|
| pgAdmin | http://localhost:5050 |
| Airflow | http://localhost:8080 |
| Snowflake | https://app.snowflake.com/ |
| GitHub | https://github.com/AliatTidiany/Big_Data_Project |

---

##  Avancement

| Étape | Statut | Responsable |
|-------|--------|-------------|
| PostgreSQL + Docker | ✅ TERMINÉ | Niako |
| Tables + données PostgreSQL | ✅ TERMINÉ | Niako |
| Snowflake (base + schémas) | ⏳ À faire | Aliou |
| Ingestion PostgreSQL → Snowflake | ⏳ À faire | Niako |
| DBT (staging, warehouse, marts) | ⏳ À faire | Aliou |
| Airflow | ⏳ À faire | Niako |
| Dashboard Streamlit | ⏳ À faire | Ensemble |
| Livrables (PDF, PPT, vidéo) | ⏳ À faire | Ensemble |

---

##  Notes importantes

- Les dates `date_edit` sont stockées en VARCHAR(8) au format `YYYYMMDD` (ex: `20250315`)
- La table `ventes` fait la liaison entre `factures` et `books`
- Le projet respecte l'architecture Medallion : RAW → STAGGING → WAREHOUSE → MARTS


## ARCHITECTURE DU PROJET 

![Architecture](architecture.png)