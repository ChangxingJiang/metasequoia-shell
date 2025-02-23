"""
Shell 抽象语法树中的抽象基类节点
"""

import abc
import dataclasses
from typing import Optional

from metasequoia_shell.simu_env import SimuVariable
from metasequoia_shell.simu_env.system import SimuProcess

__all__ = [
    "ASTBase",  # Shell 抽象语法树节点的抽象基类
    "ASTElement",  # Shell 的元素层级节点
    "ASTWord",  # Shell 的单词层级节点
    "ASTCommand",  # Shell 的命令层级节点
    "ASTScript",  # Shell 的脚本层级节点
]


@dataclasses.dataclass(slots=True)
class ASTBase(abc.ABC):
    """Shell 抽象语法树节点的抽象基类"""

    @abc.abstractmethod
    def source(self) -> str:
        """返回样例值"""

    @abc.abstractmethod
    def execute(self, process: SimuProcess,
                input_stream: Optional[str] = None,
                is_in_double_quote: bool = False) -> SimuVariable:
        """模拟执行，返回打印到日志中的值

        Parameters
        ----------
        process : SimuProcess
            模拟执行环境
        input_stream : Optional[str] = None
            输入流
        is_in_double_quote : bool, default = False
            是否在双引号字符串中
        """


class ASTElement(ASTBase, abc.ABC):
    """Shell 的元素层级节点"""


class ASTWord(ASTBase, abc.ABC):
    """Shell 的单词层级节点"""


class ASTCommand(ASTBase, abc.ABC):
    """Shell 的命令层级节点"""


class ASTScript(ASTBase, abc.ABC):
    """Shell 的脚本层级节点"""

    @abc.abstractmethod
    def execute_as_arithmetic(self, process: SimuProcess, is_in_double_quote: bool = False) -> SimuVariable:
        """将当前 Shell 脚本层级节点视作算术表达式执行"""

    @abc.abstractmethod
    def execute_as_condition(self, process: SimuProcess, is_in_double_quote: bool = False) -> SimuVariable:
        """将当前 Shell 脚本层级节点视作条件表达式执行"""
