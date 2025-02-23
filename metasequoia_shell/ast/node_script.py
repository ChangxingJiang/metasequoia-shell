"""
Shell 抽象语法树中的脚本层级节点
"""

import dataclasses
from typing import List

from metasequoia_shell.ast.node_base import ASTCommand
from metasequoia_shell.ast.node_base import ASTScript
from metasequoia_shell.simu_env import SimuVariable
from metasequoia_shell.simu_env.system import SimuProcess

__all__ = [
    "Script",  # Shell 抽象语法树的脚本节点
]


@dataclasses.dataclass(slots=True)
class Script(ASTScript):
    """Shell 抽象语法树的脚本节点"""

    command_list: List[ASTCommand] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return "\n".join(command.source() for command in self.command_list)

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        res = SimuVariable.empty()
        for command in self.command_list:
            res = command.execute(process)  # 不断更新最后一个命令的参数
        return res

    def execute_as_arithmetic(self, process: SimuProcess, is_in_double_quote: bool = False) -> SimuVariable:
        """将当前 Shell 脚本层级节点视作算术表达式执行"""
        # TODO 待实现算术表达式执行逻辑
        return SimuVariable.unknown()

    def execute_as_condition(self, process: SimuProcess, is_in_double_quote: bool = False) -> SimuVariable:
        """将当前 Shell 脚本层级节点视作条件表达式执行"""
        # TODO 待实现条件表达式执行逻辑
        return SimuVariable.unknown()
