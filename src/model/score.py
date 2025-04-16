import pydantic
import datetime as dt


class ScoreSummary(pydantic.BaseModel):
    """
    Summary of a score
    """
    created: dt.datetime
    period: dt.date
    score: float

