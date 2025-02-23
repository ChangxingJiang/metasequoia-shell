"""
Shell 抽象语法树中的元素层级节点
"""

import dataclasses
import re
from typing import List, Optional

from metasequoia_shell.ast.enum_type import SubstitutionType
from metasequoia_shell.ast.node_base import ASTBase
from metasequoia_shell.ast.node_base import ASTElement
from metasequoia_shell.ast.node_base import ASTScript
from metasequoia_shell.ast.utils import decode_asci_c_string
from metasequoia_shell.ast.utils import get_array_at
from metasequoia_shell.ast.utils import get_array_star
from metasequoia_shell.simu_env import SimuVariable, SimuVariableInteger, SimuVariableString
from metasequoia_shell.simu_env.system import SimuProcess

__all__ = [
    "Ident",  # 普通文本元素
    "Param0",  # 特殊参数 `$0`：返回 shell 或 shell 脚本的名称
    "Param1",  # 位置参数 `$1`：返回命令参数中的第 1 个位置参数
    "Param2",  # 位置参数 `$2`：返回命令参数中的第 2 个位置参数
    "Param3",  # 位置参数 `$3`：返回命令参数中的第 3 个位置参数
    "Param4",  # 位置参数 `$4`：返回命令参数中的第 4 个位置参数
    "Param5",  # 位置参数 `$5`：返回命令参数中的第 5 个位置参数
    "Param6",  # 位置参数 `$6`：返回命令参数中的第 6 个位置参数
    "Param7",  # 位置参数 `$7`：返回命令参数中的第 7 个位置参数
    "Param8",  # 位置参数 `$8`：返回命令参数中的第 8 个位置参数
    "Param9",  # 位置参数 `$9`：返回命令参数中的第 9 个位置参数
    "ParamStar",  # 特殊参数 `$*`：展开为从第一个开始的位置参数的列表（当在双引号中时返回一个完整字符串）
    "ParamAt",  # 特殊参数 `$@`：展开为从第一个开始的位置参数的列表（当在双引号中时返回每个参数字符串的列表）
    "ParamPound",  # 特殊参数 `$#`：展开为十进制形式的位置参数的数量
    "ParamQuestion",  # 特殊参数 `$?`：展开为最近执行的前台管道的退出状态
    "ParamHyphen",  # 特殊参数 `$-`：展开为调用时指定的当前选项标志
    "ParamDollar",  # 特殊参数 `$$`：展开为 shell 的进程 ID
    "ParamExclamation",  # 特殊参数 `$!`：展开为为最近放入后台运行的作业的进程 ID
    "ArithmeticExpansion",  # Shell 抽象语法树的算术扩展
    "BraceExpansion",  # Shell 抽象语法树的大括号扩展
    "TildeExpansion",  # Shell 抽象语法树的波浪线扩展
    "BraceParamExpansion",  # Shell 抽象语法树的有大括号的参数扩展
    "ParamExpansion",  # Shell 抽象语法树的没有大括号的参数扩展
    "CommandSubstitution",  # Shell 抽象语法树的命令替换
    "SingleQuoteString",  # Shell 抽象语法树中的单引号字符串
    "DollarSingleQuoteString",  # Shell 抽象语法树中的 ANSI-C 扩展单引号字符串
    "DoubleQuoteString",  # Shell 抽象语法树的双引号字符串
    "DollarDoubleQuoteString",  # Shell 抽象语法树的本地化翻译字符串
    "ArrayAt",  # array[@]
    "ArrayStar",  # array[*]
    "ArrayGetter",  # array[subscript]
]


@dataclasses.dataclass(slots=True)
class Ident(ASTElement):
    """普通文本元素"""

    string: str = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return self.string

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(self.string)


@dataclasses.dataclass(slots=True)
class Param0(ASTElement):
    """特殊参数 `$0`：返回 shell 或 shell 脚本的名称"""

    def source(self) -> str:
        return "$0"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_script_name())


@dataclasses.dataclass(slots=True)
class Param1(ASTElement):
    """位置参数 `$1`：返回命令参数中的第 1 个位置参数"""

    def source(self) -> str:
        return "$1"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(1, default=""))


@dataclasses.dataclass(slots=True)
class Param2(ASTElement):
    """位置参数 `$2`：返回命令参数中的第 2 个位置参数"""

    def source(self) -> str:
        return "$2"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(2, default=""))


