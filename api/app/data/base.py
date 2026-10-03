import logging
from typing import TYPE_CHECKING, Any, Self

from sqlalchemy import (
    ColumnExpressionArgument,
    select,
)
from sqlalchemy.exc import IntegrityError

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
