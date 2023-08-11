# Long Running Queries Alert - Airflow DAG

This is an Airflow DAG that monitors long-running queries in a Snowflake database and sends an email alert if any queries have been running for more than 5 minutes.

## Prerequisites

- Airflow installed and configured.
- Snowflake connection configured in Airflow.
- Email recipients configured as an Airflow Variable.

## DAG Overview

The DAG performs the following steps:

1. Executes a Snowflake query to retrieve long-running queries (queries running for more than 5 minutes).
2. If there are any long-running queries, it sends an email alert with query details to the specified recipients.
3. If no long-running queries are found, it logs a message indicating no action is taken.

## DAG Configuration

- The DAG is scheduled to run daily.
- The `SnowflakeHook` is used to execute the query against the Snowflake database.
- The results of the query are processed, and if long-running queries are found, an email is sent using the `EmailOperator`.
- If no long-running queries are found, a `DummyOperator` is used as a placeholder.

## Configuration Steps

1. Configure the Snowflake connection in Airflow.
2. Set up email recipients as an Airflow Variable.
3. Copy the provided DAG script to your Airflow DAGs folder.
4. Adjust the DAG's default arguments, schedule interval, and other parameters as needed.
5. Run the DAG in your Airflow environment.

## Usage

1. The DAG will run daily at the scheduled interval.
2. If there are any long-running queries, an email will be sent to the specified recipients with query details.
3. If no long-running queries are found, a log message will indicate no action taken.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to customize and enhance this README file based on your project's specific details and requirements.
