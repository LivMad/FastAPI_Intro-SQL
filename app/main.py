from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select


class ItemTodo(SQLModel, table=True):  # Usuário não acessa porque não indica o id.
    id: int | None = Field(default=None, primary_key=True)
    titulo: str
    descricao: str
    concluido: bool = False


class ItemTodoEditar(
    BaseModel
):  # Acesso do usuário. É opcional as edições, por isso o None = None.
    titulo: str | None = None
    descricao: str | None = None
    concluido: bool | None = None


postgres_url = "postgresql://user:123@localhost:5432/postgres"

engine = create_engine(postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/tarefas/")
def lista_tarefas(tarefa: ItemTodo):
    with Session(engine) as session:
        session.add(tarefa)
        session.commit()
        session.refresh(tarefa)
        return tarefa


@app.get("/tarefas/")
def ver_tarefas():
    with Session(engine) as session:
        tarefas = session.exec(select(ItemTodo)).all()
        return tarefas


@app.get("/tarefas/{tarefa_id}")
async def tarefa_path(tarefa_id: int):
    with Session(engine) as session:
        tarefa = session.exec(select(ItemTodo).where(ItemTodo.id == tarefa_id)).first()
        if tarefa is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="id não encontrado")
        return tarefa


@app.patch("/tarefas/{tarefa_id}")
def editar_tarefas(tarefa_id: int, tarefa_editada: ItemTodoEditar):
    with Session(engine) as session:
        tarefa = session.exec(select(ItemTodo).where(ItemTodo.id == tarefa_id)).first()

        if tarefa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item com id={tarefa_id} não encontrado!",
            )

        if tarefa_editada.titulo is not None:
            tarefa.titulo = tarefa_editada.titulo

        if tarefa_editada.descricao is not None:
            tarefa.descricao = tarefa_editada.descricao

        if tarefa_editada.concluido is not None:
            tarefa.concluido = tarefa_editada.concluido

        session.add(tarefa)
        session.commit()
        session.refresh(tarefa)
        return tarefa


@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int):
    with Session(engine) as session:
        tarefa = session.exec(select(ItemTodo).where(ItemTodo.id == tarefa_id)).first()
        if tarefa is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item com id={tarefa_id} não encontrado!",
            )
        session.delete(tarefa)
        session.commit()
