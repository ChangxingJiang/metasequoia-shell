from typing import Dict, Tuple

import metasequoia_parser as ms_parser
from metasequoia_parser.lexical import DEFAULT
from metasequoia_parser.template.charset import ALPHA, ALPHA_LOWER, ALPHA_UPPER, NUMBER
from metasequoia_shell import lexical_operator as op
from metasequoia_shell.common import update_dict
from metasequoia_shell.lexical_state import CharState as CState
from metasequoia_shell.lexical_state import NestState as NState
from metasequoia_shell.terminal_type import ShellTerminalType as TType

# ANSI-C 扩展中，转义符后有特殊意义的字符集合
AFTER_ANSI_C_ESCAPE = frozenset({"a", "b", "e", "E", "f", "n", "r", "t", "v", "\\", "'", "\"", "?", "n", "x", "u",
                                 "U", "c"})

# 所有可以被用作参数的字母
CHARSET_PARAM = frozenset(ALPHA_UPPER | ALPHA_LOWER | NUMBER | {"_"})

# 当前词语的结束符
END_WORD = frozenset({" ", "\t"})

# 当前命令的结束符
END_COMMAND = frozenset({";", "\n"})

# CState.DOLLAR 的通用行为表
COMMON_DOLLAR_MAP = {
    # 特殊参数 I
    "0": op.MoveFixedSetCharState(end_as=TType.DOLLAR_0, value="$0", char_state=CState.INIT),

    # 位置参数
    "1": op.MoveFixedSetCharState(end_as=TType.DOLLAR_1, value="$1", char_state=CState.INIT),
    "2": op.MoveFixedSetCharState(end_as=TType.DOLLAR_2, value="$2", char_state=CState.INIT),
    "3": op.MoveFixedSetCharState(end_as=TType.DOLLAR_3, value="$3", char_state=CState.INIT),
    "4": op.MoveFixedSetCharState(end_as=TType.DOLLAR_4, value="$4", char_state=CState.INIT),
    "5": op.MoveFixedSetCharState(end_as=TType.DOLLAR_5, value="$5", char_state=CState.INIT),
    "6": op.MoveFixedSetCharState(end_as=TType.DOLLAR_6, value="$6", char_state=CState.INIT),
    "7": op.MoveFixedSetCharState(end_as=TType.DOLLAR_7, value="$7", char_state=CState.INIT),
    "8": op.MoveFixedSetCharState(end_as=TType.DOLLAR_8, value="$8", char_state=CState.INIT),
    "9": op.MoveFixedSetCharState(end_as=TType.DOLLAR_9, value="$9", char_state=CState.INIT),

    # 特殊参数 II
    "!": op.MoveFixedSetCharState(end_as=TType.DOLLAR_0x21, value="$!", char_state=CState.INIT),
    "#": op.MoveFixedSetCharState(end_as=TType.DOLLAR_0x23, value="$#", char_state=CState.INIT),
    "*": op.MoveFixedSetCharState(end_as=TType.DOLLAR_0x2A, value="$*", char_state=CState.INIT),
    "-": op.MoveFixedSetCharState(end_as=TType.DOLLAR_0x2D, value="$-", char_state=CState.INIT),
    "?": op.MoveFixedSetCharState(end_as=TType.DOLLAR_0x3F, value="$?", char_state=CState.INIT),
    "@": op.MoveFixedSetCharState(end_as=TType.DOLLAR_0x40, value="$@", char_state=CState.INIT),
    "$": op.MoveFixedSetCharState(end_as=TType.DOLLAR_DOLLAR, value="$$", char_state=CState.INIT),

    # 包含大括号的参数扩展
    "{": op.MoveFixedAppendState(end_as=TType.DOLLAR_0x7B, value="${", nest_state=NState.IN_BRACE_PARAM),

    # ASCI-C 扩展字符串
    "'": op.MoveFixedAppendState(end_as=TType.DOLLAR_SINGLE_QUOTE, value="$'",
                                 nest_state=NState.IN_DOLLAR_SINGLE_QUOTE),

    # 本地化翻译字符串
    "\"": op.MoveFixedAppendState(end_as=TType.DOLLAR_DOUBLE_QUOTE, value="$\"",
                                  nest_state=NState.IN_DOLLAR_DOUBLE_QUOTE),

    # 小括号的命令替换 | 算术替换
    "(": op.SkipSetCharState(char_state=CState.DOLLAR_0x28),

    # 不包含大括号的参数扩展
    frozenset(ALPHA | {"_"}): op.FixedAppendState(end_as=TType.DOLLAR, value="$", nest_state=NState.IN_PARAM),

    DEFAULT: op.FixedSetCharState(end_as=TType.DOLLAR, value="$", char_state=CState.INIT),

    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.DOLLAR, value="$", char_state=CState.INIT),
}

