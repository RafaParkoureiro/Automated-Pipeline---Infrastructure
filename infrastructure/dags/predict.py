from sklearn.metrics import accuracy_score
import pandas as pd
import helper
from helper import minio_connection
from io import BytesIO
import pickle
import mlflow

# Configura o URI do MLFLOW
mlflow.set_tracking_uri("http://host.docker.internal:5000")


def get_model_versions(reg_model_name: str) -> list:
    """
    Returns a list with model versions. Each model allow to access model run_id, version, etc.
    Params:
        reg_model_name: the model name
    Returns:
        list: list with model versions sorted by date
    """

    client = mlflow.MlflowClient()
    model_versions = client.search_model_versions(
        f"name='{reg_model_name}'",
        order_by=["creation_timestamp DESC", "last_updated_timestamp DESC"],
    )
    return model_versions

def get_latest_model_uri(reg_model_name: str) -> str:
    """Returns the model uri latest version of the model from the mlflow model registry.

    Params:
        reg_model_name: the model name

    Returns:
        model_uri

    Example:
        >>> reg_model_name = get_registered_model_name()
        >>> model_uri = get_latest_model_uri(reg_model_name)
        >>> pipe = mlflow.sklearn.load_model(model_uri)
    """

    model_versions = get_model_versions(reg_model_name)

    return f"models:/{reg_model_name}/{model_versions[0].version}"


def predict_results(data_interval_end):

    minio_client = minio_connection()   #criar instancia do minio	
    found = minio_client.bucket_exists(helper.BUCKET_NAME)  #verificar se o bucket existe

    if not found:
        minio_client.make_bucket(helper.BUCKET_NAME)  #criar bucket caso não exista      
    else:
        print(f"Bucket '{helper.BUCKET_NAME}' found sucessfully!")

    #obter os dados de teste do bucket
    data = minio_client.get_object(helper.BUCKET_NAME, f"iris/{data_interval_end.to_date_string()}/test/test_data.csv")
    df = pd.read_csv(data, na_values=['NA'], encoding='utf-8')
    print(df)

    # Load the model from the MLflow model registry
    mlflow_model_uri = get_latest_model_uri("knn-iris")
    knn_model = mlflow.sklearn.load_model(mlflow_model_uri)
    print(knn_model)

    X = df.loc[:,helper.Numerical_columns]  
    Y = df[helper.target_column]    

    y_pred = knn_model.predict(X)   #obter previsões do modelo
    print("predictions:",y_pred)

    accuracy = accuracy_score(Y, y_pred) #calcular accuracy
    print("Accuracy on the new dataset:", accuracy)

    #mudanças ao dataset -> adicionar uma coluna com as previsões, outra com a data de execução e retirar a classe,a flag e o índice
    df['predicted_label'] = y_pred
    df['execution_date'] = data_interval_end
    df.drop(columns=['flag'], inplace=True)
    df.drop(columns=['class'], inplace=True)
    df.drop(df.columns[0], axis=1, inplace=True)

    print("Novo df com as predicoes",df)

    csv = df.to_csv(index=False).encode('utf-8')    #converter o dataframe para csv
    object_name = f"iris/{data_interval_end.to_date_string()}/prediction/predictions.csv"   #definir nome do objeto a ser guardado

    #remove se houver algo nesse path
    a = minio_client.remove_object(helper.BUCKET_NAME, object_name)

    #adicionar as predictions ao Bucket
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


