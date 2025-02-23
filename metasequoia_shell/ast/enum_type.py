"""
Shell 抽象语法树中的枚举类
"""

import enum

__all__ = [
    "SubstitutionType",
    "GroupingType",
    "RedirectionType",
    "PipeType",
    "CommandRelationType",
    "CommandEndType",
]


class SubstitutionType(enum.IntEnum):
    """命令替换类型（用于抽象语法树的命令替换节点）"""

    # $(abc)
    CURVE = 1

    # `abc`
    BACK_QUOTE = 2


class GroupingType(enum.IntEnum):
    """命令组类型（用于抽象语法树的命令组节点）"""

    # ( command_list )  -- 在子 shell 中执行命令组中的命令
    SUB_PROCESS = 1

    # { command_list }  -- 在当上下文中执行命令组中的命令
    CONTEXT = 2


class RedirectionType(enum.Enum):
    """重定向类型的枚举类（用于抽象语法树的重定向子句）"""

    # n<  -- 重定向文件描述符 n 的输入
    NUMBER_0x3C = (True, "<")  # 【重定向输入】n<

    # n<&  -- 复制输入文件描述符 n
    NUMBER_0x3C_0x26 = (True, "<&")

    # n<<  -- Here Documents
    NUMBER_0x3C_0x3C = (True, "<<")

    # n<>  -- 打开文件以支持读写
    NUMBER_0x3C_0x3E = (True, "<>")

    # n<<- -- Here Documents
    NUMBER_0x3C_0x3C_0x2D = (True, "<<-")

    # n<<< -- Here Strings
    NUMBER_0x3C_0x3C_0x3C = (True, "<<<")

    # n>  -- 重定向文件描述符 n 的输出（若文件已存在且 noclobber 选项启用则重定向失败）
    NUMBER_0x3E = (True, ">")

    # n>|  -- 重定向文件描述符 n 的输出（无论文件是否存在均可重定向）
    NUMBER_0x3E_0x7C = (True, ">|")

    # n>>  -- 追加重定向文件描述符 n 的输出
    NUMBER_0x3E_0x3E = (True, ">>")

    # n>&  -- 复制输出文件描述符 n
    NUMBER_0x3E_0x26 = (True, ">&")

    # <  -- 重定向标准输入
    ASCII_0x3C = (False, "<")

    # >  -- 重定向标准输出（若文件已存在且 noclobber 选项启用则重定向失败）
    ASCII_0x3E = (False, ">")

    # >|  -- 重定向标准输出（无论文件是否存在均可重定向）
    ASCII_0x3E_0x7C = (False, ">|")

    # >>  -- 追加重定向标准输出
    ASCII_0x3E_0x3E = (False, ">>")

    # n>&  -- 重定向标准输出和标准错误输出
    ASCII_0x26_0x3E = (False, "&>")

    # >&  -- 复制标准输出
    ASCII_0x3E_0x26 = (False, ">&")

    # &>>  -- 追加重定向标准输出和标准错误输出
    ASCII_0x26_0x3E_0x3E = (False, "&>>")

    # <<  -- Here Documents
    ASCII_0x3C_0x3C = (False, "<<")

    # <<-  -- Here Documents
    ASCII_0x3C_0x3C_0x2D = (False, "<<-")

    # <<<  -- Here Strings
    ASCII_0x3C_0x3C_0x3C = (False, "<<<")

    # <&  -- 复制标准输入
    ASCII_0x3C_0x26 = (False, "<&")

    # <>  -- 打开文件以支持读写
    ASCII_0x3C_0x3E = (False, "<>")


class PipeType(enum.Enum):
    """管道类型（用于抽象语法树的管道子句）"""

    # |  -- 将前一个命令的标准输出作为下一个命令的标准输入
    ASCII_0x7C = "|"

    # |&  -- 将前一个命令的标准输出和标准错误作为下一个命令的标准输出
    ASCII_0x7C_0x26 = "|&"


class CommandRelationType(enum.Enum):
    """命令的关系符（用于抽象语法树中的单个关系、命令组合的子句节点）"""

    # command1 && command2  -- 当且仅当 command1 的退出状态为 0 时，才会允许 command2
    ASCII_0x26_0x26 = "&&"

    # command1 || command2  -- 当且仅当 command1 的退出状态不为 0 时，才会允许 command2
    ASCII_0x7C_0x7C = "||"


class CommandEndType(enum.Enum):
    """命令的结束符（用于抽象语法树的命令列表节点）"""

    # 换行符  -- 顺序执行
    ASCII_0x0A = "\n"

    # &  -- 在子 Shell 中异步执行
    ASCII_0x26 = "&"

    # ;  -- 顺序执行
    ASCII_0x3B = ";"

    # 没有显式地结束符  -- 命令列表末尾的命令
    DEFAULT = ""
