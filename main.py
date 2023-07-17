## an alert system to send a message to the user about 
## all long running queries in the snowflake database 

import snowflake.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Snowflake connection parameters
snowflake_user = '<your_snowflake_username>'
snowflake_password = '<your_snowflake_password>'
snowflake_account = '<your_snowflake_account>'
snowflake_warehouse = '<your_snowflake_warehouse>'
snowflake_database = '<your_snowflake_database>'
snowflake_schema = '<your_snowflake_schema>'

# Email parameters
email_from = '<sender_email_address>'
email_to = '<recipient_email_address>'
smtp_server = '<your_smtp_server>'
smtp_port = '<your_smtp_port>'
smtp_username = '<your_smtp_username>'
smtp_password = '<your_smtp_password>'

# Function to send an email
def send_email(subject, body):
    message = MIMEMultipart()
    message['From'] = email_from
    message['To'] = email_to
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(email_from, email_to, message.as_string())

# Function to identify long-running queries
def identify_long_running_queries():
    query = f'''
        SELECT query_id, user_name, database_name, schema_name, query_text, start_time, end_time
        FROM table(information_schema.query_history_by_user(
            DATEADD(HOUR, -1, CURRENT_TIMESTAMP()), CURRENT_TIMESTAMP()))
        WHERE datediff('second', start_time, end_time) > 300 -- Long-running queries exceeding 5 minutes
        ORDER BY start_time DESC;
    '''

    # Establish connection to Snowflake
    conn = snowflake.connector.connect(
        user=snowflake_user,
        password=snowflake_password,
        account=snowflake_account,
        warehouse=snowflake_warehouse,
        database=snowflake_database,
        schema=snowflake_schema
    )

    # Execute the query
    cursor = conn.cursor()
    cursor.execute(query)

    # Retrieve the query results
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    # Prepare email content
    subject = 'Long-Running Queries Alert'
    body = 'The following queries have been running for a long time:\n\n'
    for row in results:
        body += f'Query ID: {row[0]}\n'
        body += f'User: {row[1]}\n'
        body += f'Database: {row[2]}\n'
        body += f'Schema: {row[3]}\n'
        body += f'Query Text: {row[4]}\n'
        body += f'Start Time: {row[5]}\n'
        body += f'End Time: {row[6]}\n\n'

    # Send the email
    send_email(subject, body)

# Call the procedure periodically
identify_long_running_queries()