# CState.DOLLAR_0x28 的通用行为表
COMMON_DOLLAR_0x28_MAP = {
    # 算术替换
    "(": op.MoveFixedAppendState(end_as=TType.DOLLAR_0x28_0x28, value="$((", nest_state=NState.IN_ARITHMETIC_EXPANSION),

    # 小括号的命令替换
    DEFAULT: op.FixedAppendState(end_as=TType.DOLLAR_0x28, value="$(", nest_state=NState.IN_DOLLAR_CURVE),

    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.DOLLAR_0x28, value="$(", char_state=CState.INIT),
}

# CState.INIT 的通用行为表
COMMON_INIT_MAP = {
    # TODO 将闭括号等符号增加只有开括号时才能生效的逻辑
    " ": op.MoveFixed(end_as=TType.SPACE, value=" "),
    "\t": op.MoveFixed(end_as=TType.SPACE, value="\t"),  # 将 \t 视为与空格性质相同的终结符
    ";": op.MoveFixed(end_as=TType.ASCII_0x3B, value=";"),
    "\n": op.MoveFixed(end_as=TType.ASCII_0x0A, value="\n"),
    "'": op.MoveFixedAppendState(end_as=TType.SINGLE_QUOTE, value="'", nest_state=NState.IN_SINGLE_QUOTE),
    "\"": op.MoveFixedAppendState(end_as=TType.DOUBLE_QUOTE_OPEN, value="\"", nest_state=NState.IN_DOUBLE_QUOTE),
    "$": op.SkipSetCharState(char_state=CState.DOLLAR),
    "`": op.MoveFixedAppendState(end_as=TType.BACK_QUOTE_OPEN, value="`", nest_state=NState.IN_BACK_QUOTE),
    "~": op.MoveFixed(end_as=TType.SLIDE, value="~"),  # TODO 波浪线扩展
    "=": op.SkipSetCharState(char_state=CState.ASCII_0x3D),
    "{": op.SkipSetCharState(char_state=CState.ASCII_0x7B),
    "(": op.SkipSetCharState(char_state=CState.ASCII_0x28),
    ")": op.SkipSetCharState(char_state=CState.ASCII_0x29),
    "<": op.SkipSetCharState(char_state=CState.ASCII_0x3C),
    ">": op.SkipSetCharState(char_state=CState.ASCII_0x3E),
    "|": op.SkipSetCharState(char_state=CState.ASCII_0x7C),
    "&": op.SkipSetCharState(char_state=CState.ASCII_0x26),
    "[": op.SkipSetCharState(char_state=CState.ASCII_0x5B),
    "]": op.SkipSetCharState(char_state=CState.ASCII_0x5D),
    "#": op.SkipSetCharState(char_state=CState.COMMENT),
    "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
    NUMBER: op.ShiftSetCharState(char_state=CState.NUMBER),
    DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
    ms_parser.lexical.END: op.Finish(),
}

# CState.NORMAL 通用行为表
COMMON_NORMAL_MAP = {
    END_WORD: op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    END_COMMAND: op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "'": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "\"": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "$": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "`": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "~": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "{": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "(": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    ")": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "<": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    ">": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "|": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "&": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "=": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
    DEFAULT: op.Shift(),
    ms_parser.lexical.END: op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT)
}

# CState.ASCII_0x3D
# 在 = 之后：如果之后是空格、命令结束符或结束符，则将 = 作为常规 IDENT 添加；否则将 = 作为赋值语句的等号添加
COMMON_ASCII_0x3D_MAP = {
    # 解析特殊符号
    "=": op.MoveFixedSetCharState(end_as=TType.IDENT, value="==", char_state=CState.INIT),
    "~": op.MoveFixedSetCharState(end_as=TType.IDENT, value="=~", char_state=CState.INIT),

    "\n": op.FixedSetCharState(end_as=TType.IDENT, value="=", char_state=CState.INIT),
    ";": op.FixedSetCharState(end_as=TType.IDENT, value="=", char_state=CState.INIT),
    "&": op.FixedSetCharState(end_as=TType.IDENT, value="=", char_state=CState.INIT),
    END_WORD: op.FixedSetCharState(end_as=TType.IDENT, value="=", char_state=CState.INIT),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x3D, value="=", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.IDENT, value="=", char_state=CState.INIT),
}

# CState.ASCII_0x7B 的通用行为
COMMON_ASCII_0x7B_MAP = {
    # 大括号作为保留字（命令组）
    END_WORD: op.FixedAppendState(end_as=TType.KEYWORD_BRACE_OPEN, value="{", nest_state=NState.IN_GROUPING_BRACE),
    "\n": op.FixedAppendState(end_as=TType.KEYWORD_BRACE_OPEN, value="{", nest_state=NState.IN_GROUPING_BRACE),

    # 大括号作为大括号扩展
    DEFAULT: op.FixedAppendState(end_as=TType.ASCII_0x7B, value="{", nest_state=NState.IN_BRACE),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x7B, value="{", char_state=CState.INIT),
}

