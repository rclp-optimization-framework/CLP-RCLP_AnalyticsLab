from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
import datetime
from config.db import Base


class Prueba(Base):
    __tablename__ = "prueba"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bateria_id = Column(Integer, ForeignKey("bateria.id"), nullable=False)
    num_buses = Column(Integer, nullable=False)
    num_stations = Column(Integer, nullable=False)
    max_stops = Column(Integer, nullable=False)
    num_stops = Column(JSON, nullable=False)
    st_bi = Column(JSON, nullable=False)
    d = Column(JSON, nullable=False)
    t = Column(JSON, nullable=False)
    tau_bi = Column(JSON, nullable=False)
    consumo_max = Column(Integer, nullable=False)
    consumo_min = Column(Integer, nullable=False)
    alpha = Column(Float, nullable=False)
    mu = Column(Float, nullable=False)
    sm = Column(Integer, nullable=False)
    psi = Column(Float, nullable=False)
    beta = Column(Float, nullable=False)
    m = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    bateria = relationship("Bateria", back_populates="pruebas")
    results = relationship("Result", back_populates="prueba", cascade="all, delete-orphan")


class Bateria(Base):
    __tablename__ = "bateria"
    __table_args__ = (UniqueConstraint("nombre", name="unique_bateria_nombre"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    pruebas = relationship("Prueba", back_populates="bateria", cascade="all, delete-orphan")


class Result(Base):
    __tablename__ = "result"
    __table_args__ = (
        UniqueConstraint('prueba_id', 'solver', name='unique_prueba_solver'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    prueba_id = Column(Integer, ForeignKey("prueba.id"), nullable=False)
    solver = Column(String, nullable=False)
    execution_time_seconds = Column(Float, nullable=False)
    charged_stations = Column(Integer, nullable=False)
    charging_locations = Column(JSON, nullable=False)
    time_deviation_minutes = Column(Float, nullable=False)
    bateria = Column(JSON, nullable=False)
    carga = Column(JSON, nullable=False)
    comment = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relaciones
    prueba = relationship("Prueba", back_populates="results")


# Backwards compatibility alias
Cache = Result
