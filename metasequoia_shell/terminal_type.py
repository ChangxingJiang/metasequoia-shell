"""
Shell 解析器：终结符类型的枚举类
"""

import enum

import metasequoia_parser as ms_parser


@enum.unique
class ShellTerminalType(ms_parser.symbol.TerminalType):
    """终结符名称到 ID 的映射"""

    END = 0

    IDENT = enum.auto()  # 普通字符串

    # ------------------------------ 单字符符号 ------------------------------

    ASCII_0x0A = enum.auto()  # 【0x0A】换行符 \n
    SPACE = enum.auto()  # 【0x09】【0x20】空格和水平制表符（`\t`）
    ASCII_0x21 = enum.auto()  # 【0x21】!
    DOUBLE_QUOTE_OPEN = enum.auto()  # 【0x22】双引号 "
    DOUBLE_QUOTE_CLOSE = enum.auto()  # 【0x22】双引号 "
    ASCII_0x23 = enum.auto()  # 【0x23】井号 #
    DOLLAR = enum.auto()  # 【0x24】$
    ASCII_0x25 = enum.auto()  # 【0x25】百分号 %
    ASCII_0x26 = enum.auto()  # &  -- 命令列表
    SINGLE_QUOTE = enum.auto()  # 【0x27】'
    ASCII_0x28 = enum.auto()  # (  -- 命令组
    ASCII_0x29 = enum.auto()  # )  -- 命令组
    ASCII_0x2A = enum.auto()  # 【0x2A】星号 *
    ASCII_0x2C = enum.auto()  # 【0x2C】英文半角逗号 ,
    ASCII_0x2D = enum.auto()  # -  -- 重定向
    ASCII_0x2F = enum.auto()  # 【0x2F】斜杠 /
    ASCII_0x3A = enum.auto()  # 【0X3A】冒号 :
    ASCII_0x3B = enum.auto()  # 【0x3B】分号 ;
    ASCII_0x3C = enum.auto()  # <  -- 重定向
    ASCII_0x3D = enum.auto()  # 【0x3D】等于号（赋值语句） =
    ASCII_0x3E = enum.auto()  # >  -- 重定向
    ASCII_0x40 = enum.auto()  # 【0x40】电子邮件符号 @
    ASCII_0x5B = enum.auto()  # [  -- 命令组
    ASCII_0x5D = enum.auto()  # ]  -- 命令组
    ASCII_0x5E = enum.auto()  # 【0x5E】脱字符 ^
    BACK_QUOTE_OPEN = enum.auto()  # 【0x60】反引号（左）
    BACK_QUOTE_CLOSE = enum.auto()  # 【0x60】反引号（右）
    ASCII_0x7B = enum.auto()  # {  -- 大括号扩展
    KEYWORD_BRACE_OPEN = enum.auto()  # 【0x7B】命令组中的开大括号，要求之后必须是空格（实际上是关键字）
    ASCII_0x7C = enum.auto()  # |  -- 管道
    ASCII_0x7D = enum.auto()  # }  -- 大括号扩展
    KEYWORD_BRACE_CLOSE = enum.auto()  # 【0x7D】命令组中的闭大括号，要求之前必须是空格（实际上是关键字）
    SLIDE = enum.auto()  # 【0x7E】波浪号（波浪线扩展） ~

    # ------------------------------ 特殊参数与位置参数 ------------------------------

    # 特殊参数 I
    DOLLAR_0 = enum.auto()  # $0  -- 特殊参数

    # 位置参数：当由超过一个数字组成的位置参数时，它必须被包含在大括号中展开，例如 ${10}
    DOLLAR_1 = enum.auto()  # $1  -- 位置参数
    DOLLAR_2 = enum.auto()  # $2  -- 位置参数
    DOLLAR_3 = enum.auto()  # $3  -- 位置参数
    DOLLAR_4 = enum.auto()  # $4  -- 位置参数
    DOLLAR_5 = enum.auto()  # $5  -- 位置参数
    DOLLAR_6 = enum.auto()  # $6  -- 位置参数
    DOLLAR_7 = enum.auto()  # $7  -- 位置参数
    DOLLAR_8 = enum.auto()  # $8  -- 位置参数
    DOLLAR_9 = enum.auto()  # $9  -- 位置参数

    # 特殊参数 II
    DOLLAR_0x21 = enum.auto()  # $!  -- 特殊参数
    DOLLAR_0x23 = enum.auto()  # $#  -- 特殊参数
    DOLLAR_0x2A = enum.auto()  # $*  -- 特殊参数
    DOLLAR_0x2D = enum.auto()  # $-  -- 特殊参数
    DOLLAR_0x3F = enum.auto()  # $?  -- 特殊参数
    DOLLAR_0x40 = enum.auto()  # $@  -- 特殊参数

    # 特殊参数 III
    DOLLAR_DOLLAR = enum.auto()  # $$  -- 特殊参数

    # ------------------------------ 参数扩展中符号 ------------------------------

    COLON_0x2D = enum.auto()  # :-
    COLON_0x3D = enum.auto()  # :=
    COLON_0x3F = enum.auto()  # :?
    COLON_0x2B = enum.auto()  # :+
    ASCII_0x23_0x23 = enum.auto()  # ##
    ASCII_0x25_0x25 = enum.auto()  # %%
    ASCII_0x2C_0x2C = enum.auto()  # ,,
    ASCII_0x5E_0x5E = enum.auto()  # ^^

    # ------------------------------ 扩展类符号 ------------------------------

    # 参数拓展
    DOLLAR_0x7B = enum.auto()  # ${  -- 参数扩展

    # 命令替换
    DOLLAR_0x28 = enum.auto()  # $(  -- 命令替换

    # 算术表达式和算术扩展
    ASCII_0x28_0x28 = enum.auto()  # ((  -- 算术表达式
    ASCII_0x29_0x29 = enum.auto()  # ))  -- 算术表达式
    DOLLAR_0x28_0x28 = enum.auto()  # $((  -- 算术扩展

    # 条件表达式
    ASCII_0x5B_0x5B = enum.auto()  # [[  -- 条件表达式
    ASCII_0x5D_0x5D = enum.auto()  # ]]  -- 条件表达式

    # 进程替换
    ASCII_0x3C_0x28 = enum.auto()  # <(  -- 进程替换
    ASCII_0x3E_0x28 = enum.auto()  # >(  -- 进程替换

    # ASCI-C 扩展字符串
    DOLLAR_SINGLE_QUOTE = enum.auto()  # $'  -- ASCI-C 扩展字符串

    # 本地化翻译字符串
    DOLLAR_DOUBLE_QUOTE = enum.auto()  # $"  -- 本地化翻译字符串

    # ------------------------------ 管道、重定向和命令列表 ------------------------------

    # 管道
    ASCII_0x7C_0x26 = enum.auto()  # |&  -- 管道

    # 命令列表
    ASCII_0x26_0x26 = enum.auto()  # &&  -- 命令列表
    ASCII_0x7C_0x7C = enum.auto()  # ||  -- 命令列表

    # 重定向
    NUMBER_0x3C = enum.auto()  # 【重定向输入】n<
    NUMBER_0x3C_0x26 = enum.auto()  # 【重定向输入】n<&
    NUMBER_0x3C_0x3C = enum.auto()  # 【重定向输入】n<<
    NUMBER_0x3C_0x3E = enum.auto()  # 【重定向输入】n<>
    NUMBER_0x3C_0x3C_0x2D = enum.auto()  # 【重定向输入】n<<-
    NUMBER_0x3C_0x3C_0x3C = enum.auto()  # 【重定向输入】n<<<
    NUMBER_0x3E = enum.auto()  # 【重定向输出】n>
    NUMBER_0x3E_0x7C = enum.auto()  # 【重定向输出】n>|
    NUMBER_0x3E_0x3E = enum.auto()  # 【追加重定向输出】n>>
    NUMBER_0x3E_0x26 = enum.auto()  # 【追加重定向输出】n>&
    ASCII_0x3E_0x7C = enum.auto()  # >|  -- 重定向
    ASCII_0x3E_0x3E = enum.auto()  # >>  -- 重定向
    ASCII_0x26_0x3E = enum.auto()  # &>  -- 重定向
    ASCII_0x3E_0x26 = enum.auto()  # >&  -- 重定向
    ASCII_0x26_0x3E_0x3E = enum.auto()  # &>>  -- 重定向
    ASCII_0x3C_0x3C = enum.auto()  # <<  -- 重定向
    ASCII_0x3C_0x3C_0x2D = enum.auto()  # <<-  -- 重定向
    ASCII_0x3C_0x3C_0x3C = enum.auto()  # <<<  -- 重定向
    ASCII_0x3C_0x26 = enum.auto()  # <&  -- 重定向
    ASCII_0x3C_0x3E = enum.auto()  # <>  -- 重定向

    # ------------------------------ 保留字 ------------------------------
    # 其他保留字：{、}、[[、]]、!

    IF = enum.auto()
    THEN = enum.auto()
    ELIF = enum.auto()
    ELSE = enum.auto()
    FI = enum.auto()
    TIME = enum.auto()
    FOR = enum.auto()
    IN = enum.auto()
    UNTIL = enum.auto()
    WHILE = enum.auto()
    DO = enum.auto()
    DONE = enum.auto()
    CASE = enum.auto()
    ESAC = enum.auto()
    COPROC = enum.auto()
    SELECT = enum.auto()
    FUNCTION = enum.auto()


