from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID

import lxml.etree
from uuid6 import uuid7
from yarl import URL

from .page import BasePageModel, PageProtocol
from .stvector import HtmlElement, HtmlVector


def utcnow(microsecond: bool = True) -> datetime:
    dtm = datetime.now(UTC)
    if not microsecond:
        dtm = dtm.replace(microsecond=0)
    return dtm


@dataclass
class BaseDataItem:
    iid: UUID = field(default_factory=uuid7)
    created_at: datetime = field(default_factory=utcnow)


@dataclass(kw_only=True)
class BaseHtmlItem(BaseDataItem):
    url: str  # this is needed to provide base_url when parsing html string
    html: str = field(repr=False)

    @classmethod
    def from_etree(cls, url: str, element: HtmlElement, **kwargs: Any) -> Self:
        html = lxml.etree.tostring(element).decode()
        return cls(url=url, html=html, **kwargs)

    @classmethod
    async def from_page(cls, page: PageProtocol | BasePageModel, **kwargs: Any) -> Self:
        if isinstance(page, BasePageModel):
            page = page.page
        return cls(url=await page.get_url(), html=await page.get_content(), **kwargs)

    def get_vector(self) -> HtmlVector[HtmlElement]:
        return HtmlVector.from_string(self.html, base_url=URL(self.url).with_path(''))