# CState.COMMENT 的通用行为
COMMON_COMMENT_MAP = {
    "\n": op.NothingSetCharState(char_state=CState.INIT),
    DEFAULT: op.Skip(),
    ms_parser.lexical.END: op.NothingSetCharState(char_state=CState.INIT),
}

# CState.ASCII_0x28
COMMON_ASCII_0x28_MAP = {
    "(": op.MoveFixedAppendState(end_as=TType.ASCII_0x28_0x28, value="((", nest_state=NState.IN_ARITHMETIC_EXPANSION),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x28, value="(", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x28, value="(", char_state=CState.INIT),
}

# CState.ASCII_0x29
COMMON_ASCII_0x29_MAP = {
    ")": op.MoveFixedSetCharState(end_as=TType.ASCII_0x29_0x29, value="))", char_state=CState.INIT),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x29, value=")", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x29, value=")", char_state=CState.INIT),
}

# CState.ASCII_0x3C
COMMON_ASCII_0x3C_MAP = {
    "(": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3C_0x28, value="<(", char_state=CState.INIT),
    "&": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3C_0x26, value="<&", char_state=CState.INIT),
    ">": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3C_0x3E, value="<>", char_state=CState.INIT),
    "<": op.SkipSetCharState(char_state=CState.ASCII_0x3C_0x3C),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x3C, value="<", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x3C, value="<", char_state=CState.INIT),
}

# CState.ASCII_0x3C_0x3C
COMMON_ASCII_0x3C_0x3C_MAP = {
    "-": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3C_0x3C_0x2D, value="<<-", char_state=CState.INIT),
    "<": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3C_0x3C_0x3C, value="<<<", char_state=CState.INIT),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x3C_0x3C, value="<<", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x3C_0x28, value="<<", char_state=CState.INIT),
}

# CState.ASCII_0x3E
COMMON_ASCII_0x3E_MAP = {
    "(": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3E_0x28, value=">(", char_state=CState.INIT),
    ">": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3E_0x3E, value=">>", char_state=CState.INIT),
    "&": op.MoveFixedSetCharState(end_as=TType.ASCII_0x3E_0x26, value=">&", char_state=CState.INIT),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x3E, value=">", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x3E, value=">", char_state=CState.INIT),
}

# CState.ASCII_0x7C
COMMON_ASCII_0x7C_MAP = {
    "|": op.MoveFixedSetCharState(end_as=TType.ASCII_0x7C_0x7C, value="||", char_state=CState.INIT),
    "&": op.MoveFixedSetCharState(end_as=TType.ASCII_0x7C_0x26, value="|&", char_state=CState.INIT),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x7C, value="|", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x7C, value="|", char_state=CState.INIT),
}

# CState.ASCII_0x26
COMMON_ASCII_0x26_MAP = {
    "&": op.MoveFixedSetCharState(end_as=TType.ASCII_0x26_0x26, value="&&", char_state=CState.INIT),
    ">": op.SkipSetCharState(char_state=CState.ASCII_0x26_0x3E),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x26, value="&", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x26, value="&", char_state=CState.INIT),
}

# CState.ASCII_0x26_0x3E
COMMON_ASCII_0x26_0x3E_MAP = {
    ">": op.MoveFixedSetCharState(end_as=TType.ASCII_0x26_0x3E_0x3E, value="&>>", char_state=CState.INIT),
    DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x26_0x3E, value="&>", char_state=CState.INIT),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x26_0x3E, value="&>", char_state=CState.INIT),
}

# CState.ASCII_0x5B
COMMON_ASCII_0x5B_MAP = {
    "[": op.MoveFixedSetCharState(end_as=TType.ASCII_0x5B_0x5B, value="[[", char_state=CState.INIT),
    DEFAULT: op.AddSetCharState(char="[", char_state=CState.NORMAL),
    ms_parser.lexical.END: op.AddSetCharState(char="[", char_state=CState.NORMAL),
}

# CState.ASCII_0x5D
COMMON_ASCII_0x5D_MAP = {
    "]": op.MoveFixedSetCharState(end_as=TType.ASCII_0x5D_0x5D, value="]]", char_state=CState.INIT),
    DEFAULT: op.AddSetCharState(char="]", char_state=CState.NORMAL),
    ms_parser.lexical.END: op.AddSetCharState(char="]", char_state=CState.NORMAL),
}

# CState.NUMBER
COMMON_NUMBER_MAP = {
    "<": op.ShiftSetCharState(char_state=CState.NUMBER_0x3C),
    ">": op.ShiftSetCharState(char_state=CState.NUMBER_0x3E),
    DEFAULT: op.NothingSetCharState(char_state=CState.NORMAL),
    ms_parser.lexical.END: op.NothingSetCharState(char_state=CState.NORMAL),
}

