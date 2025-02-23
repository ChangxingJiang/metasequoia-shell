"""
Shell 抽象语法树中的单词层级节点
"""

import dataclasses
from typing import List

from metasequoia_shell.ast.enum_type import GroupingType
from metasequoia_shell.ast.node_base import ASTElement
from metasequoia_shell.ast.node_base import ASTScript
from metasequoia_shell.ast.node_base import ASTWord
from metasequoia_shell.simu_env import SimuVariable
from metasequoia_shell.simu_env import SimuVariableArray
from metasequoia_shell.simu_env import SimuVariableString
from metasequoia_shell.simu_env.system import SimuProcess

__all__ = [
    "NormalWord",  # Shell 抽象语法树中的普通单词
    "ArithmeticExpression",  # Shell 抽象语法树的算术表达式
    "ConditionalExpression",  # Shell 抽象语法树的条件表达式
    "GroupingCommand",  # Shell 抽象语法树的命令组
    "Assignment",  # Shell 抽象语法树的赋值语句
    "AssignmentArray",  # Shell 抽象语法树的赋值数组语句
]


@dataclasses.dataclass(slots=True)
class NormalWord(ASTWord):
    """Shell 抽象语法树中的普通单词"""

    element_list: List[ASTElement] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return "".join(element.source() for element in self.element_list)

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        element_var_list = [element.execute(process) for element in self.element_list]  # TODO 待实现大括号扩展
        if any(element_var.is_unknown for element_var in element_var_list):
            return SimuVariable.unknown()
        element_str = "".join(element_var.as_string() for element_var in element_var_list)
        return SimuVariableString.create(element_str)


@dataclasses.dataclass(slots=True)
class ArithmeticExpression(ASTWord):
    """Shell 抽象语法树的算术表达式"""

    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"(( {self.script.source()} ))"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return self.script.execute_as_arithmetic(process)


@dataclasses.dataclass(slots=True)
class ConditionalExpression(ASTWord):
    """Shell 抽象语法树的条件表达式"""

    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"[[ {self.script.source()} ]]"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return self.script.execute_as_condition(process)


@dataclasses.dataclass(slots=True)
class GroupingCommand(ASTWord):
    """Shell 抽象语法树的命令组"""

    type: GroupingType = dataclasses.field(kw_only=True)  # 命令组类型
    script: ASTScript = dataclasses.field(kw_only=True)  # 命令列表

    @staticmethod
    def create_sub_process(script: ASTScript):
        return GroupingCommand(type=GroupingType.SUB_PROCESS, script=script)

    @staticmethod
    def create_context(script: ASTScript):
        return GroupingCommand(type=GroupingType.CONTEXT, script=script)

    def source(self) -> str:
        if self.type == GroupingType.SUB_PROCESS:
            return f"( {self.script.source()} )"
        elif self.type == GroupingType.CONTEXT:
            return f"{{ {self.script.source()} }}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return self.script.execute(process)


@dataclasses.dataclass(slots=True)
class Assignment(ASTWord):
    """Shell 抽象语法树的赋值语句"""

    name: str = dataclasses.field(kw_only=True)  # TODO 待考虑 ASTElement 更优还是 str 更优
    value_element_list: List[ASTElement] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        value_str = "".join(elem.source() for elem in self.value_element_list)
        return f"{self.name}={value_str}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        value_element_var_list = [element.execute(process) for element in self.value_element_list]
        if any([element_var.is_unknown for element_var in value_element_var_list]):
            return SimuVariable.empty()  # 无法推断变量值
        value_str = "".join(element_var.as_string() for element_var in value_element_var_list)
        process.set_param(self.name, SimuVariableString.create(value_str))
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class AssignmentArray(ASTWord):
    """Shell 抽象语法树的赋值语句，赋值数据"""

    name: ASTElement = dataclasses.field(kw_only=True)  # TODO 待考虑 ASTElement 更优还是 str 更优
    value_element_list: List[ASTWord] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        word_list_str = " ".join(word.source() for word in self.value_element_list)
        return f"{self.name}=({word_list_str})"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        name_str = self.name.execute(process).as_string()
        if name_str is None:
            return SimuVariable.empty()  # 无法推断变量名
        value_element_var_list = [element.execute(process) for element in self.value_element_list]
        if any([element_var.is_unknown for element_var in value_element_var_list]):
            return SimuVariable.empty()  # 无法推断变量值
        value_element_str_list = [element_var.as_string() for element_var in value_element_var_list]
        process.set_param(name_str, SimuVariableArray.create(value_element_str_list))
        return SimuVariable.empty()
