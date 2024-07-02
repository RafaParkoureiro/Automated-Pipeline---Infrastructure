from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import pandas as pd
import helper
from helper import minio_connection
import mlflow
import datetime
from datetime import datetime, timezone
from mlflow.models import infer_signature

#Configuração ao tracking URI do MLflow
mlflow.set_tracking_uri("http://host.docker.internal:5000") 

#Criar experiment
if not mlflow.get_experiment_by_name("iris"):
  mlflow.create_experiment("iris")
mlflow.set_experiment(experiment_name="iris")


def train_model(data_interval_end):
    minio_client = minio_connection()   #criar instancia do minio	
    found = minio_client.bucket_exists(helper.BUCKET_NAME)  #verificar se o bucket existe

    if not found:
        minio_client.make_bucket(helper.BUCKET_NAME)  #criar bucket caso não exista      
    else:
        print(f"Bucket '{helper.BUCKET_NAME}' found sucessfully!")

    #obter os dados de treino do bucket
    data = minio_client.get_object(helper.BUCKET_NAME, f"iris/{data_interval_end.to_date_string()}/train/train_data.csv") 

    #import do dataset para o pandas
    df = pd.read_csv(data, na_values=['NA'], encoding='utf-8')  
    print(df)
    mlflow.autolog()   #ativar o autologging do mlflow 
    with mlflow.start_run(
    run_name=(f"iris_{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')}")
    ) :
        # creating a simple KNN classifier
        test_size = 0.3
        X = df.loc[:,helper.Numerical_columns]  #defining the X columns
        print("X treino",X)
        Y = df[helper.target_column]    #target column
        print("Y treino",Y)
        # create train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state = 99360)
        knn = KNeighborsClassifier(n_neighbors=3)   #criar o classificador KNN
        knn.fit(X_train, y_train)   

        # Prever os rótulos das amostras de teste
        y_pred = knn.predict(X_test)
        #verificar os dados
        signature = infer_signature(X_test, y_pred)

        # Logging do modelo no MLflow
        mlflow.sklearn.log_model(      
        sk_model=knn,
        artifact_path="sklearn-model",
        signature=signature,
        registered_model_name="knn-iris",
        )

        # Calcular a accuracy do modelo
        accuracy = accuracy_score(y_test, y_pred)
        print("Acurácia do KNN no conjunto de teste:", accuracy)