# CState.NUMBER_0x3C
COMMON_NUMBER_0x3C_MAP = {
    "<": op.ShiftSetCharState(char_state=CState.NUMBER_0x3C_0x3C),
    "&": op.MoveReduceSetCharState(end_as=TType.NUMBER_0x3C_0x26, char_state=CState.INIT),  # n<&
    ">": op.MoveReduceSetCharState(end_as=TType.NUMBER_0x3C_0x3E, char_state=CState.INIT),  # n<>
    DEFAULT: op.ReduceSetCharState(end_as=TType.NUMBER_0x3C, char_state=CState.INIT),  # n<
    ms_parser.lexical.END: op.ReduceSetCharState(end_as=TType.NUMBER_0x3C, char_state=CState.INIT),  # n<
}

# CState.NUMBER_0x3C_0x3C
COMMON_NUMBER_0x3C_0x3C_MAP = {
    "-": op.MoveReduceSetCharState(end_as=TType.NUMBER_0x3C_0x3C_0x2D, char_state=CState.INIT),  # n<<-
    "<": op.MoveReduceSetCharState(end_as=TType.NUMBER_0x3C_0x3C_0x3C, char_state=CState.INIT),  # n<<<
    DEFAULT: op.ReduceSetCharState(end_as=TType.NUMBER_0x3C_0x3C, char_state=CState.INIT),  # n<<
    ms_parser.lexical.END: op.ReduceSetCharState(end_as=TType.NUMBER_0x3C_0x3C, char_state=CState.INIT),  # n<<
}

# CState.NUMBER_0x3E
COMMON_NUMBER_0x3E_MAP = {
    "&": op.MoveReduceSetCharState(end_as=TType.NUMBER_0x3E_0x26, char_state=CState.INIT),  # n>&
    ">": op.MoveReduceSetCharState(end_as=TType.NUMBER_0x3E_0x3E, char_state=CState.INIT),  # n>>
    "|": op.MoveReduceSetCharState(end_as=TType.NUMBER_0x3E_0x7C, char_state=CState.INIT),  # n>|
    DEFAULT: op.ReduceSetCharState(end_as=TType.NUMBER_0x3E, char_state=CState.INIT),  # n>
    ms_parser.lexical.END: op.ReduceSetCharState(end_as=TType.NUMBER_0x3E, char_state=CState.INIT),  # n>
}

# CState.ESCAPE
COMMON_ESCAPE_MAP = {
    "\n": op.SkipSetCharState(char_state=CState.INIT),
    DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
    ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.IDENT, value="\\", char_state=CState.INIT),
}

