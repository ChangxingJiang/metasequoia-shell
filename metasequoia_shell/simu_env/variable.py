"""
Shell 模拟执行器中的变量对象

包含如下 3 种类型：
- 字符串（其他非数组类型均归入字符串类型）
- 字符串的数组
- 未知
"""

import abc
import dataclasses
from typing import List, Optional

__all__ = [
    "SimuVariable",
    "SimuVariableInteger",
    "SimuVariableString",
    "SimuVariableEmpty",
    "SimuVariableArray",
    "SimuVariableUnknown"
]


@dataclasses.dataclass(slots=True)
class SimuVariable(abc.ABC):
    """模拟执行变量"""

    @property
    @abc.abstractmethod
    def is_unknown(self) -> bool:
        """如果当前变量值未知则返回 True，否则返回 False"""

    @abc.abstractmethod
    def as_integer(self) -> Optional[int]:
        """将变量作为整数返回"""

    @abc.abstractmethod
    def as_string(self) -> Optional[str]:
        """将变量作为字符串返回"""

    @abc.abstractmethod
    def as_array(self) -> Optional[List[str]]:
        """将变量作为字符串的数组返回"""

    @staticmethod
    def unknown() -> "SimuVariable":
        return SimuVariableUnknown()

    @staticmethod
    def empty() -> "SimuVariable":
        return SimuVariableEmpty()


@dataclasses.dataclass(slots=True)
class SimuVariableInteger(SimuVariable):
    """模拟执行的整数变量"""

    value: int = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: int) -> "SimuVariableInteger":
        return SimuVariableInteger(value=value)

    @property
    def is_unknown(self) -> bool:
        return False

    def as_integer(self) -> Optional[int]:
        return self.value

    def as_string(self) -> Optional[str]:
        return str(self.value)

    def as_array(self) -> List[str]:
        return [str(self.value)]


@dataclasses.dataclass(slots=True)
class SimuVariableString(SimuVariable):
    """模拟执行的字符串变量"""

    value: str = dataclasses.field(kw_only=True)
    _is_unknown: bool = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value: str, is_unknown: bool = False) -> "SimuVariableString":
        return SimuVariableString(value=value, _is_unknown=is_unknown)

    @staticmethod
    def create_by_array(value_list: List[str], sep: str) -> "SimuVariableString":
        final_value_list = []
        contains_unknown = False
        for value in value_list:
            if value is None:
                final_value_list.append("")
                contains_unknown = True
            else:
                final_value_list.append(value)
        return SimuVariableString(
            value=sep.join(final_value_list),
            _is_unknown=contains_unknown
        )

    @property
    def is_unknown(self) -> bool:
        return self._is_unknown

    def as_integer(self) -> Optional[int]:
        return None

    def as_string(self) -> Optional[str]:
        return self.value

    def as_array(self) -> Optional[List[str]]:
        """

        【逻辑来源】
        > for x in 'abc'; do echo "$x"; done
        abc
        """
        return [self.value]


@dataclasses.dataclass(slots=True)
class SimuVariableEmpty(SimuVariable):
    """模拟执行的空变量（例如找不到参数等的返回值）"""

    @property
    def is_unknown(self) -> bool:
        return False

    def as_integer(self) -> Optional[int]:
        return None

    def as_string(self) -> Optional[str]:
        return ""

    def as_array(self) -> Optional[List[str]]:
        return [""]


@dataclasses.dataclass(slots=True)
class SimuVariableArray(SimuVariable):
    """模拟执行的数组变量"""

    value_list: List[str] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(value_list: List[str]) -> "SimuVariableArray":
        return SimuVariableArray(value_list=value_list)

    @property
    def is_unknown(self) -> bool:
        return False

    def as_integer(self) -> Optional[int]:
        return None

    def as_string(self) -> Optional[str]:
        return " ".join(self.value_list)

    def as_array(self) -> Optional[List[str]]:
        return self.value_list


class SimuVariableUnknown(SimuVariable):
    """模拟执行的未知（无法推断）变量"""

    @property
    def is_unknown(self) -> bool:
        return True

    def as_integer(self) -> Optional[int]:
        return None

    def as_string(self) -> Optional[str]:
        return None

    def as_array(self) -> Optional[List[str]]:
        return None
