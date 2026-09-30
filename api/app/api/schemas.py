from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict


class Out(BaseModel):
    """Output class to be inherited by output to add some generic functions"""

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def json_(cls, obj):
        """Validate and dump the obj"""
        return cls.model_validate(obj).model_dump(mode="json")


class ViewQuery(BaseModel):
    view: Literal["basic", "full"] = "basic"
    """Response shape, 'full' embeds related resources."""



def utc_date_time_conv(v: datetime):
    if v.tzinfo:
        return v
    return v.replace(tzinfo=UTC)

UTCDatetime = Annotated[datetime, AfterValidator(utc_date_time_conv)]
