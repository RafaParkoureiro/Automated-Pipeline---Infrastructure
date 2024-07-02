from trainmodel import train_model
from export_training_data_from_postgres import connect_and_read
from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from predict import predict_results
from add_predictions_to_postgres import dump_to_postgres
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from jinja2 import Template
import os


#definir varáveis globais
POSTGRES_CONN_ID = "postgres_default"
MY_POSTGRES_SCHEMA = "iris"
MY_GX_DATA_CONTEXT = "predictions"


with DAG("superdag",start_date = datetime(2024,1,1),schedule_interval="@daily", catchup=False) as dag:
    
    start = DummyOperator(task_id="start")  #Primeira Task, não faz nada

    #exportar os dados de treino do postgres
    export_training_data = PythonOperator(
        task_id = "export_training_data_from_postgres",
        python_callable = connect_and_read,
        op_args=["train"])
    
    #Usa o operador GreatExpectations para validar os dados de treino
    gx_validate_pg_train_data = GreatExpectationsOperator(
        task_id="test_training_data",
        conn_id=POSTGRES_CONN_ID,
        schema=MY_POSTGRES_SCHEMA,
        expectation_suite_name="test_suite_training_data",
        return_json_dict=True,
        query_to_validate=Template(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_training_test_data.sql')).read()).render(flag="train") ,
        data_context_root_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),"great_expectations"),
        data_asset_name="data",
    )

    #Treina o modelo e guarda-o no MLflow
    training = PythonOperator(
        task_id = "train_model",
        python_callable = train_model,
    )

    #Exportar os dados de treino do postgres
    export_prediction_data = PythonOperator(
        task_id = "export_prediction_data_from_postgres",
        python_callable = connect_and_read,
        op_args=["test"])
    
    #Usa o operador GreatExpectations para validar os dados de teste
    gx_validate_pg_prediction_data = GreatExpectationsOperator(
        task_id="test_prediction_data",
        conn_id=POSTGRES_CONN_ID,
        schema=MY_POSTGRES_SCHEMA,
        expectation_suite_name="test_suite_prediction_data",
        return_json_dict=True,
        query_to_validate=Template(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_training_test_data.sql')).read()).render(flag="test") ,
        data_context_root_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),"great_expectations"),
        data_asset_name="data",
    )

    #fazer as predictions e guardar no Bucket
    predictions = PythonOperator(
        task_id = "predict_results",
        python_callable = predict_results,
    )

    #adicionar as previsões ao postgres
    add_to_postgres = PythonOperator(
        task_id = "add_predictions_to_postgres",
        python_callable = dump_to_postgres,
    )

    #Usa o operador GreatExpectations para validar os dados de Prediction
    gx_validate_pg_predicted_data = GreatExpectationsOperator(
        task_id="test_predicted_data",
        conn_id=POSTGRES_CONN_ID,
        schema=MY_POSTGRES_SCHEMA,
        expectation_suite_name="test_suite_predicted_data",
        return_json_dict=True,
        query_to_validate=Template(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_predicted_data.sql')).read()).render(date="{{ data_interval_end }}"),
        data_context_root_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),"great_expectations"),
        data_asset_name="predictions",
    )

    end = DummyOperator(task_id="end")  # última task, não faz nada

    start >> gx_validate_pg_train_data >> export_training_data >> training >> gx_validate_pg_prediction_data >> export_prediction_data  >> predictions >> add_to_postgres >> gx_validate_pg_predicted_data >> end
