from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator, ShortCircuitOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 6, 30),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('long_running_queries_alert', default_args=default_args, schedule_interval='@daily')

# Snowflake connection ID defined in Airflow
snowflake_conn_id = 'snowflake_connection'

# SQL query to retrieve long-running queries
long_running_queries_query = """
SELECT query_id, query_text, start_time, end_time, DATEDIFF('SECOND', start_time, end_time) AS duration
FROM table(information_schema.query_history())
WHERE DATEDIFF('SECOND', start_time, end_time) > 300
ORDER BY duration DESC
"""

# Task to retrieve long-running queries using SnowflakeOperator
get_long_running_queries_task = SnowflakeOperator(
    task_id='get_long_running_queries',
    sql=long_running_queries_query,
    snowflake_conn_id=snowflake_conn_id,
    dag=dag
)

# Task to check if there are any long-running queries
def has_long_running_queries(**kwargs):
    ti = kwargs['ti']
    query_results = ti.xcom_pull(task_ids='get_long_running_queries')
    return bool(query_results)

# Task to send email alert with the long-running queries
def send_email_alert(**kwargs):
    ti = kwargs['ti']
    query_results = ti.xcom_pull(task_ids='get_long_running_queries')
    if query_results:
        email_subject = "Long Running Queries Alert"
        email_body = "The following queries have been running for more than 5 minutes:\n\n"
        for row in query_results:
            query_id, query_text, start_time, end_time, duration = row
            email_body += f"Query ID: {query_id}, Duration: {duration} seconds\nQuery Text: {query_text}\n\n"

        # Send email
        recipients = Variable.get("email_recipients", default_var="")
        email_operator = EmailOperator(
            task_id='send_email_alert',
            to=recipients,
            subject=email_subject,
            html_content=email_body,
            dag=dag
        )
        email_operator.execute(context=kwargs)

# ShortCircuitOperator to check if there are any long-running queries
check_long_running_queries_task = ShortCircuitOperator(
    task_id='check_long_running_queries',
    python_callable=has_long_running_queries,
    provide_context=True,
    dag=dag
)

# Task to call the Python function to send email alert
send_email_alert_task = PythonOperator(
    task_id='send_email_alert_task',
    python_callable=send_email_alert,
    provide_context=True,
    dag=dag
)

# Define the task dependencies
get_long_running_queries_task >> check_long_running_queries_task >> send_email_alert_task
