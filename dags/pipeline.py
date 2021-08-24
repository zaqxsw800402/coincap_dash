from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow import DAG

from datetime import datetime, timezone, timedelta

from sqlalchemy import create_engine
import requests
import pandas as pd


def download():
    url = 'https://api.coincap.io/v2/assets'
    r = requests.get(url)
    data = r.json().get('data')
    coins = pd.DataFrame(data)
    coins.to_csv('coins.csv')
    # print(coins.head())


def load_data():
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    pg_engine = pg_hook.get_sqlalchemy_engine()

    coins = pd.read_csv('coins.csv')
    coins['dt'] = pd.to_datetime(datetime.now(tz=timezone(timedelta(hours=8))))
    coins.rename(columns={'rank': 'coinrank', 'priceUsd': 'priceusd'}, inplace=True)
    coins['priceusd'] = coins.priceusd.round(2)
    coins_sql = coins[['id', 'coinrank', 'symbol', 'name', 'priceusd', 'dt']]
    coins_sql.to_sql('coins', con=pg_engine, if_exists='append', index=False)


# def load_logs():
#     conn = PostgresHook(postgres_conn_id='postgres_default').get_conn()
#     cur = conn.cursor()
#     SQL_STATEMENT = """
#         COPY newbc (title, price, stock)
#         FROM STDIN WITH CSV HEADER
#         """
#
#     with open('/opt/webscrape/bookstoscrape/new.csv', 'r') as f:
#         cur.copy_expert(SQL_STATEMENT, f)
#         conn.commit()


# def loadtosql(df):
#     engine = create_engine('postgresql+psycopg2://airflow:airflow@127.0.0.1:5432/postgres')
#     df.to_sql('coins', con=engine, if_exists='append', index=False)


default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 3,
    "retry_exponential_backoff": True,  # 每次時間遞增
    "retry_delay": timedelta(minutes=1),
    'depend_on_past': False

}

with DAG("pipeline", start_date=datetime(2021, 7, 10), schedule_interval=timedelta(minutes=10),
         default_args=default_args, catchup=False) as dag:
    download_data = PythonOperator(
        task_id='download_data',
        python_callable=download,
        # op_kwargs={'filename':'coins.csv'}
    )

    load_data = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
        # op_kwargs={'filename':'coins.csv'}
    )

    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="postgres_default",
        sql=
        '''
    create table if not exists coins (
    id varchar,
    coinrank int, 
    symbol varchar,
    name varchar,
    priceUsd double precision,
    dt timestamp
    )
    ''')

    download_data >> create_table >> load_data