KEYWORD_HASH = {
    "IF": ShellTerminalType.IF,
    "THEN": ShellTerminalType.THEN,
    "ELIF": ShellTerminalType.ELIF,
    "ELSE": ShellTerminalType.ELSE,
    "FI": ShellTerminalType.FI,
    "TIME": ShellTerminalType.TIME,
    "FOR": ShellTerminalType.FOR,
    "IN": ShellTerminalType.IN,
    "UNTIL": ShellTerminalType.UNTIL,
    "WHILE": ShellTerminalType.WHILE,
    "DO": ShellTerminalType.DO,
    "DONE": ShellTerminalType.DONE,
    "CASE": ShellTerminalType.CASE,
    "ESAC": ShellTerminalType.ESAC,
    "COPROC": ShellTerminalType.COPROC,
    "SELECT": ShellTerminalType.SELECT,
    "FUNCTION": ShellTerminalType.FUNCTION,
}

# 重定向终结符的集合
REDIRECTION_TERMINAL_SET = {
    ShellTerminalType.NUMBER_0x3C,
    ShellTerminalType.NUMBER_0x3C_0x26,
    ShellTerminalType.NUMBER_0x3C_0x3C,
    ShellTerminalType.NUMBER_0x3C_0x3E,
    ShellTerminalType.NUMBER_0x3C_0x3C_0x2D,
    ShellTerminalType.NUMBER_0x3C_0x3C_0x3C,
    ShellTerminalType.NUMBER_0x3E,
    ShellTerminalType.NUMBER_0x3E_0x7C,
    ShellTerminalType.NUMBER_0x3E_0x3E,
    ShellTerminalType.NUMBER_0x3E_0x26,
    ShellTerminalType.ASCII_0x3C,
    ShellTerminalType.ASCII_0x3E,
    ShellTerminalType.ASCII_0x3E_0x7C,
    ShellTerminalType.ASCII_0x3E_0x3E,
    ShellTerminalType.ASCII_0x26_0x3E,
    ShellTerminalType.ASCII_0x3E_0x26,
    ShellTerminalType.ASCII_0x26_0x3E_0x3E,
    ShellTerminalType.ASCII_0x3C_0x3C,
    ShellTerminalType.ASCII_0x3C_0x3C_0x2D,
    ShellTerminalType.ASCII_0x3C_0x3C_0x3C,
    ShellTerminalType.ASCII_0x3C_0x26,
    ShellTerminalType.ASCII_0x3C_0x3E,
}

# 通道终结符的集合
PIPE_TERMINAL_SET = {
    ShellTerminalType.ASCII_0x7C_0x26,
    ShellTerminalType.ASCII_0x7C
}

# 命令列表关系终结符的集合
RELATION_TERMINAL_SET = {
    ShellTerminalType.ASCII_0x26_0x26,
    ShellTerminalType.ASCII_0x7C_0x7C
}

# 命令结束终结符的集合
END_TERMINAL_SET = {
    ShellTerminalType.ASCII_0x0A,
    ShellTerminalType.ASCII_0x26,
    ShellTerminalType.ASCII_0x3B
}
