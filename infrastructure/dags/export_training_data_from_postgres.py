import pandas as pd
import helper
from jinja2 import Template
import psycopg2
from io import BytesIO
from helper import minio_connection


def connect_and_read(flag,data_interval_end):
    # Conectar ao PostgreSQL
    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="host.docker.internal",
        port="5432"
    )
    cur = conn.cursor()
    import os


    # Especificar o path para o file export_data.sql
    sql_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export_data.sql')

    sql_template = Template(open(sql_file_path).read())

    #flag tanto pode ser train ou test 
    sql_query = sql_template.render(flag=flag)  

    #Executar a query SQL para selecionar os dados de interesse
    cur.execute(sql_query)  

    # guardar numa variável e fechar conexões ao PostgreSQL
    df = cur.fetchall()
    cur.close()
    conn.close()
    print("lista",df)

    #criar um pandas dataframe com as colunas necessárias
    colunaflag = ['flag']
    columns= helper.Numerical_columns+helper.target_column+colunaflag   #todas as colunas
    df = pd.DataFrame(df, columns=columns)
    print("pandas",df)

    # Conectar ao MinIO
    minio_client = minio_connection()
    found = minio_client.bucket_exists(helper.BUCKET_NAME)
    if not found:
        minio_client.make_bucket(helper.BUCKET_NAME)
        print("A criar bucket...")       
    else:
        print(f"Bucket '{helper.BUCKET_NAME}' encontrado com sucesso")

    # Gera o nome completo do objeto para ser dumped no Bucket
    prefix = f"iris/{data_interval_end.to_date_string()}/{flag}"
    object_name = prefix + f"/{flag}_data.csv"

    #Elimina o objeto se já existir nesse path
    a = minio_client.remove_object(helper.BUCKET_NAME, object_name)

    # Converte o DataFrame em CSV
    csv = df.to_csv().encode('utf-8')

    #coloca no Bucket
    result = minio_client.put_object(
    helper.BUCKET_NAME,
    object_name,
    data=BytesIO(csv),
    length=len(csv),
    content_type='application/csv'
)
    print(
        "Created object: {0}; etag: {1}".format(
            result.object_name, result.etag
        )
    )