import helper
import psycopg2
from helper import minio_connection
import io

def dump_to_postgres(data_interval_end):

    minio_client = minio_connection()
    data = minio_client.get_object(helper.BUCKET_NAME, f"iris/{data_interval_end.to_date_string()}/prediction/predictions.csv")
    print("Dados lidos do bucket",data)

    # Connectar to PostgreSQL
    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="host.docker.internal",
        port="5432"
    )
    cur = conn.cursor()

    # Apagar os dados que já existem para a data de execução e copiar novos dados do CSV
    copy_sql = f"""
    DELETE FROM iris.predictions WHERE execution_date::date = '{data_interval_end.to_date_string()}'::date;   
    COPY airflow.iris.predictions FROM stdin WITH CSV HEADER DELIMITER ','
    """

    #ler os dados e passar para um file-like object
    data_bytes = data.read()
    data_file = io.BytesIO(data_bytes)

    # Apontar para o início do ficheiro
    data_file.seek(0)

    #Executa a query
    cur.copy_expert(sql=copy_sql, file=data_file)
    conn.commit()

    # Fechar as conexões
    cur.close()
    conn.close()
        