@dataclasses.dataclass(slots=True)
class Param3(ASTElement):
    """位置参数 `$3`：返回命令参数中的第 3 个位置参数"""

    def source(self) -> str:
        return "$3"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(3, default=""))


@dataclasses.dataclass(slots=True)
class Param4(ASTElement):
    """位置参数 `$4`：返回命令参数中的第 4 个位置参数"""

    def source(self) -> str:
        return "$4"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(4, default=""))


@dataclasses.dataclass(slots=True)
class Param5(ASTElement):
    """位置参数 `$5`：返回命令参数中的第 5 个位置参数"""

    def source(self) -> str:
        return "$5"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(5, default=""))


@dataclasses.dataclass(slots=True)
class Param6(ASTElement):
    """位置参数 `$6`：返回命令参数中的第 6 个位置参数"""

    def source(self) -> str:
        return "$6"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(6, default=""))


@dataclasses.dataclass(slots=True)
class Param7(ASTElement):
    """位置参数 `$7`：返回命令参数中的第 7 个位置参数"""

    def source(self) -> str:
        return "$7"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(7, default=""))


@dataclasses.dataclass(slots=True)
class Param8(ASTElement):
    """位置参数 `$8`：返回命令参数中的第 8 个位置参数"""

    def source(self) -> str:
        return "$8"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(8, default=""))


@dataclasses.dataclass(slots=True)
class Param9(ASTElement):
    """位置参数 `$9`：返回命令参数中的第 9 个位置参数"""

    def source(self) -> str:
        return "$9"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.get_pos_param(9, default=""))


@dataclasses.dataclass(slots=True)
class ParamStar(ASTElement):
    """特殊参数 `$*`：展开为从第一个开始的位置参数的列表（当在双引号中时返回一个完整字符串）"""

    def source(self) -> str:
        return "$*"

    def execute(self, process: SimuProcess, is_in_double_quote: bool = False, **kwargs) -> SimuVariable:
        return get_array_star(process.get_pos_params(), is_in_double_quote=is_in_double_quote)


@dataclasses.dataclass(slots=True)
class ParamAt(ASTElement):
    """特殊参数 `$@`：展开为从第一个开始的位置参数的列表（当在双引号中时返回每个参数字符串的列表）"""

    def source(self) -> str:
        return "$@"

    def execute(self, process: SimuProcess, is_in_double_quote: bool = False, **kwargs) -> SimuVariable:
        return get_array_at(process.get_pos_params(), is_in_double_quote=is_in_double_quote)


@dataclasses.dataclass(slots=True)
class ParamPound(ASTElement):
    """特殊参数 `$#`：展开为十进制形式的位置参数的数量"""

    def source(self) -> str:
        return "$#"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableInteger.create(len(process.get_pos_params()))


@dataclasses.dataclass(slots=True)
class ParamQuestion(ASTElement):
    """特殊参数 `$?`：展开为最近执行的前台管道的退出状态"""

    def source(self) -> str:
        return "$?"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableInteger.create(process.get_last_status())


@dataclasses.dataclass(slots=True)
class ParamHyphen(ASTElement):
    """特殊参数 `$-`：展开为调用时指定的当前选项标志"""

    def source(self) -> str:
        return "$-"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(process.system.default_shell_flags)  # TODO 将默认返回值改为进程返回值


@dataclasses.dataclass(slots=True)
class ParamDollar(ASTElement):
    """特殊参数 `$$`：展开为 shell 的进程 ID"""

    def source(self) -> str:
        return "$$"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableInteger.create(process.process_id)


@dataclasses.dataclass(slots=True)
class ParamExclamation(ASTElement):
    """特殊参数 `$!`：展开为为最近放入后台运行的作业的进程 ID"""

    def source(self) -> str:
        return "$!"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableInteger.create(process.get_last_sub_process_id())


@dataclasses.dataclass(slots=True)
class ArithmeticExpansion(ASTElement):
    """Shell 抽象语法树的算术扩展"""

    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"$(( {self.script.source()} ))"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return self.script.execute_as_arithmetic(process)


