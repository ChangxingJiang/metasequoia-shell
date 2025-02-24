"""
Shell 抽象语法树中的命令层级节点
"""

import dataclasses
from typing import List, Optional

from metasequoia_shell.ast.enum_type import CommandEndType
from metasequoia_shell.ast.enum_type import CommandRelationType
from metasequoia_shell.ast.enum_type import PipeType
from metasequoia_shell.ast.enum_type import RedirectionType
from metasequoia_shell.ast.node_base import ASTBase
from metasequoia_shell.ast.node_base import ASTCommand
from metasequoia_shell.ast.node_base import ASTScript
from metasequoia_shell.ast.node_base import ASTWord
from metasequoia_shell.simu_env import SimuVariable
from metasequoia_shell.simu_env import SimuVariableString
from metasequoia_shell.simu_env.configuration import CaseItemRunMode
from metasequoia_shell.simu_env.configuration import CaseRunMode
from metasequoia_shell.simu_env.configuration import ConditionRunMode
from metasequoia_shell.simu_env.configuration import EnhanceForRunMode
from metasequoia_shell.simu_env.configuration import ForRunMode
from metasequoia_shell.simu_env.configuration import IfRunMode
from metasequoia_shell.simu_env.configuration import RelationRunMode
from metasequoia_shell.simu_env.system import SimuProcess

__all__ = [
    "SimpleCommand",  # Shell 抽象语法树的简单命令
    "UntilCommand",  # Shell 抽象语法树的 UNTIL 命令
    "WhileCommand",  # Shell 抽象语法树的 WHILE 命令
    "EnhanceForCommand",  # Shell 抽象语法树的 FOR 命令（第一种语法）
    "ForCommand",  # Shell 抽象语法树的 FOR 命令（第二种语法）
    "ElifItem", "IfCommand",  # Shell 抽象语法树的 IF 命令
    "CaseItem", "CaseCommand",  # Shell 抽象语法树的 CASE 命令
    "SelectCommand",  # Shell 抽象语法树的 SELECT 命令
    "Coprocess",  # Shell 抽象语法树的协进程
    "Function",  # Shell 抽象语法树的函数
    "Redirection",  # Shell 抽象语法树的重定向子句
    "CommandWithRedirection",  # Shell 抽象语法树包含重定向子句的命令
    "Pipe",  # Shell 抽象语法树中的管道子句
    "CommandWithPipe",  # Shell 抽象语法树中包含管道子句的命令
    "CommandWithRelation",  # Shell 抽象语法树种的命令列表中的单个关系、命令组合的子句
    "CommandWithList",  # Shell 抽象语法树包含命令列表的命令
]


@dataclasses.dataclass(slots=True)
class SimpleCommand(ASTCommand):
    """Shell 抽象语法树的简单命令"""

    word_list: List[ASTWord] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return " ".join(element.source() for element in self.word_list)

    def execute(self, process: SimuProcess, input_stream: Optional[str] = None, **kwargs) -> SimuVariable:
        # 处理只包含赋值语句的情况
        if len(self.word_list) == 1 and self.word_list[0].__class__.__name__ == "Assignment":  # TODO 待优化分析逻辑
            self.word_list[0].execute(process)
            return SimuVariable.empty()

        word_str_list = [word.execute(process).as_string() for word in self.word_list]
        return process.execute_simple_command(word_str_list, input_stream=input_stream)


