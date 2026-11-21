from flask import Blueprint
from flask_login import current_user
from pydantic import BaseModel, Field

from bkyz.api.schemas import Out
from bkyz.data.label import Label
from bkyz.extensions import spec

labels = Blueprint("labels", __name__)


class LabelIn(BaseModel):
    name: str = Field(examples=["Computer Science"])


class LabelOut(Out):
    id: int
    name: str


@labels.get("")
def list_labels():
    return [LabelOut.json_(lbl) for lbl in Label.get_all_owned(current_user.id)]


@labels.post("")
@spec.validate(json=LabelIn)
def create_label(json: LabelIn):
    lbl = Label.create(
        name=json.name,
        user_id=current_user.id,
    )
    return LabelOut.json_(lbl)