@dataclasses.dataclass(slots=True)
class BraceExpansion(ASTBase):
    """Shell 抽象语法树的大括号扩展"""

    element_list: List[ASTElement] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return "{" + ",".join(element.source() for element in self.element_list) + "}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariable.unknown()  # TODO 待开发处理逻辑


@dataclasses.dataclass(slots=True)
class TildeExpansion(ASTBase):
    """Shell 抽象语法树的波浪线扩展"""

    element_list: List[ASTElement] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return "~" + "".join(element.source() for element in self.element_list)

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariable.unknown()  # TODO 待开发处理逻辑


@dataclasses.dataclass(slots=True)
class BraceParamExpansion(ASTBase):
    """Shell 抽象语法树的有大括号的参数扩展

    支持如下 3 种形式：
    {name:offset:length}
    {name:offset}
    {name}

    支持间接引用
    """

    element_list: List[ASTElement] = dataclasses.field(kw_only=True)  # TODO 待考虑是否可以改为非列表或仅支持字符串
    indirect: bool = dataclasses.field(kw_only=True)  # 间接引用（是否包含 !）
    offset: Optional[ASTElement] = dataclasses.field(kw_only=True, default=None)  # TODO 待改为仅支持数字
    length: Optional[ASTElement] = dataclasses.field(kw_only=True, default=None)  # TODO 待改为仅支持数字

    def source(self) -> str:
        indirect_str: str = "!" if self.indirect is True else ""
        if self.offset is not None and self.length is not None:
            extra = f":{self.offset.source()}:{self.length.source()}"
        elif self.offset is not None:
            extra = f":{self.offset.source()}"
        else:
            extra = ""
        return "${" + indirect_str + "".join(element.source() for element in self.element_list) + extra + "}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        if self.offset is not None or self.length is not None:
            return SimuVariable.unknown()  # TODO 待增加处理逻辑
        if self.indirect is True:
            return SimuVariable.unknown()  # TODO 待增加处理逻辑

        # 生成变量名
        param_name_elements = []
        for element in self.element_list:
            value = element.execute(process).as_string()
            if value is None:
                return SimuVariable.unknown()
            param_name_elements.append(value)
        param_name = "".join(param_name_elements)

        return process.get_param(param_name)


@dataclasses.dataclass(slots=True)
class ParamExpansion(ASTBase):
    """Shell 抽象语法树的没有大括号的参数扩展"""

    name: str = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"${self.name}"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return process.get_param(self.name)


@dataclasses.dataclass(slots=True)
class CommandSubstitution(ASTBase):
    """Shell 抽象语法树的命令替换"""

    type: SubstitutionType = dataclasses.field(kw_only=True)
    script: ASTScript = dataclasses.field(kw_only=True)

    @staticmethod
    def create_curve(script: ASTScript) -> "CommandSubstitution":
        return CommandSubstitution(type=SubstitutionType.CURVE, script=script)

    @staticmethod
    def create_back_quote(script: ASTScript) -> "CommandSubstitution":
        return CommandSubstitution(type=SubstitutionType.BACK_QUOTE, script=script)

    def source(self) -> str:
        if self.type == SubstitutionType.CURVE:
            return "$(" + self.script.source() + ")"
        if self.type == SubstitutionType.BACK_QUOTE:
            return "`" + self.script.source() + "`"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return self.script.execute(process)


@dataclasses.dataclass(slots=True)
class SingleQuoteString(ASTElement):
    """Shell 抽象语法树中的单引号字符串

    形如 `'abc'` 的字符序列称为单引号字符串，单引号字符串保留单引号内所有字符的字面值。
    在单引号字符串中，任何特殊符号均不生效（包括转义符）。

    Attributes
    ----------
    string : str
        字符串
    """

    string: Optional[str] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        if self.string is None:
            return "''"
        return f"'{self.string}'"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(self.string)


# 匹配 ASCI-C 扩展单引号字符串中的 \nnn 格式：八进制编码
PATTERN_OCT_VALUE = re.compile(r"\\n([0-7]{1,3})")

# 匹配 ASCI-C 扩展单引号字符串中的 \xHH 格式：十六进制编码
PATTERN_HEX_VALUE = re.compile(r"\\x([0-9AaBbCcDdEeFf]{1,2})")

# 匹配 ASCI-C 扩展单引号字符串中的 \uHHHH 格式：十六进制 Unicode 编码
PATTERN_UNICODE_4_VALUE = re.compile(r"\\u([0-9AaBbCcDdEeFf]{1,4})")

