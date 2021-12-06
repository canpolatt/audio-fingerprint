import psycopg2

conn = psycopg2.connect(dbname="audiodb", user="postgres", password="1234", host="localhost")
cur = conn.cursor()
data=['ASDASDASD','CAN']
cur.execute('SELECT * FROM songs WHERE id=%s',[9])
x=cur.fetchone()
print(len(x))
conn.commit()

