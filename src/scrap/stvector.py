import re
from collections.abc import Iterable, Iterator
from datetime import date, datetime
from typing import TYPE_CHECKING, ParamSpec, TypeVar
from zoneinfo import ZoneInfo

from lxml.etree import ElementBase as ElementBase
from lxml.etree import _Element as Element
from lxml.etree import tostring
from lxml.html import HtmlElement as HtmlElement
from lxml.html import fromstring
from typing_extensions import Self

from .exception import ShapeError

if TYPE_CHECKING:
    import builtins  # noqa: F401  # used in type hint
    from collections.abc import Callable, Sequence  # noqa: F401  # used in type hint
    from typing import Concatenate  # noqa: F401  # used in type hint

    import yarl  # noqa: F401  # used in type hint

P = ParamSpec('P')
R = TypeVar('R', bound=object)
T = TypeVar('T', bound=object)

type Nested[T] = T | list[T] | list[Nested[T]]


class StVector[T]:
    """
    Data structure providing easy chaining interface to html parsing results.
    """

    def __init__(self, data: Nested[T], depth: int = 0) -> None:
        self.data: Nested[T] = data
        self.depth: int = depth

    @property
    def is_empty(self) -> bool:
        return self.data == []

    @property
    def is_scalar(self) -> bool:
        return self.depth == 0

    @classmethod
    def from_html(cls, content, base_url=None):  # type: (str | bytes, str | yarl.URL | None) -> StVector[HtmlElement]
        base_url = base_url if base_url is None else str(base_url)
        data = fromstring(content, base_url=base_url)  # type: ignore[arg-type]  # until lxml/lxml-stubs#107 is released
        return cls(data)  # type: ignore[arg-type]

    def copy(self) -> Self:
        return self.__class__(copy_upto_level(self.data, self.depth), depth=self.depth)

    def __iter__(self) -> Iterator[Self]:
        if self.depth == 0:
            raise ValueError('Unable to iterate scalar')
        for item in iter_at_level(self.data, self.depth):
            yield self.__class__(item, depth=self.depth - 1)

    def __bool__(self) -> bool:
        for _ in iter_at_level(self.data, self.depth):
            return True
        return False

    def __len__(self) -> int:
        return sum(1 for _ in iter_at_level(self.data, self.depth))

    def __getitem__(self, index: int) -> Self:
        if self.depth == 0:
            raise ValueError('Unable to access items of scalar')
        elif self.depth == 1:
            return self.__class__(self.data[index], depth=0)  # type: ignore[index]  # depth==1 means data is a list
        else:
            ret = self.copy()
            for parent in iter_at_level(ret.data, ret.depth - 2):
                if not isinstance(parent, list):
                    raise iterable_required(parent)
                parent[:] = (item[index] for item in parent.copy())  # type: ignore[index,misc]  # depth>=2 means item is a list
            ret.depth -= 1
            return ret

    def apply(self, func, *args, **kwargs):  # type: (Callable[Concatenate[Nested[T], P], Nested[R]], P.args, P.kwargs) -> StVector[R]
        """
        Apply arbitrary function to all items on bottom level.
        """
        if self.depth == 0:
            return self.__class__(func(self.data, *args, **kwargs))  # type: ignore[arg-type,return-value]
        ret = self.copy()
        for parent in iter_at_level(ret.data, ret.depth - 1):
            if not isinstance(parent, list):
                raise iterable_required(parent)
            parent[:] = (func(item, *args, **kwargs) for item in parent.copy())  # type: ignore[misc]
        return ret  # type: ignore[return-value]

    def flatten(self, level=1):  # type: (int) -> StVector[T]
        """
        Flatten all items below specified level; by default, flatten up to top level.
        """
        depth = level if level >= 0 else self.depth - level + 1
        if self.depth == 0:
            raise ValueError('Unable to flatten scalar')
        if depth == 0:
            raise ValueError('Unable to flatten to scalar')
        ret = self.copy()
        for parent in iter_at_level(ret.data, depth - 1):
            if not isinstance(parent, list):
                raise iterable_required(parent)
            parent[:] = iter_at_level(parent.copy(), ret.depth - depth + 1)  # type: ignore[assignment,misc]
        ret.depth = depth
        return ret

    def level(self, index: int | None = None, /, up: int = 0, down: int = 0) -> Self:
        """
        Change data level.
        """
        if index is None:
            new_depth = self.depth
        else:
            new_depth = index if index >= 0 else (self.depth - index)
        new_depth += down - up
        if new_depth < 0:
            raise ValueError('Unable to set negative depth')
        ret = self.__class__(self.data)
        ret.depth = new_depth
        return ret

    def scalar(self, nested: bool = True) -> T:
        """
        Return single scalar data value and raise exception otherwise.
        """
        return get_nested_scalar(self.data, recurse=nested)

    # transformations

    def all_(self):  # type: () -> StVector[bool]
        ret = self.level(up=1).apply(
            lambda x: all(x) if isinstance(x, Iterable) else bool(x)
        )
        return ret

    def any_(self):  # type: () -> StVector[bool]
        ret = self.level(up=1).apply(
            lambda x: any(x) if isinstance(x, Iterable) else bool(x)
        )
        return ret

    def attr(self, name):  # type: (str) -> StVector[str | None]
        def _attr(item: ElementBase) -> str | None:
            if not isinstance(item, ElementBase):
                raise TypeError(f'Required ElementBase instead of {type(item)}')
            return item.get(name)

        ret = self.apply(_attr)  # type: ignore[arg-type]
        return ret

    def css(self, expr):  # type: (str) -> StVector[Element]
        def _css(item: ElementBase) -> list[Element]:
            if not isinstance(item, ElementBase):
                raise TypeError(f'Required ElementBase instead of {type(item)}')
            return item.cssselect(expr)

        ret = self.apply(_css)  # type: ignore[arg-type]
        ret.depth += 1
        return ret

    def date(self, fmt):  # type: (str) -> StVector[date | None]
        def _date(item: str) -> date | None:
            if not isinstance(item, str):
                raise TypeError(f'Required str instead of {type(item)}')
            try:
                return datetime.strptime(item.strip(), fmt).date()
            except ValueError:
                return None

        ret = self.apply(_date)  # type: ignore[arg-type]
        return ret

    def datetime(self, fmt, tz=None):  # type: (str, str | ZoneInfo | None) -> StVector[datetime | None]
        def _datetime(item: str) -> datetime | None:
            if not isinstance(item, str):
                raise TypeError(f'Required str instead of {type(item)}')
            try:
                dt = datetime.strptime(item.strip(), fmt)
                if dt.tzinfo is None and tz is not None:
                    dt = dt.replace(tzinfo=ZoneInfo(tz) if isinstance(tz, str) else tz)
                return dt
            except ValueError:
                return None

        ret = self.apply(_datetime)  # type: ignore[arg-type]
        return ret

    def float(self):  # type: () -> StVector[float | None]
        def _float(item: str) -> float | None:
            if not isinstance(item, str):
                raise TypeError(f'Required str instead of {type(item)}')
            try:
                return float(item.strip())
            except ValueError:
                return None

        ret = self.apply(_float)  # type: ignore[arg-type]
        return ret

    def int(self):  # type: () -> StVector[int | None]
        def _int(item: str) -> int | None:
            if not isinstance(item, str):
                raise TypeError(f'Required str instead of {type(item)}')
            try:
                return int(item.strip())
            except BaseException:
                return None

        ret = self.apply(_int)  # type: ignore[arg-type]
        return ret

    def join(self, sep=' '):  # type: (str | Sequence[str]) -> StVector[str]
        def _join(item: list[str], sep: str) -> str:
            if not isinstance(item, list):
                raise TypeError(f'Required list instead of {type(item)}')
            return sep.join(item)

        separators = [sep] if isinstance(sep, str) else sep
        if self.depth == 0:
            raise ValueError('Unable to join scalar')
        elif len(sep) > self.depth + 1:
            raise ValueError('Data has not enough levels to be joined')
        ret = self
        for s in separators:
            ret = ret.level(up=1).apply(_join, s)  # type: ignore[arg-type]
        return ret  # type: ignore[return-value]

    def normspace(self):  # type: () -> StVector[str]
        def _normspace(item: str) -> str:
            if not isinstance(item, str):
                raise TypeError(f'Required str instead of {type(item)}')
            return re.sub(r'\s+', ' ', item).strip()

        ret = self.apply(_normspace)  # type: ignore[arg-type]
        return ret

    def replace(self, old, new, count=-1):  # type: (str, str, builtins.int) -> StVector[str]
        def _replace(item: str) -> str:
            if not isinstance(item, str):
                raise TypeError(f'Required str instead of {type(item)}')
            return item.replace(old, new, count)

        ret = self.apply(_replace)  # type: ignore[arg-type]
        return ret

    def split(self, sep=' '):  # type: (str | Sequence[str]) -> StVector[str]
        def _split(item: str, sep: str) -> list[str]:
            if not isinstance(item, str):
                raise TypeError(f'Required str instead of {type(item)}')
            return item.split(sep)

        separators = [sep] if isinstance(sep, str) else sep
        ret = self
        for s in separators:
            ret = ret.apply(_split, s).level(ret.depth + 1)  # type: ignore[arg-type,assignment]
        return ret  # type: ignore[return-value]

    def string(self):  # type: () -> StVector[str]
        def _str(item: object) -> str:
            if isinstance(item, ElementBase):
                return tostring(item).decode()
            else:
                return str(item)

        ret = self.apply(_str)
        return ret

    def strip(self, chars=None):  # type: (str | None) -> StVector[str]
        def _strip(item: str, chars: str | None) -> str:
            if not isinstance(item, str):
                raise TypeError(f'Required str or bytes instead of {type(item)}')
            return item.strip() if chars is None else item.strip(chars)

        ret = self.apply(_strip, chars)  # type: ignore[arg-type]
        return ret

    def text(self):  # type: () -> StVector[str]
        def _text(item: HtmlElement) -> str:
            if not isinstance(item, HtmlElement):
                raise TypeError(f'Required HtmlElement instead of {type(item)}')
            return str(item.text_content())

        ret = self.apply(_text)
        return ret

    def xpath(self, expr):  # type: (str) -> StVector[ElementBase] | StVector[bool] | StVector[builtins.float] | StVector[str]
        def _xpath(
            item: ElementBase,
        ) -> list[ElementBase] | list[bool] | list[float] | list[str]:
            if not isinstance(item, ElementBase):
                raise TypeError(f'Required ElementBase instead of {type(item)}')
            return item.xpath(expr)  # type: ignore[return-value]

        ret = self.apply(_xpath)  # type: ignore[arg-type,misc]
        ret.depth += 1
        return ret


