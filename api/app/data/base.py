import logging
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any, Self

from sqlalchemy import (
    ColumnExpressionArgument,
    func,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped

from app import db
from app.errors import NotFoundError, ResourceExistsError

logger = logging.getLogger(__name__)


class CRUDMixin:
    """Generic CRUD methods mix-in.

    Wrappers around plain database calls, to keep database out of view layer.
    """

    if TYPE_CHECKING:

        def __init__(self, **kwargs: Any) -> None: ...

    @classmethod
    def get_one(cls, *criteria: ColumnExpressionArgument) -> Self:
        """Query for one object based on criteria.

        Raises:
            NotFoundError if there is none found.
        """
        obj = db.session.scalar(
            select(cls).
            where(*criteria)
        )  # fmt: skip
        if obj is None:
            raise NotFoundError(cls.__name__)
        return obj

    @classmethod
    def get_all(cls, *criteria: ColumnExpressionArgument) -> list[Self]:
        return list(db.session.scalars(
            select(cls).
            where(*criteria)
        ))  # fmt: skip

    @classmethod
    def get_by_id(cls, id: int) -> Self:
        """Lookup an obj by it's PK id.

        Raises:
            NotFoundError if the id isn't found.
        """
        if (obj := db.session.get(cls, id)) is None:
            raise NotFoundError("id", id)
        return obj

    @classmethod
    def delete_by_id(cls, id: int) -> None:
        """Delete an obj by it's PK id.

        Raises:
            NotFoundError if the id isn't found (could already have been deleted.)
        """
        if (obj := cls.get_by_id(id)) is None:
            raise NotFoundError("id", id)
        obj.delete()

    @classmethod
    def create(cls, **kwargs) -> Self:
        try:
            return cls(**kwargs)._save()
        except IntegrityError as e:
            db.session.rollback()
            logger.warning(f"integrity error creating {cls.__name__}: {e.orig}")
            raise ResourceExistsError(cls.__name__)

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs) -> Self:
        for f, v in kwargs.items():
            setattr(self, f, v)
        return self._save()

    def _save(self) -> Self:
        db.session.add(self)
        db.session.commit()
        return self


class Direction(StrEnum):
    up = auto()
    down = auto()


class SortOrderMixin:
    """Gives a mode a sort_order that auto increments with in a scope (e.g., playlist)"""

    __sort_scope__: str
    sort_order: Mapped[int]

    @classmethod
    def next_sort_order(cls, scope_id: int) -> int:
        scope = getattr(cls, cls.__sort_scope__)
        return db.session.execute(
            select(func.coalesce(func.max(cls.sort_order), 0) + 1).where(scope == scope_id)
        ).scalar_one()

    @classmethod
    def create(cls, **kwargs) -> Self:
        kwargs["sort_order"] = cls.next_sort_order(kwargs[cls.__sort_scope__])
        return super().create(**kwargs)

    def move(self, direction: Direction):
        scope = getattr(type(self), self.__sort_scope__)
        scope_id = getattr(self, self.__sort_scope__)
        col = type(self).sort_order

        if direction is Direction.up:
            where, order = col < self.sort_order, col.desc()
        else:
            where, order = col > self.sort_order, col.asc()

        neighbour = db.session.scalar(
            select(type(self)).where(scope == scope_id, where).order_by(order).limit(1)
        )
        if neighbour is None:  # already at top
            return

        self.sort_order, neighbour.sort_order = neighbour.sort_order, self.sort_order
        db.session.commit()