# 行为映射表设置表（用于设置配置信息，输入参数允许是一个不可变集合）
FSM_OPERATION_MAP_SOURCE: Dict[Tuple[NState, CState], Dict[str, op.Operator]] = {
    # ------------------------------ 初始状态 ------------------------------
    (NState.NORMAL, CState.INIT): COMMON_INIT_MAP,
    (NState.NORMAL, CState.NORMAL): COMMON_NORMAL_MAP,
    (NState.NORMAL, CState.DOLLAR): COMMON_DOLLAR_MAP,
    (NState.NORMAL, CState.DOLLAR_0x28): COMMON_DOLLAR_0x28_MAP,
    (NState.NORMAL, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.NORMAL, CState.ASCII_0x29): COMMON_ASCII_0x29_MAP,
    (NState.NORMAL, CState.ASCII_0x3C): COMMON_ASCII_0x3C_MAP,
    (NState.NORMAL, CState.ASCII_0x3C_0x3C): COMMON_ASCII_0x3C_0x3C_MAP,
    (NState.NORMAL, CState.ASCII_0x3E): COMMON_ASCII_0x3E_MAP,
    (NState.NORMAL, CState.ASCII_0x26): COMMON_ASCII_0x26_MAP,
    (NState.NORMAL, CState.ASCII_0x26_0x3E): COMMON_ASCII_0x26_0x3E_MAP,
    (NState.NORMAL, CState.ASCII_0x7C): COMMON_ASCII_0x7C_MAP,
    (NState.NORMAL, CState.ASCII_0x5B): COMMON_ASCII_0x5B_MAP,
    (NState.NORMAL, CState.ASCII_0x5D): COMMON_ASCII_0x5D_MAP,
    (NState.NORMAL, CState.ASCII_0x7B): COMMON_ASCII_0x7B_MAP,
    (NState.NORMAL, CState.NUMBER): COMMON_NUMBER_MAP,
    (NState.NORMAL, CState.NUMBER_0x3C): COMMON_NUMBER_0x3C_MAP,
    (NState.NORMAL, CState.NUMBER_0x3C_0x3C): COMMON_NUMBER_0x3C_0x3C_MAP,
    (NState.NORMAL, CState.NUMBER_0x3E): COMMON_NUMBER_0x3E_MAP,
    (NState.NORMAL, CState.ESCAPE): COMMON_ESCAPE_MAP,
    (NState.NORMAL, CState.COMMENT): COMMON_COMMENT_MAP,
    (NState.NORMAL, CState.ASCII_0x3D): COMMON_ASCII_0x3D_MAP,

    # ------------------------------ 单引号字符串 ------------------------------
    (NState.IN_SINGLE_QUOTE, CState.INIT): {
        "'": op.MoveFixedPopState(end_as=TType.SINGLE_QUOTE, value="'"),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_SINGLE_QUOTE, CState.NORMAL): {
        "'": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },

    # ------------------------------ ANSI-C 扩展字符串 ------------------------------
    (NState.IN_DOLLAR_SINGLE_QUOTE, CState.INIT): {
        "'": op.MoveFixedPopState(end_as=TType.SINGLE_QUOTE, value="'"),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_DOLLAR_SINGLE_QUOTE, CState.NORMAL): {
        "'": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_DOLLAR_SINGLE_QUOTE, CState.ESCAPE): {
        AFTER_ANSI_C_ESCAPE: op.AddAndShiftSetCharState(char="\\", char_state=CState.NORMAL),  # 解析逻辑在执行层处理
        DEFAULT: op.AddSetCharState(char="\\", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },

    # ------------------------------ 双引号字符串 ------------------------------
    (NState.IN_DOUBLE_QUOTE, CState.INIT): {
        "\"": op.MoveFixedPopState(end_as=TType.DOUBLE_QUOTE_CLOSE, value="\""),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        "`": op.MoveFixedAppendState(end_as=TType.BACK_QUOTE_OPEN, value="`", nest_state=NState.IN_BACK_QUOTE),
        "$": op.SkipSetCharState(char_state=CState.DOLLAR),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_DOUBLE_QUOTE, CState.NORMAL): {
        "\"": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "`": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "$": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },
    # 在双引号字符串中，\ 之后只有跟着 $、`、"、\ 或 \n 时才作为转义符使用
    (NState.IN_DOUBLE_QUOTE, CState.ESCAPE): {
        frozenset({"$", "`", "\"", "\\", "\n"}): op.ShiftSetCharState(char_state=CState.INIT),
        DEFAULT: op.AddSetCharState(char="\\", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_DOUBLE_QUOTE, CState.DOLLAR): update_dict(COMMON_DOLLAR_MAP, {
        "'": op.AddSetCharState(char="$", char_state=CState.NORMAL)
    }),
    (NState.IN_DOUBLE_QUOTE, CState.DOLLAR_0x28): COMMON_DOLLAR_0x28_MAP,

    # ------------------------------ 本地化翻译字符串 ------------------------------
    (NState.IN_DOLLAR_DOUBLE_QUOTE, CState.INIT): {
        "\"": op.MoveFixedPopState(end_as=TType.DOUBLE_QUOTE_CLOSE, value="\""),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        "`": op.MoveFixedAppendState(end_as=TType.BACK_QUOTE_OPEN, value="`", nest_state=NState.IN_BACK_QUOTE),
        "$": op.SkipSetCharState(char_state=CState.DOLLAR),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_DOLLAR_DOUBLE_QUOTE, CState.NORMAL): {
        "\"": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "`": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "$": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },
    # 在双引号字符串中，\ 之后只有跟着 $、`、"、\ 或 \n 时才作为转义符使用
    (NState.IN_DOLLAR_DOUBLE_QUOTE, CState.ESCAPE): {
        frozenset({"$", "`", "\"", "\\", "\n"}): op.ShiftSetCharState(char_state=CState.INIT),
        DEFAULT: op.AddSetCharState(char="\\", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_DOLLAR_DOUBLE_QUOTE, CState.DOLLAR): COMMON_DOLLAR_MAP,
    (NState.IN_DOLLAR_DOUBLE_QUOTE, CState.DOLLAR_0x28): COMMON_DOLLAR_0x28_MAP,

    # ------------------------------ 大括号扩展 ------------------------------
    (NState.IN_BRACE, CState.INIT): {
        "}": op.MoveFixedPopState(end_as=TType.ASCII_0x7D, value="}"),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        ",": op.MoveFixed(end_as=TType.ASCII_0x2C, value=","),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE, CState.NORMAL): {
        frozenset({"}", ","}): op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE, CState.ESCAPE): {
        frozenset({"}", ","}): op.ShiftSetCharState(char_state=CState.INIT),
        DEFAULT: op.AddSetCharState(char="\\", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },

    # ------------------------------ 带大括号的参数扩展 ------------------------------
    (NState.IN_BRACE_PARAM, CState.INIT): {
        "}": op.MoveFixedPopState(end_as=TType.ASCII_0x7D, value="}"),
        "!": op.MoveFixed(end_as=TType.ASCII_0x21, value="!"),
        ",": op.SkipSetCharState(char_state=CState.ASCII_0x2C),
        "@": op.MoveFixed(end_as=TType.ASCII_0x40, value="@"),
        "*": op.MoveFixed(end_as=TType.ASCII_0x2A, value="*"),
        ":": op.SkipSetCharState(char_state=CState.COLON),
        "#": op.SkipSetCharState(char_state=CState.ASCII_0x23),
        "%": op.SkipSetCharState(char_state=CState.ASCII_0x25),
        "[": op.MoveFixedAppendState(end_as=TType.ASCII_0x5B, value="[", nest_state=NState.IN_SPLIT),
        "/": op.MoveFixed(end_as=TType.ASCII_0x2F, value="/"),
        "^": op.SkipSetCharState(char_state=CState.ASCII_0x5E),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM, CState.NORMAL): {
        "}": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        ",": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "@": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "*": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        ":": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "#": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "%": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "[": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "/": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "^": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        "\\": op.SkipSetCharState(char_state=CState.ESCAPE),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM, CState.COLON): {
        "+": op.MoveFixedSetCharState(end_as=TType.COLON_0x2B, value=":+", char_state=CState.NORMAL),
        "-": op.MoveFixedSetCharState(end_as=TType.COLON_0x2D, value=":-", char_state=CState.NORMAL),
        "=": op.MoveFixedSetCharState(end_as=TType.COLON_0x3D, value=":=", char_state=CState.NORMAL),
        "?": op.MoveFixedSetCharState(end_as=TType.COLON_0x3F, value=":?", char_state=CState.NORMAL),
        DEFAULT: op.FixedSetState(end_as=TType.ASCII_0x3A, value=":", nest_state=NState.IN_BRACE_PARAM_AFTER_COLON,
                                  char_state=CState.INIT),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM, CState.ASCII_0x23): {
        "#": op.MoveFixedSetCharState(end_as=TType.ASCII_0x23_0x23, value="##", char_state=CState.NORMAL),
        DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x23, value="#", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM, CState.ASCII_0x25): {
        "%": op.MoveFixedSetCharState(end_as=TType.ASCII_0x25_0x25, value="%%", char_state=CState.NORMAL),
        DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x25, value="%", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM, CState.ASCII_0x2C): {
        ",": op.MoveFixedSetCharState(end_as=TType.ASCII_0x2C_0x2C, value=",,", char_state=CState.NORMAL),
        DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x2C, value=",", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM, CState.ASCII_0x5E): {
        "^": op.MoveFixedSetCharState(end_as=TType.ASCII_0x5E_0x5E, value="^^", char_state=CState.NORMAL),
        DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x5E, value="^", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM, CState.ESCAPE): {
        frozenset({"}", ","}): op.ShiftSetCharState(char_state=CState.INIT),
        DEFAULT: op.AddSetCharState(char="\\", char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM_AFTER_COLON, CState.INIT): {
        "}": op.MoveFixedPopState(end_as=TType.ASCII_0x7D, value="}"),
        ":": op.SkipSetCharState(char_state=CState.COLON),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM_AFTER_COLON, CState.NORMAL): {
        "}": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        ":": op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_BRACE_PARAM_AFTER_COLON, CState.COLON): {
        DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x3A, value=":", char_state=CState.INIT),
        ms_parser.lexical.END: op.Error()
    },

    # ------------------------------ 参数扩展 ------------------------------
    (NState.IN_PARAM, CState.INIT): {
        CHARSET_PARAM: op.ShiftSetCharState(char_state=CState.NORMAL),
        DEFAULT: op.NothingPopState(),
        ms_parser.lexical.END: op.NothingPopState()
    },
    (NState.IN_PARAM, CState.NORMAL): {
        CHARSET_PARAM: op.Shift(),
        DEFAULT: op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        ms_parser.lexical.END: op.ReducePopState(end_as=TType.IDENT)
    },

    # ------------------------------ 数组切片 ------------------------------
    (NState.IN_SPLIT, CState.INIT): {
        "]": op.MoveFixedPopState(end_as=TType.ASCII_0x5D, value="]"),
        "@": op.MoveFixed(end_as=TType.ASCII_0x40, value="@"),
        "*": op.MoveFixed(end_as=TType.ASCII_0x2A, value="*"),
        DEFAULT: op.ShiftSetCharState(char_state=CState.NORMAL),
        ms_parser.lexical.END: op.Error()
    },
    (NState.IN_SPLIT, CState.NORMAL): {
        frozenset({"]", "@", "*"}): op.ReduceSetCharState(end_as=TType.IDENT, char_state=CState.INIT),
        DEFAULT: op.Shift(),
        ms_parser.lexical.END: op.Error()
    },

    # ------------------------------ $(abc) 格式的命令替换 ------------------------------
    (NState.IN_DOLLAR_CURVE, CState.INIT): update_dict(COMMON_INIT_MAP, {
        ")": op.MoveFixedPopState(end_as=TType.ASCII_0x29, value=")")
    }),
    (NState.IN_DOLLAR_CURVE, CState.NORMAL): COMMON_NORMAL_MAP,
    (NState.IN_DOLLAR_CURVE, CState.DOLLAR): COMMON_DOLLAR_MAP,
    (NState.IN_DOLLAR_CURVE, CState.DOLLAR_0x28): COMMON_DOLLAR_0x28_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x3D): COMMON_ASCII_0x3D_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x7B): COMMON_ASCII_0x7B_MAP,
    (NState.IN_DOLLAR_CURVE, CState.COMMENT): COMMON_COMMENT_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x3C): COMMON_ASCII_0x3C_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x3C_0x3C): COMMON_ASCII_0x3C_0x3C_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x3E): COMMON_ASCII_0x3E_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x7C): COMMON_ASCII_0x7C_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x26): COMMON_ASCII_0x26_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x26_0x3E): COMMON_ASCII_0x26_0x3E_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x5B): COMMON_ASCII_0x5B_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ASCII_0x5D): COMMON_ASCII_0x5D_MAP,
    (NState.IN_DOLLAR_CURVE, CState.NUMBER): COMMON_NUMBER_MAP,
    (NState.IN_DOLLAR_CURVE, CState.NUMBER_0x3C): COMMON_NUMBER_0x3C_MAP,
    (NState.IN_DOLLAR_CURVE, CState.NUMBER_0x3C_0x3C): COMMON_NUMBER_0x3C_0x3C_MAP,
    (NState.IN_DOLLAR_CURVE, CState.NUMBER_0x3E): COMMON_NUMBER_0x3E_MAP,
    (NState.IN_DOLLAR_CURVE, CState.ESCAPE): COMMON_ESCAPE_MAP,

    # ------------------------------ `abc` 格式的命令替换 ------------------------------
    (NState.IN_BACK_QUOTE, CState.INIT): update_dict(COMMON_INIT_MAP, {
        "`": op.MoveFixedPopState(end_as=TType.BACK_QUOTE_CLOSE, value="`")
    }),
    (NState.IN_BACK_QUOTE, CState.NORMAL): COMMON_NORMAL_MAP,
    (NState.IN_BACK_QUOTE, CState.DOLLAR): COMMON_DOLLAR_MAP,
    (NState.IN_BACK_QUOTE, CState.DOLLAR_0x28): COMMON_DOLLAR_0x28_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x29): COMMON_ASCII_0x29_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x3D): COMMON_ASCII_0x3D_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x7B): COMMON_ASCII_0x7B_MAP,
    (NState.IN_BACK_QUOTE, CState.COMMENT): COMMON_COMMENT_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x3C): COMMON_ASCII_0x3C_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x3C_0x3C): COMMON_ASCII_0x3C_0x3C_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x3E): COMMON_ASCII_0x3E_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x7C): COMMON_ASCII_0x7C_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x26): COMMON_ASCII_0x26_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x26_0x3E): COMMON_ASCII_0x26_0x3E_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x5B): COMMON_ASCII_0x5B_MAP,
    (NState.IN_BACK_QUOTE, CState.ASCII_0x5D): COMMON_ASCII_0x5D_MAP,
    (NState.IN_BACK_QUOTE, CState.NUMBER): COMMON_NUMBER_MAP,
    (NState.IN_BACK_QUOTE, CState.NUMBER_0x3C): COMMON_NUMBER_0x3C_MAP,
    (NState.IN_BACK_QUOTE, CState.NUMBER_0x3C_0x3C): COMMON_NUMBER_0x3C_0x3C_MAP,
    (NState.IN_BACK_QUOTE, CState.NUMBER_0x3E): COMMON_NUMBER_0x3E_MAP,
    (NState.IN_BACK_QUOTE, CState.ESCAPE): COMMON_ESCAPE_MAP,

    # ------------------------------ { abc } 命令组 ------------------------------
    (NState.IN_GROUPING_BRACE, CState.INIT): update_dict(COMMON_INIT_MAP, {
        "}": op.MoveFixedPopState(end_as=TType.KEYWORD_BRACE_CLOSE, value="}"),
    }),
    (NState.IN_GROUPING_BRACE, CState.NORMAL): update_dict(COMMON_NORMAL_MAP, {
        "}": op.ReduceSetCharStateMaybeKeyword(char_state=CState.INIT),
    }),
    (NState.IN_GROUPING_BRACE, CState.DOLLAR): COMMON_DOLLAR_MAP,
    (NState.IN_GROUPING_BRACE, CState.DOLLAR_0x28): COMMON_DOLLAR_0x28_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x29): COMMON_ASCII_0x29_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x3D): COMMON_ASCII_0x3D_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x7B): COMMON_ASCII_0x7B_MAP,
    (NState.IN_GROUPING_BRACE, CState.COMMENT): COMMON_COMMENT_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x3C): COMMON_ASCII_0x3C_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x3C_0x3C): COMMON_ASCII_0x3C_0x3C_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x3E): COMMON_ASCII_0x3E_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x7C): COMMON_ASCII_0x7C_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x26): COMMON_ASCII_0x26_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x26_0x3E): COMMON_ASCII_0x26_0x3E_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x5B): COMMON_ASCII_0x5B_MAP,
    (NState.IN_GROUPING_BRACE, CState.ASCII_0x5D): COMMON_ASCII_0x5D_MAP,
    (NState.IN_GROUPING_BRACE, CState.NUMBER): COMMON_NUMBER_MAP,
    (NState.IN_GROUPING_BRACE, CState.NUMBER_0x3C): COMMON_NUMBER_0x3C_MAP,
    (NState.IN_GROUPING_BRACE, CState.NUMBER_0x3C_0x3C): COMMON_NUMBER_0x3C_0x3C_MAP,
    (NState.IN_GROUPING_BRACE, CState.NUMBER_0x3E): COMMON_NUMBER_0x3E_MAP,
    (NState.IN_GROUPING_BRACE, CState.ESCAPE): COMMON_ESCAPE_MAP,

    # ------------------------------ $(( abc )) 或 (( )) ------------------------------
    (NState.IN_ARITHMETIC_EXPANSION, CState.INIT): COMMON_INIT_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.NORMAL): COMMON_NORMAL_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.DOLLAR): COMMON_DOLLAR_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.DOLLAR_0x28): COMMON_DOLLAR_0x28_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x29): update_dict(COMMON_ASCII_0x29_MAP, {
        ")": op.MoveFixedPopState(end_as=TType.ASCII_0x29_0x29, value="))"),
        DEFAULT: op.FixedSetCharState(end_as=TType.ASCII_0x29, value=")", char_state=CState.INIT),
        ms_parser.lexical.END: op.FixedSetCharState(end_as=TType.ASCII_0x29, value=")", char_state=CState.INIT),
    }),
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x3D): COMMON_ASCII_0x3D_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x7B): COMMON_ASCII_0x7B_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.COMMENT): COMMON_COMMENT_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x28): COMMON_ASCII_0x28_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x3C): COMMON_ASCII_0x3C_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x3C_0x3C): COMMON_ASCII_0x3C_0x3C_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x3E): COMMON_ASCII_0x3E_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x7C): COMMON_ASCII_0x7C_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x26): COMMON_ASCII_0x26_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x26_0x3E): COMMON_ASCII_0x26_0x3E_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x5B): COMMON_ASCII_0x5B_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ASCII_0x5D): COMMON_ASCII_0x5D_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.NUMBER): COMMON_NUMBER_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.NUMBER_0x3C): COMMON_NUMBER_0x3C_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.NUMBER_0x3C_0x3C): COMMON_NUMBER_0x3C_0x3C_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.NUMBER_0x3E): COMMON_NUMBER_0x3E_MAP,
    (NState.IN_ARITHMETIC_EXPANSION, CState.ESCAPE): COMMON_ESCAPE_MAP,
}

