import psycopg2

conn = psycopg2.connect(dbname="audiodb", user="postgres", password="1234", host="localhost")
cur = conn.cursor()

cur.execute('CREATE TABLE ')





