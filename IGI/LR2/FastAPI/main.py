from fastapi import FastAPI
import redis
import psycopg2
import os

app = FastAPI()

# Инициализация клиентов (в реальном проекте используйте async драйверы: motor, aioredis)
cache = redis.Redis(host='cache', port=6379)
DB_URL = "dbname='app_db' user='user' password='password' host='db'"

@app.get("/")
def read_root():
    # Проверка Redis
    cache.incr("hits")
    hits = cache.get("hits")
    
    # Проверка Postgres
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    cur.close()
    conn.close()

    return {
        "status": "online",
        "redis_hits": hits,
        "postgres_version": db_version
    }
