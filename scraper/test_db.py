import psycopg, os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(os.getenv("DATABASE_URL"))
print("OK CONNECTED")
conn.close()