@dataclasses.dataclass(slots=True)
class UntilCommand(ASTCommand):
    """Shell 抽象语法树的 UNTIL 命令"""

    test_script: ASTScript = dataclasses.field(kw_only=True)
    consequent_script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"until {self.test_script.source()} do {self.consequent_script.source()} done"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.UNTIL_RUN_MODE
        if run_mode in {ConditionRunMode.ONCE, ConditionRunMode.ONLY_CONDITION}:
            self.test_script.execute(process)
        if run_mode in {ConditionRunMode.ONCE, ConditionRunMode.ONLY_COMMANDS}:
            self.consequent_script.execute(process)
        # TODO 考虑移出命名空间
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class WhileCommand(ASTCommand):
    """Shell 抽象语法树的 WHILE 命令"""

    test_script: ASTScript = dataclasses.field(kw_only=True)
    consequent_script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"while {self.test_script.source()} do {self.consequent_script.source()} done"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.WHILE_RUN_MODE
        if run_mode in {ConditionRunMode.ONCE, ConditionRunMode.ONLY_CONDITION}:
            self.test_script.execute(process)
        if run_mode in {ConditionRunMode.ONCE, ConditionRunMode.ONLY_COMMANDS}:
            self.consequent_script.execute(process)
        # TODO 考虑移出命名空间
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class EnhanceForCommand(ASTCommand):
    """Shell 抽象语法树的 FOR 命令（第一种语法）

    样式：
    for name [ [in [words ...] ] ; ]
    do
        commands
    done
    """

    name: ASTWord = dataclasses.field(kw_only=True)
    word_list: Optional[List[ASTWord]] = dataclasses.field(kw_only=True, default=None)
    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        if self.word_list is not None:
            in_word_str = f"in " + " ".join(word.source() for word in self.word_list) + " "
        else:
            in_word_str = ""
        return f"for {self.name.source()} {in_word_str}; do {self.script.source()} done"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.ENHANCE_FOR_RUN_MODE

        # 计算变量名
        name_str = self.name.execute(process).as_string()
        if name_str is None:
            process.add_unknown_command(self.source(), "cannot refer name")
            return SimuVariable.empty()

        if run_mode in {EnhanceForRunMode.ONLY_COMMANDS_USE_FIRST_VALUE,
                        EnhanceForRunMode.ONLY_COMMANDS_USE_LAST_VALUE}:

            # 将变量值添加到命名空间
            if self.word_list is None:
                process.add_unknown_command(self.source(), "cannot refer words")
                return SimuVariable.empty()

            if run_mode == EnhanceForRunMode.ONLY_COMMANDS_USE_FIRST_VALUE:
                value = self.word_list[0].execute(process)
            else:
                value = self.word_list[-1].execute(process)
            process.set_param(name_str, value)

            # 模拟执行命令
            self.script.execute(process)

            # 将变量值移出命名空间
            process.del_param(name_str)  # 待考虑命名空间的问题

        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class ForCommand(ASTCommand):
    """Shell 抽象语法树的 FOR 命令（第二种语法）

    样式：for (( expr1 ; expr2 ; expr3 )) ; do commands ; done
    """

    test_script: ASTScript = dataclasses.field(kw_only=True)
    consequent_script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return (f"for (( {self.test_script.source()} )) ; "
                f"do {self.consequent_script.source()} "
                f"done")

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.FOR_RUN_MODE
        if run_mode in {ForRunMode.ONCE, ForRunMode.ONLY_CONDITION}:
            self.test_script.execute(process)
        if run_mode in {ForRunMode.ONCE, ForRunMode.ONLY_COMMANDS}:
            self.consequent_script.execute(process)
        # TODO 考虑移出命名空间
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class ElifItem(ASTBase):
    """IF 命令中的 ELIF 结构

    样式：
    [elif more-test-commands; then
    more-consequents;]
    """

    test_script: ASTScript = dataclasses.field(kw_only=True)
    consequent_script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"elif {self.test_script.source()} then {self.consequent_script.source()}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.ELIF_RUN_MODE
        if run_mode in {ConditionRunMode.ONCE, ConditionRunMode.ONLY_CONDITION}:
            self.test_script.execute(process)
        if run_mode in {ConditionRunMode.ONCE, ConditionRunMode.ONLY_COMMANDS}:
            self.consequent_script.execute(process)
        # TODO 考虑移出命名空间
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class IfCommand(ASTCommand):
    """Shell 抽象语法树的 IF 命令

    样式：
    if test-commands; then
      consequent-commands;
    [elif more-test-commands; then
      more-consequents;]
    [else alternate-consequents;]
    fi
    """

    test_script: ASTScript = dataclasses.field(kw_only=True)
    consequent_script: ASTScript = dataclasses.field(kw_only=True)
    else_if_list: List[ElifItem] = dataclasses.field(kw_only=True)
    alternate_script: Optional[ASTScript] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        if self.else_if_list:
            else_if_str = " ".join(else_if.source() for else_if in self.else_if_list) + " "
        else:
            else_if_str = ""
        if self.alternate_script is not None:
            else_str = "else " + self.alternate_script.source() + " "
        else:
            else_str = ""
        return (f"if {self.test_script.source()} "
                f"then {self.consequent_script.source()} "
                f"{else_if_str}"
                f"{else_str}"
                f"fi")

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.IF_RUN_MODE
        if run_mode in {IfRunMode.ALL, IfRunMode.IF_ELIF, IfRunMode.IF_ELSE, IfRunMode.ONLY_IF}:
            self.test_script.execute(process)
        if run_mode in {IfRunMode.ALL, IfRunMode.IF_ELIF, IfRunMode.IF_ELSE, IfRunMode.ONLY_IF, IfRunMode.ONLY_COMMAND}:
            self.consequent_script.execute(process)
            # TODO 考虑移出命名空间
        if run_mode in {IfRunMode.ALL, IfRunMode.IF_ELIF, IfRunMode.ONLY_ELIF, IfRunMode.ONLY_COMMAND}:
            for else_if in self.else_if_list:
                else_if.execute(process)
        if run_mode in {IfRunMode.ALL, IfRunMode.IF_ELSE, IfRunMode.ONLY_ELSE, IfRunMode.ONLY_COMMAND}:
            if self.alternate_script is not None:
                self.alternate_script.execute(process)
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class CaseItem(ASTBase):
    """CASE 命令中的每个条件结构

    样式：
    [ [(] pattern [| pattern]…) command-list ;;]…
    """

    pattern_list: List[ASTWord] = dataclasses.field(kw_only=True)
    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        pattern_str = " | ".join(pattern.source() for pattern in self.pattern_list)
        return f"{pattern_str} {self.script.source()};"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.CASE_ITEM_RUN_MODE
        if run_mode in {CaseItemRunMode.ONLY_COMMANDS}:
            self.script.execute(process)
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class CaseCommand(ASTCommand):
    """Shell 抽象语法树的 CASE 命令

    样式：
    case word in
        [ [(] pattern [| pattern]…) command-list ;;]…
    esac
    """

    word: ASTWord = dataclasses.field(kw_only=True)
    item_list: List[CaseItem] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        item_str = "\n".join(item.source() for item in self.item_list)
        return (f"case {self.word.source()} in "
                f"{item_str} "
                f"esac")

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.CASE_RUN_MODE
        if run_mode in {CaseRunMode.ALL}:
            for item in self.item_list:
                item.execute(process)
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class SelectCommand(ASTCommand):
    """Shell 抽象语法树的 SELECT 命令

    样式：
    select name [in words …]
    do
      commands
    done
    """

    name: ASTWord = dataclasses.field(kw_only=True)
    word_list: Optional[List[ASTWord]] = dataclasses.field(kw_only=True)
    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        if self.word_list is not None:
            in_word_str = f"in " + " ".join(word.source() for word in self.word_list)
        else:
            in_word_str = ""
        return f"select {self.name.source()} {in_word_str}; do {self.script.source()} done"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.SELECT_RUN_MODE

        # 计算变量名
        name_str = self.name.execute(process).as_string()
        if name_str is None:
            process.add_unknown_command(self.source(), "cannot refer name")
            return SimuVariable.empty()

        if run_mode in {EnhanceForRunMode.ONLY_COMMANDS_USE_FIRST_VALUE,
                        EnhanceForRunMode.ONLY_COMMANDS_USE_LAST_VALUE}:

            # 将变量值添加到命名空间
            if self.word_list is None:
                process.add_unknown_command(self.source(), "cannot refer words")
                return SimuVariable.empty()

            if run_mode == EnhanceForRunMode.ONLY_COMMANDS_USE_FIRST_VALUE:
                value = self.word_list[0].execute(process)
            else:
                value = self.word_list[-1].execute(process)
            process.set_param(name_str, value)

            # 模拟执行命令
            self.script.execute(process)

            # 将变量值移出命名空间
            process.del_param(name_str)  # 待考虑命名空间的问题

        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class Coprocess(ASTCommand):
    """Shell 抽象语法树的协进程"""

    name: Optional[ASTWord] = dataclasses.field(kw_only=True)
    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        if self.name is not None:
            return f"coproc {self.name.source()} {{ {self.script.source()} }}"
        return f"coproc {{ {self.script.source()} }}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        sub_process = process.system.create_process()
        self.script.execute(sub_process)
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class Function(ASTBase):
    """Shell 抽象语法树的函数"""

    name: ASTWord = dataclasses.field(kw_only=True)
    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"function {self.name.source()} () {{ {self.script.source()} }}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        # TODO 待实现函数相关逻辑
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class Redirection(ASTBase):
    """Shell 抽象语法树的重定向子句"""

    type: RedirectionType = dataclasses.field(kw_only=True)
    number: Optional[int] = dataclasses.field(kw_only=True, default=None)
    word_list: List[ASTWord] = dataclasses.field(kw_only=True)  # TODO 待研究这里是否需要 list

    @staticmethod
    def create_number_redirection(rtype: RedirectionType, number: int, word_list: List[ASTWord]):
        return Redirection(
            type=rtype,
            number=number,
            word_list=word_list
        )

    @staticmethod
    def create_redirection(rtype: RedirectionType, word_list: List[ASTWord]):
        return Redirection(
            type=rtype,
            word_list=word_list
        )

    def source(self) -> str:
        if self.type.value[0] is True:
            return f"{self.number}{self.type.value[1]} " + " ".join(word.source() for word in self.word_list)
        return f"{self.type.value[1]} " + " ".join(word.source() for word in self.word_list)

    def execute(self, process: SimuProcess, input_stream: Optional[str] = None, **kwargs) -> SimuVariable:
        if self.type == RedirectionType.ASCII_0x3E and len(self.word_list) == 1:
            file_name = self.word_list[0].execute(process).as_string()
            if file_name is None:
                process.add_unknown_command(self.source(), "cannot refer file_name")
                return SimuVariable.empty()
            process.write_file(file_name, input_stream)  # TODO 待实现绝对路径
        # TODO 其他重定向待实现
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class CommandWithRedirection(ASTCommand):
    """Shell 抽象语法树包含重定向子句的命令"""

    bare_command: ASTCommand = dataclasses.field(kw_only=True)
    redirection_list: List[Redirection] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(bare_command: ASTCommand,
               redirection_list: Optional[List[Redirection]] = None):
        return CommandWithRedirection(
            bare_command=bare_command,
            redirection_list=redirection_list if redirection_list is not None else []
        )

    def source(self) -> str:
        if self.redirection_list:
            redirection_str = " ".join(redirection.source() for redirection in self.redirection_list)
            return f"{self.bare_command.source()} {redirection_str}"
        else:
            return self.bare_command.source()

    def execute(self, process: SimuProcess, input_stream: Optional[str] = None, **kwargs) -> SimuVariable:
        output_stream = self.bare_command.execute(process, input_stream=input_stream)
        result = output_stream
        for redirection in self.redirection_list:
            if redirection.type == RedirectionType.ASCII_0x3E:
                redirection.execute(process, input_stream=output_stream.as_string())
                result = SimuVariable.empty()  # 将标准输出置为空
            # TODO 待实现其他重定向
        return result


