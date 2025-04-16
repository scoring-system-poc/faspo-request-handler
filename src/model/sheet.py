import pydantic


class _SheetInfo(pydantic.BaseModel):
    """
    Generic document sheet information
    """
    id: str
    name: str
    number: int


class Sheet(_SheetInfo):
    """
    Document sheet data
    """
    inner_type: str = pydantic.Field(default="sheet", alias="_type")
    subject_id: str
    doc_id: str
    items: list[list[float | int | bool | str | None]]


class SheetCell(pydantic.BaseModel):
    row_num: int
    col_num: int
    value: float | int | bool | str | None

