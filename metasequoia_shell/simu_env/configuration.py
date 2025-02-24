"""
模拟运行环境全局配置
"""

import dataclasses
import enum

__all__ = [
    "SimuConfiguration",
    "ConditionRunMode",
    "EnhanceForRunMode",
    "ForRunMode",
    "IfRunMode",
    "CaseItemRunMode",
    "CaseRunMode",
    "RelationRunMode",
]


class ConditionRunMode(enum.Enum):
    """条件语句执行模式

    场景 1:
    until [condition]
    do
        commands
    done

    场景 2:
    while [condition]
    do
        commands
    done

    场景 3:
    elif condition
    then
        commands
    """

    # SIMULATE = enum.auto()  # 完全模拟执行【暂不支持】
    ONCE = enum.auto()  # 模拟执行 condition 和 commands 各一次
    ONLY_CONDITION = enum.auto()  # 仅执行 condition 一次
    ONLY_COMMANDS = enum.auto()  # 仅执行 commands 一次
    IGNORE = enum.auto()  # 不执行


class EnhanceForRunMode(enum.Enum):
    """增强 for 语句执行模式

    for name [ [in [words ...] ] ; ]
    do
        commands
    done
    """

    # SIMULATE = enum.auto()  # 完全模拟执行【暂不支持】
    ONLY_COMMANDS_USE_FIRST_VALUE = enum.auto()  # 将 name 初始化为第 1 个值，模拟执行一次 commands 命令
    ONLY_COMMANDS_USE_LAST_VALUE = enum.auto()  # 将 name 初始化为最后 1 个值，模拟执行一次 commands 命令
    IGNORE = enum.auto()  # 不执行


class ForRunMode(enum.Enum):
    """for 语句执行模式

    for (( expr1 ; expr2 ; expr3 ))
    do
        commands
    done
    """

    # SIMULATE = enum.auto()  # 完全模拟执行【暂不支持】
    ONCE = enum.auto()  # 模拟执行 expr1, expr2, expr3 和 commands 各一次
    ONLY_CONDITION = enum.auto()  # 仅执行 expr1, expr2, expr3 一次
    ONLY_COMMANDS = enum.auto()  # 仅执行 commands 一次
    IGNORE = enum.auto()


class IfRunMode(enum.Enum):
    """if 语句运行模式

    if condition1
    then
        commands1
    elif condition2
    then
        commands2
    else
        commands3
    fi
    """

    # SIMULATE = enum.auto()  # 完全模拟执行【暂不支持】
    ALL = enum.auto()  # 运行所有 condition1、commands1、elif（elif 子句中的执行逻辑由 ELIF_RUN_MODE 指定）和 commands3
    IF_ELIF = enum.auto()  # 运行 condition1、commands1 和 elif（elif 子句中的执行逻辑由 ELIF_RUN_MODE 指定）
    IF_ELSE = enum.auto()  # 运行 condition1、commands1 和 commands3
    ONLY_IF = enum.auto()  # 运行 condition1、commands1
    ONLY_ELIF = enum.auto()  # 运行 elif（elif 子句中的执行逻辑由 ELIF_RUN_MODE 指定）
    ONLY_ELSE = enum.auto()  # 运行 commands3
    ONLY_COMMAND = enum.auto()  # 运行 commands1、commands3 和 elif（elif 子句中的执行逻辑由 ELIF_RUN_MODE 指定）
    IGNORE = enum.auto()


class CaseItemRunMode(enum.Enum):
    """case 语句中每个条件结构的运行模式

    [ [(] pattern [| pattern]…) command-list ;;]…
    """

    # SIMULATE = enum.auto()  # 完全模拟执行【暂不支持】
    ONLY_COMMANDS = enum.auto()  # 仅运行命令部分
    IGNORE = enum.auto()


class CaseRunMode(enum.Enum):
    """case 语句的运行模式"""

    # SIMULATE = enum.auto()  # 完全模拟执行【暂不支持】
    ALL = enum.auto()  # 运行所有条件中的命令
    IGNORE = enum.auto()  # 跳过 case 语句


class RelationRunMode(enum.Enum):
    """&& 或 || 关系的运行模式"""

    # SIMULATE = enum.auto()  # 完全模拟执行【暂不支持】
    ALL = enum.auto()  # 运行所有任务


@dataclasses.dataclass(slots=True)
class SimuConfiguration:
    """模拟执行环境配置信息"""

    # -------------------- 流程控制语句执行策略 --------------------
    # until 语句执行模式：默认仅执行 commands 一次（condition 为条件表达式，是否执行通常没有影响）
    UNTIL_RUN_MODE: ConditionRunMode = dataclasses.field(
        kw_only=True,
        default=ConditionRunMode.ONLY_COMMANDS
    )

    # while 语句执行模式：默认仅执行 commands 一次（condition 为条件表达式，是否执行通常没有影响）
    WHILE_RUN_MODE: ConditionRunMode = dataclasses.field(
        kw_only=True,
        default=ConditionRunMode.ONLY_COMMANDS
    )

    # 增强 for 语句的执行模式：默认仅执行 commands 一次
    ENHANCE_FOR_RUN_MODE: EnhanceForRunMode = dataclasses.field(
        kw_only=True,
        default=EnhanceForRunMode.ONLY_COMMANDS_USE_FIRST_VALUE
    )

    # for 语句的执行模式：默认执行 expr1, expr2, expr3 和 commands 各一次
    FOR_RUN_MODE: ForRunMode = dataclasses.field(
        kw_only=True,
        default=ForRunMode.ONCE
    )

    # elif 语句执行模式：默认仅执行 commands 一次（condition 为条件表达式，是否执行通常没有影响）
    ELIF_RUN_MODE: ConditionRunMode = dataclasses.field(
        kw_only=True,
        default=ConditionRunMode.ONLY_COMMANDS
    )

    # if 语句运行模式：默认运行所有部分（elif 子句中的执行逻辑由 ELIF_RUN_MODE 指定）
    IF_RUN_MODE: IfRunMode = dataclasses.field(
        kw_only=True,
        default=IfRunMode.ONLY_COMMAND
    )

    # case 语句的每个条件结构的运行模式：默认仅运行命令部分
    CASE_ITEM_RUN_MODE: CaseItemRunMode = dataclasses.field(
        kw_only=True,
        default=CaseItemRunMode.ONLY_COMMANDS
    )

    # case 语句的运行模式：默认运行所有条件中的命令
    CASE_RUN_MODE: CaseRunMode = dataclasses.field(
        kw_only=True,
        default=CaseRunMode.ALL
    )

    # select 语句的执行模式：默认仅执行 commands 一次
    SELECT_RUN_MODE: EnhanceForRunMode = dataclasses.field(
        kw_only=True,
        default=EnhanceForRunMode.ONLY_COMMANDS_USE_FIRST_VALUE
    )

    # && 和 || 的执行模式：默认运行运行所有任务
    RELATION_RUN_MODE: RelationRunMode = dataclasses.field(
        kw_only=True,
        default=RelationRunMode.ALL
    )
