from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.db import Base, engine
from model.dataStructure import Result, Bateria, Prueba
from routes.bateria import bateriaRouter
from routes.cache import cacheRouter
from routes.prueba import pruebaRouter
from routes.ejecucion import ejecucionRouter
from sqlalchemy import inspect, text


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)
        if "result" in inspector.get_table_names():
            result_columns = {column["name"] for column in inspector.get_columns("result")}
            if "comment" not in result_columns:
                with engine.begin() as connection:
                    connection.execute(text("ALTER TABLE result ADD COLUMN comment VARCHAR"))
    except Exception as e:
        print(f"Error al crear tablas: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Tablas creadas")
    yield

    print("Servidor apagándose, liberando recursos...")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bateriaRouter)
app.include_router(pruebaRouter)
app.include_router(cacheRouter)
app.include_router(ejecucionRouter)


@app.get("/ping")
def ping():
    return {"message": "Conectado correctamente"}

