from pydantic import BaseModel, ConfigDict


class Out(BaseModel):
    """Output class to be inherited by output to add some generic functions"""

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def json_(cls, obj):
        """Validate and dump the obj"""
        return cls.model_validate(obj).model_dump()