# helpers


def iterable_required(item: object) -> TypeError:
    return TypeError(f'Unable to iterate object of type {type(item).__name__}')


def copy_upto_level(data: T, level: int) -> T:
    """
    Create deep copy of nested list up to specified level; objects below this level
    are copied as is.
    """
    if level < 0:
        raise ValueError(f'Invalid negative level {level}')
    elif level == 0:
        return data
    else:
        if not isinstance(data, list):
            raise iterable_required(data)
        return [copy_upto_level(item, level - 1) for item in data]  # type: ignore[return-value]


def iter_at_level(data: Nested[T], level: int) -> Iterable[Nested[T]]:
    """
    Iterate over items at specified level of the nested list.
    """
    if level < 0:
        raise ValueError(f'Invalid negative level {level}')
    elif level == 0:
        yield data
    else:
        if not isinstance(data, list):
            raise iterable_required(data)
        for item in data:
            yield from iter_at_level(item, level=level - 1)


def get_nested_scalar(data: Nested[T], recurse: bool = True) -> T:
    if not isinstance(data, list):
        return data
    elif len(data) == 1:
        if recurse:
            return get_nested_scalar(data[0])  # type: ignore[no-any-return]
        else:
            raise ShapeError('Not a scalar')
    else:
        raise ShapeError('Not a nested scalar')
