import requests
import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

TOP_1M_DOMAINS = 'https://storage.yandexcloud.net/kc-startda/top-1m.csv'
TOP_1M_DOMAINS_FILE = 'top-1m.csv'


def get_data():
    top_doms = pd.read_csv(TOP_1M_DOMAINS)
    top_data = top_doms.to_csv(index=False)

    with open(TOP_1M_DOMAINS_FILE, 'w') as f:
        f.write(top_data)


def top_10_zone():
    top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    top_data_df['zone'] = top_data_df.domain.str.rpartition('.')[2]
    top_10_zone=top_data_df.groupby('zone', as_index=False).agg({'domain':'count'}).sort_values('domain', ascending = False).head(10)
    with open('top_10_zone.csv', 'w') as f:
        f.write(top_10_zone.to_csv(index=False, header=False))


def len_name():
    top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    len_name=top_data_df.loc[df.domain.str.len() == df.domain.str.len().max()]
    with open('len_name.csv', 'w') as f:
        f.write(len_name.to_csv(index=False, header=False))

def airflow_dom():
    top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE, names=['rank', 'domain'])
    airflow_dom=top_data_df.query('domain =="airflow.com"')
    with open('airflow_dom.csv', 'w') as f:
        f.write(airflow_dom.to_csv(index=False, header=False))

def print_data(ds):
    with open('top_10_zone.csv', 'r') as f:
        top_zone = f.read()
    with open('len_name.csv', 'r') as f:
        longest_name = f.read()
    with open('airflow_dom.csv', 'r') as f:
        rank_airflow_dom = f.read()
    date = ds

    print(f'Top 10 domain zones for date {date}')
    print(top_zone)

    print(f'Domain with the longest name for date {date}')
    print(longest_name)
    
    print(f'Rank for airflow.com domain for date {date}')
    print(rank_airflow_dom)


default_args = {
    'owner': 'm.botalova',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 8, 5),
}
schedule_interval = '0 12 * * *'

dag = DAG('top_domain', default_args=default_args, schedule_interval=schedule_interval)

t1 = PythonOperator(task_id='get_data',
                    python_callable=get_data,
                    dag=dag)

t2 = PythonOperator(task_id='top_10_zone',
                    python_callable=top_10_zone,
                    dag=dag)

t3 = PythonOperator(task_id='len_name',
                        python_callable=len_name,
                        dag=dag)

t4 = PythonOperator(task_id='airflow_dom',
                        python_callable=airflow_dom,
                        dag=dag)

t5 = PythonOperator(task_id='print_data',
                    python_callable=print_data,
                    dag=dag)

t1 >> [t2, t3, t4] >> t5