import psycopg2

conn = psycopg2.connect(dbname="best_hack_2020_finals",
                        user = "postgres",
                        password = '2254321R1V3N@',
                        host = "localhost",
                        port = '5432')

curs = conn.cursor()