# 状态行为映射表（用于用时行为映射信息，输入参数必须是一个字符）
FSM_OPERATION_MAP: Dict[Tuple[NState, CState, str], op.Operator] = {}
FSM_OPERATION_MAP_DEFAULT: Dict[Tuple[NState, CState], op.Operator] = {}
for (nest_state, char_state), operation_map in FSM_OPERATION_MAP_SOURCE.items():
    # 遍历并添加定义的字符到行为映射表中
    for ch_or_set, fsm_operation in operation_map.items():
        if ch_or_set is DEFAULT:
            FSM_OPERATION_MAP_DEFAULT[(nest_state, char_state)] = fsm_operation
        elif isinstance(ch_or_set, str):
            FSM_OPERATION_MAP[(nest_state, char_state, ch_or_set)] = fsm_operation
        elif isinstance(ch_or_set, frozenset):
            for ch in ch_or_set:
                FSM_OPERATION_MAP[(nest_state, char_state, ch)] = fsm_operation
        else:
            raise KeyError("非法的行为映射表设置表")

    # 将 ASCII 编码 20 - 7E 之间的字符添加到行为映射表中（从而令第一次查询的命中率提高，避免第二次查询）
    for dec in range(32, 127):
        ch = chr(dec)
        if (nest_state, char_state, ch) not in FSM_OPERATION_MAP:
            FSM_OPERATION_MAP[(nest_state, char_state, ch)] = FSM_OPERATION_MAP_DEFAULT[(nest_state, char_state)]
