from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Usar /app/data para persistencia en Docker/Coolify
DB_DIR = os.getenv("DB_DIR", "/app/data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR}/citas.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)
    whatsapp = Column(Boolean, default=False)
    notify_email = Column(Boolean, default=True)
    notify_telegram = Column(Boolean, default=True)
    notify_whatsapp = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)  # email, telegram, whatsapp
    mensaje = Column(String, nullable=False)
    enviada = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CitaDisponibilidad(Base):
    __tablename__ = "citas_disponibilidad"

    id = Column(Integer, primary_key=True, index=True)
    hay_citas = Column(Boolean, default=False)
    detalles = Column(String, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
