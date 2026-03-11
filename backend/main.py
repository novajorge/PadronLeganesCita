from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import os

from database import init_db, get_db, Usuario
from scheduler import iniciar_scheduler, detener_scheduler

app = FastAPI(title="Cita Previa Padrón Leganés API")

# Montar archivos estáticos del frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic
class UsuarioCreate(BaseModel):
    nombre: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    notify_email: bool = True
    notify_telegram: bool = True
    notify_whatsapp: bool = False


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    notify_email: bool = True
    notify_telegram: bool = True
    notify_whatsapp: bool = False
    activo: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


# Endpoints
@app.on_event("startup")
def startup_event():
    init_db()
    iniciar_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    detener_scheduler()


@app.get("/")
def root():
    """Sirve la landing page"""
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "mensaje": "API Cita Previa Padrón Leganés",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/usuarios", response_model=UsuarioResponse)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario"""
    db_usuario = Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        telefono=usuario.telefono,
        telegram_chat_id=usuario.telegram_chat_id,
        notify_email=usuario.notify_email,
        notify_telegram=usuario.notify_telegram,
        notify_whatsapp=usuario.notify_whatsapp,
        activo=True
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@app.get("/api/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos los usuarios"""
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios


@app.get("/api/usuarios/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario por ID"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@app.put("/api/usuarios/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(usuario_id: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """Actualiza un usuario"""
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_usuario.nombre = usuario.nombre
    db_usuario.email = usuario.email
    db_usuario.telefono = usuario.telefono
    db_usuario.telegram_chat_id = usuario.telegram_chat_id
    db_usuario.notify_email = usuario.notify_email
    db_usuario.notify_telegram = usuario.notify_telegram
    db_usuario.notify_whatsapp = usuario.notify_whatsapp
    db_usuario.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@app.delete("/api/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Elimina (desactiva) un usuario"""
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_usuario.activo = False
    db.commit()

    return {"mensaje": "Usuario desactivado", "id": usuario_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