# 匹配 ASCI-C 扩展单引号字符串中的 \uHHHHHHHH 格式：十六进制 Unicode 编码
PATTERN_UNICODE_8_VALUE = re.compile(r"\\U([0-9AaBbCcDdEeFf]{1,8})")


@dataclasses.dataclass(slots=True)
class DollarSingleQuoteString(ASTElement):
    """Shell 抽象语法树中的 ANSI-C 扩展单引号字符串

    形如 `$'abc'` 的字符序列称为 ANSI-C 扩展单引号字符串，ANSI-C 扩展单引号字符串是一种特殊的单引号字符串，会将字符串中的转义符根据 ANSI-C
    标准进行替换。
    在 ANSI-C 扩展字符串中，只有以转义符开头的 ANSI-C 标准符号具有特殊含义。

    Attributes
    ----------
    string : str
        字符串
    """

    string: Optional[str] = dataclasses.field(kw_only=True)
    actual: Optional[str] = dataclasses.field(kw_only=True)  # 去除特殊字符后的字符串

    @staticmethod
    def create(string: Optional[str]) -> "DollarSingleQuoteString":
        return DollarSingleQuoteString(string=string, actual=decode_asci_c_string(string))

    def source(self) -> str:
        if self.string is None:
            return "$''"
        return f"$'{self.string}'"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        return SimuVariableString.create(self.actual)


@dataclasses.dataclass(slots=True)
class DoubleQuoteString(ASTElement):
    """Shell 抽象语法树的双引号字符串"""

    element_list: Optional[List[ASTElement]] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        if self.element_list is None:
            return "\"\""
        return "\"" + "".join(element.source() for element in self.element_list) + "\""

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        result = []
        for element in self.element_list:
            value = element.execute(process).as_string()
            if value is None:
                return SimuVariable.unknown()
            result.append(value)
        return SimuVariableString.create("".join(result))


@dataclasses.dataclass(slots=True)
class DollarDoubleQuoteString(ASTElement):
    """Shell 抽象语法树的本地化翻译字符串"""

    element_list: Optional[List[ASTElement]] = dataclasses.field(kw_only=True)

    def source(self) -> str:
        if self.element_list is None:
            return "$\"\""
        return "$\"" + "".join(element.source() for element in self.element_list) + "\""

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        # TODO 待考虑本地化翻译的特殊处理逻辑
        result = []
        for element in self.element_list:
            value = element.execute(process).as_string()
            if value is None:
                return SimuVariable.unknown()
            result.append(value)
        return SimuVariableString.create("".join(result))


@dataclasses.dataclass(slots=True)
class ArrayAt(ASTElement):
    """array[@]"""

    array: str = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"{self.array}[@]"

    def execute(self, process: SimuProcess, is_in_double_quote: bool = False, **kwargs) -> SimuVariable:
        return get_array_at(process.get_param(self.array).as_array(), is_in_double_quote=is_in_double_quote)


@dataclasses.dataclass(slots=True)
class ArrayStar(ASTElement):
    """Array[*]"""

    array: str = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"{self.array}[*]"

    def execute(self, process: SimuProcess, is_in_double_quote: bool = False, **kwargs) -> SimuVariable:
        return get_array_star(process.get_param(self.array).as_array(), is_in_double_quote=is_in_double_quote)


@dataclasses.dataclass(slots=True)
class ArrayGetter(ASTElement):
    """Array[subscript]"""

    array: str = dataclasses.field(kw_only=True)
    script: ASTScript = dataclasses.field(kw_only=True)

    def source(self) -> str:
        return f"{self.array}[{self.script.source()}]"

    def execute(self, process: SimuProcess, **kwargs) -> SimuVariable:
        # 尝试将 sub_script 解析为数组下标
        index = self.script.execute(process).as_integer()
        if index is None:
            return SimuVariable.unknown()

        # 尝试获取变量
        variable = process.get_param(self.array)
        if variable.is_unknown:
            return SimuVariable.unknown()

        # 尝试获取第 index 个元素
        value_list = variable.as_array()
        if index > len(value_list):
            return SimuVariable.empty()  # 如果元素不存在则返回空变量
        return SimuVariableString.create(value_list[index])
