import psycopg2

conn = psycopg2.connect(dbname="best_hack_2020_finals",
                        user = "postgres",
                        password = '@',
                        host = "localhost",
                        port = '5432')

curs = conn.cursor()