@dataclasses.dataclass(slots=True)
class Pipe(ASTBase):
    """Shell 抽象语法树中的管道子句"""

    type: PipeType = dataclasses.field(kw_only=True)
    command: CommandWithRedirection = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"{self.type.value} {self.command.source()}"

    def execute(self, process: SimuProcess, input_stream: Optional[str] = None, **kwargs) -> SimuVariable:
        output_stream = self.command.execute(process, input_stream=input_stream)
        return output_stream


@dataclasses.dataclass(slots=True)
class CommandWithPipe(ASTBase):
    """Shell 抽象语法树中包含管道子句的命令"""

    command: CommandWithRedirection = dataclasses.field(kw_only=True)
    pipe_list: List[Pipe] = dataclasses.field(kw_only=True)

    @staticmethod
    def create(command: CommandWithRedirection,
               pipe_list: Optional[List[Pipe]] = None):
        return CommandWithPipe(
            command=command,
            pipe_list=pipe_list if pipe_list is not None else []
        )

    def source(self) -> str:
        if self.pipe_list:
            pip_one_str = "".join(pipe_one.source() for pipe_one in self.pipe_list)
            return f"{self.command.source()} {pip_one_str}"
        else:
            return self.command.source()

    def execute(self, process: SimuProcess, input_stream: Optional[str] = None, **kwargs) -> SimuVariable:
        output_stream = self.command.execute(process, input_stream=input_stream)
        for pipe in self.pipe_list:
            output_stream = pipe.execute(process, input_stream=output_stream.as_string())
        return output_stream


