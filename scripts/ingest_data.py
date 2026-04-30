### ------------------------------------------------ INGESTION POSTGRE-SNOWFLAKE -------------------------------------------

"""
Script d'ingestion : PostgreSQL (Docker) → Snowflake
"""

import pandas as pd
import snowflake.connector
import psycopg2
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =====================================================
# CONFIGURATION
# =====================================================

# Connexion PostgreSQL (Docker)
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'bookshop_local',
    'user': 'adminan',
    'password': 'admin2026'
}

# Connexion Snowflake
SNOWFLAKE_CONFIG = {
    'user': 'ATTIDIANY',
    'password': "{{ env_var('SNOWFLAKE_PASSWORD') }}",
    'account': 'iwledsd-ow30473',
    'warehouse': 'COMPUTE_WH',
    'database': 'BOOKSHOP',
    'schema': 'RAW'
}

# =====================================================
# FONCTIONS
# =====================================================

def get_postgres_connection():
    """Établit la connexion à PostgreSQL"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        logger.info(" Connexion PostgreSQL établie")
        return conn
    except Exception as e:
        logger.error(f" Erreur connexion PostgreSQL: {e}")
        raise

def get_snowflake_connection():
    """Établit la connexion à Snowflake"""
    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        logger.info(" Connexion Snowflake établie")
        return conn
    except Exception as e:
        logger.error(f" Erreur connexion Snowflake: {e}")
        raise

def create_raw_tables(sf_conn):
    """Crée les tables RAW dans Snowflake si elles n'existent pas"""
    logger.info(" Création des tables RAW dans Snowflake...")
    
    create_statements = [
        """
        CREATE TABLE IF NOT EXISTS BOOKSHOP.RAW.category (
            id INTEGER,
            intitule VARCHAR(100),
            created_at VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS BOOKSHOP.RAW.books (
            id INTEGER,
            category_id INTEGER,
            code VARCHAR(50),
            intitule VARCHAR(200),
            isbn_10 VARCHAR(20),
            isbn_13 VARCHAR(20),
            created_at VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS BOOKSHOP.RAW.customers (
            id INTEGER,
            code VARCHAR(50),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            created_at VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS BOOKSHOP.RAW.factures (
            id INTEGER,
            code VARCHAR(50),
            date_edit VARCHAR(8),
            customers_id INTEGER,
            qte_totale INTEGER,
            total_amount DECIMAL(10,2),
            total_paid DECIMAL(10,2),
            created_at VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS BOOKSHOP.RAW.ventes (
            id INTEGER,
            code VARCHAR(50),
            date_edit VARCHAR(8),
            factures_id INTEGER,
            books_id INTEGER,
            pu DECIMAL(10,2),
            qte INTEGER,
            created_at VARCHAR(100)
        )
        """
    ]
    
    cursor = sf_conn.cursor()
    try:
        for stmt in create_statements:
            cursor.execute(stmt)
        logger.info(" Tables RAW créées avec succès")
    except Exception as e:
        logger.error(f" Erreur création tables: {e}")
        raise
    finally:
        cursor.close()

def migrate_table(pg_conn, sf_conn, table_name):
    """Migre une table de PostgreSQL vers Snowflake"""
    logger.info(f" Migration de la table '{table_name}'...")
    
    # Lire les données depuis PostgreSQL
    df = pd.read_sql(f"SELECT * FROM {table_name}", pg_conn)
    logger.info(f"    {len(df)} lignes lues depuis PostgreSQL")
    
    if df.empty:
        logger.warning(f"    Table {table_name} vide, rien à migrer")
        return
    
    # Convertir toutes les colonnes datetime en string
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
    
    # Vider la table Snowflake avant insertion
    cursor = sf_conn.cursor()
    try:
        cursor.execute(f"DELETE FROM BOOKSHOP.RAW.{table_name}")
        logger.info(f"    Table Snowflake vidée")
    finally:
        cursor.close()
    
    # Insérer les données ligne par ligne
    for _, row in df.iterrows():
        cursor = sf_conn.cursor()
        try:
            columns = ', '.join(df.columns)
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_sql = f"INSERT INTO BOOKSHOP.RAW.{table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(insert_sql, tuple(row))
        except Exception as e:
            logger.error(f"    Erreur insertion ligne: {row.to_dict()}")
            logger.error(f"    Erreur: {e}")
            raise
        finally:
            cursor.close()
    
    logger.info(f"    {len(df)} lignes insérées dans Snowflake")

def verify_migration(sf_conn):
    """Vérifie que les données ont bien été migrées"""
    logger.info(" Vérification de la migration...")
    
    tables = ['category', 'books', 'customers', 'factures', 'ventes']
    cursor = sf_conn.cursor()
    
    try:
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM BOOKSHOP.RAW.{table}")
            count = cursor.fetchone()[0]
            logger.info(f"    {table}: {count} lignes dans Snowflake")
    finally:
        cursor.close()

# =====================================================
# MAIN
# =====================================================

def main():
    logger.info("=" * 50)
    logger.info(" DÉBUT DE L'INGESTION PostgreSQL → Snowflake")
    logger.info("=" * 50)
    
    pg_conn = None
    sf_conn = None
    
    try:
        # 1. Connexions
        pg_conn = get_postgres_connection()
        sf_conn = get_snowflake_connection()
        
        # 2. Créer les tables RAW dans Snowflake
        create_raw_tables(sf_conn)
        
        # 3. Migrer chaque table
        tables = ['category', 'books', 'customers', 'factures', 'ventes']
        for table in tables:
            migrate_table(pg_conn, sf_conn, table)
        
        # 4. Vérification
        verify_migration(sf_conn)
        
        logger.info("=" * 50)
        logger.info("🎉 INGESTION TERMINÉE AVEC SUCCÈS")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f" ERREUR: {e}")
        raise
    finally:
        if pg_conn:
            pg_conn.close()
        if sf_conn:
            sf_conn.close()

if __name__ == "__main__":
    main()