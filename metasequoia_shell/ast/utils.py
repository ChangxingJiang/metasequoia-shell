"""
抽象语法树的通用工具函数
"""

import re
from typing import List, Optional

from metasequoia_shell.simu_env.variable import SimuVariable, SimuVariableArray, SimuVariableString

__all__ = [
    "get_array_star",
    "get_array_at",
    "decode_asci_c_string",
]


def get_array_star(params: List[str], is_in_double_quote: bool) -> SimuVariable:
    """计算 array[*] 或 $* 的模拟执行结果

    样例 1：
    > set -- "first argument" "second argument"
    > for arg in "$*"; do echo "$arg"; done
    first argument second argument

    样例 2：
    > set -- "first argument" "second argument"
    > for arg in $*; do echo "$arg"; done
    first
    argument
    second
    argument

    Parameters
    ----------
    params : List[str]
        参数列表
    is_in_double_quote : bool
        是否在双引号中

    Returns
    -------
    SimuVariable
        模拟执行的变量
    """
    if is_in_double_quote:
        return SimuVariableString.create(" ".join(params))

    result = []
    for param in params:
        result.extend(param.split(" "))
    return SimuVariableArray.create(result)


def get_array_at(params: List[str], is_in_double_quote: bool) -> SimuVariable:
    """计算 array[*] 或 $* 的模拟执行结果

    样例 1：
    > set -- "first argument" "second argument"
    > for arg in "$@"; do echo "$arg"; done
    first argument
    second argument

    样例 2：
    > set -- "first argument" "second argument"
    > for arg in $@; do echo "$arg"; done
    first
    argument
    second
    argument

    Parameters
    ----------
    params : List[str]
        参数列表
    is_in_double_quote : bool
        是否在双引号中

    Returns
    -------
    SimuVariable
        模拟执行的变量
    """
    if is_in_double_quote:
        return SimuVariableArray.create(params)

    result = []
    for param in params:
        result.extend(param.split(" "))
    return SimuVariableArray.create(result)


# 匹配 ASCI-C 扩展单引号字符串中的 \nnn 格式：八进制编码
PATTERN_OCT_VALUE = re.compile(r"\\n([0-7]{1,3})")

# 匹配 ASCI-C 扩展单引号字符串中的 \xHH 格式：十六进制编码
PATTERN_HEX_VALUE = re.compile(r"\\x([0-9AaBbCcDdEeFf]{1,2})")

# 匹配 ASCI-C 扩展单引号字符串中的 \uHHHH 格式：十六进制 Unicode 编码
PATTERN_UNICODE_4_VALUE = re.compile(r"\\u([0-9AaBbCcDdEeFf]{1,4})")

# 匹配 ASCI-C 扩展单引号字符串中的 \uHHHHHHHH 格式：十六进制 Unicode 编码
PATTERN_UNICODE_8_VALUE = re.compile(r"\\U([0-9AaBbCcDdEeFf]{1,8})")


def decode_asci_c_string(string: Optional[str]) -> Optional[str]:
    """解码 ASCI-C 字符串"""
    if string is None:
        return None
    actual = string.replace("\\a", "\a")
    actual = actual.replace("\\b", "\b")
    actual = actual.replace("\\e", r"\e")  # 不是 ANSI C 字符
    actual = actual.replace("\\E", r"\E")  # 不是 ANSI C 字符
    actual = actual.replace("\\f", "\f")
    actual = actual.replace("\\n", "\n")
    actual = actual.replace("\\r", "\r")
    actual = actual.replace("\\t", "\t")
    actual = actual.replace("\\v", "\v")
    actual = actual.replace("\\\\", "\\")
    actual = actual.replace("\\'", "'")
    actual = actual.replace("\\\"", "\"")
    actual = actual.replace("\\?", "?")
    actual = PATTERN_OCT_VALUE.sub(lambda x: chr(int(x.group(1), base=8)), actual)
    actual = PATTERN_HEX_VALUE.sub(lambda x: chr(int(x.group(1), base=16)), actual)
    actual = PATTERN_UNICODE_4_VALUE.sub(lambda x: chr(int(x.group(1), base=16)), actual)
    actual = PATTERN_UNICODE_8_VALUE.sub(lambda x: chr(int(x.group(1), base=16)), actual)
    return actual
