import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class PageProtocol(Protocol):
    """
    Base browser page protocol.
    """

    browser: object

    # navigation and lifecycle
    async def goto_blank(self) -> None: ...
    async def goto_url(self, url: str) -> None: ...
    async def close(self) -> None: ...
    # accessors
    async def get_content(self) -> str: ...
    async def get_url(self) -> str: ...
    # scrolling
    async def scroll_top(self) -> None: ...
    async def scroll_bottom(self) -> None: ...
    async def scroll_page_up(self, num: int = 1) -> None: ...
    async def scroll_page_down(self, num: int = 1) -> None: ...
    # conditions and delays
    async def expect_url(
        self,
        pattern: str | re.Pattern[str],
        retry_delay: int | float = 100,
    ) -> None: ...
    async def sleep(self, timeout: int | float) -> None: ...


@runtime_checkable
class BrowserProtocol(Protocol):
    """
    Base browser protocol.
    """

    page: PageProtocol | None
    pages: list[PageProtocol]

    async def open_page(self) -> PageProtocol: ...
    async def close_page(self, page: int | PageProtocol) -> None: ...
    def page_index(self, page: PageProtocol) -> int | None: ...


@dataclass
class BasePageModel:
    """
    Base page model.
    """

    page: PageProtocol


@runtime_checkable
class LocatorProtocol(Protocol):
    """
    Base locator protocol.
    """

    page: PageProtocol

    async def click(self) -> None: ...
    async def scroll_into_view(self) -> None: ...


class BasePageElement(ABC):
    """
    Base page markup element.
    """

    @abstractmethod
    def __get__(self, obj: BasePageModel, cls: type | None = None) -> LocatorProtocol:
        raise NotImplementedError