@dataclasses.dataclass(slots=True)
class CommandWithRelation(ASTBase):
    """Shell 抽象语法树种的命令列表中的单个关系、命令组合的子句"""

    relation: CommandRelationType = dataclasses.field(kw_only=True)  # 与上一个命令的关系
    command: CommandWithPipe = dataclasses.field(kw_only=True)  # 当前命令

    def source(self) -> str:
        return f"{self.relation.value} {self.command.source()}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        run_mode = process.system.configuration.RELATION_RUN_MODE
        if run_mode in {RelationRunMode.ALL}:
            return self.command.execute(process)
        return SimuVariable.empty()


@dataclasses.dataclass(slots=True)
class CommandWithList(ASTCommand):
    """Shell 抽象语法树包含命令列表的命令"""

    first_command: CommandWithPipe = dataclasses.field(kw_only=True)  # 第一个命令
    other_command_list: List[CommandWithRelation] = dataclasses.field(kw_only=True)  # 后续命令
    end_type: CommandEndType = dataclasses.field(kw_only=True)  # 结束符

    @staticmethod
    def create(first_command: CommandWithPipe,
               end_type: CommandEndType,
               other_command_list: Optional[List[CommandWithRelation]] = None):
        return CommandWithList(
            first_command=first_command,
            other_command_list=other_command_list if other_command_list is not None else [],
            end_type=end_type if end_type is not None else CommandEndType.DEFAULT
        )

    def source(self) -> str:
        if self.other_command_list:
            other_command_list_str = " ".join(command_one.source() for command_one in self.other_command_list)
            return f"{self.first_command.source()} {other_command_list_str} {self.end_type.value}"
        else:
            return f"{self.first_command.source()} {self.end_type.value}"

    def execute(self, process: SimuProcess, input_stream: Optional[str] = None, **kwargs) -> SimuVariable:
        result = [self.first_command.execute(process, input_stream=input_stream).as_string()]
        for other_command in self.other_command_list:
            result.append(other_command.execute(process, input_stream=input_stream).as_string())
        return SimuVariableString.create_by_array(result, sep=" ")  # TODO 分隔符待验证
