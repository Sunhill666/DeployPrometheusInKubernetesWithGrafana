from typing import Generic, TypeVar

from fastapi import Query
from fastapi_pagination.default import Page as BasePage, Params as BaseParams

T = TypeVar("T")
C = TypeVar("C")


class Params(BaseParams):
    size: int = Query(20, ge=1, le=100, description="Page size")


class Page(BasePage[T], Generic[T]):
    __params_type__ = Params
