from typing import Annotated
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi_zero.database import get_session
from fastapi_zero.models import User, Todo
from fastapi_zero.schemas import (
    TodoSchema,
    TodoPublic,
    FilterTodo,
    TodoList,
    Message,
    TodoUpdate,
)
from fastapi_zero.security import get_current_user

router = APIRouter(prefix='/todo', tags=['todo'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: Session,
):
    db_todo = Todo(
        user_id=user.id,
        title=todo.title,
        state=todo.state,
        description=todo.description,
    )
    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)
    return db_todo


@router.get('/', response_model=TodoList)
async def list_todos(
    user: CurrentUser,
    session: Session,
    todo_filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state == todo_filter.state)

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos': todos.all()}


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(
    todo_id: int,
    user: CurrentUser,
    session: Session,
):
    todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task deleted'}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int,
    user: CurrentUser,
    session: Session,
    todo: TodoUpdate,
):
    db_todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo
