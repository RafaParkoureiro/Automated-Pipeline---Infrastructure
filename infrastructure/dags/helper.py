from minio import Minio

#definir credenciais de acesso
MINIO_ACCESS_KEY = "zaai_infrastructure"
MINIO_SECRET_KEY = "zaai_infrastructure"
MINIO_IP = "host.docker.internal:9000"
BUCKET_NAME = "zaai"

#defenicao das colunas numéricas do dataset iris e da target column
Numerical_columns = ['sepal_length_cm', 'sepal_width_cm', 'petal_length_cm', 'petal_width_cm']
target_column = ['class']

#retorna o client do minio
def minio_connection():
    try:
        client = Minio(MINIO_IP, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)
    except Exception as e:
        print(f"Error connecting to MinIO: {e}")
        return
    return client