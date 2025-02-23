"""Shell 词法解析器状态信息"""

import dataclasses
import enum
from typing import List, Tuple

import metasequoia_parser as ms_parser


@enum.unique  # 保证每个值只有一个名称
class NestState(enum.IntFlag):
    """嵌套状态，是否处于单引号引用、双引号引用、命令替换、算术扩展等嵌套元素内

    | 嵌套状态名称                | 嵌套状态格式             | 嵌套状态含义                                                 |
    | --------------------------- | ------------------------ | ------------------------------------------------------------ |
    | `INIT`                      | -                        | 初始状态（处于脚本开头、命令开头或 Token 开头）              |
    | `IDENT`                     | `abc`                    | 在不处于任何引用、扩展中的普通 Token 中                      |
    | `IN_SINGLE_QUOTE`           | `'abc'`                  | 在单引号引用中                                               |
    | `IN_DOUBLE_QUOTE`           | `"abc"`                  | 在双引号引用中                                               |
    | `IN_DOLLAR_SINGLE_QUOTE`    | `$'abc'`                 | 在 ASCI-C 扩展的单引号引用中                                 |
    | `IN_DOLLAR_DOUBLE_QUOTE`    | `$"abc"`                 | 在本地化翻译的双引号引用中                                   |
    | `IN_DOLLAR_BRACE_EXPANSION` | `${abc}`                 | 在包含大括号的参数扩展中                                     |
    | `IN_DOLLAR_EXPANSION`       | `$abc`                   | 在不包含大括号的参数扩展中                                   |
    | `IN_DOLLAR_CURVE`           | `$(abc)`                 | 在小括号的命令替换中（除等待未被引用的闭小括号外与普通语法相同） |
    | `IN_BACK_QUOTE`             | \\`abc\\`                  | 在反引号的命令替换中（除等待未被引用的反引号外与普通语法相同） |
    | `IN_ARITHMETIC_EXPANSION`   | `$((abc))`               | 在算术扩展中（除等待未被引用的 `))` 外与普通语法相同）       |
    | `IN_PROCESS_SUBSTITUTION`   | `<(list)` 或 `>(list)` | 在过程替换中（除等待未被引用的 `)` 外与普通语法相同）        |
    """

    NORMAL = enum.auto()  # 初始状态
    IN_SINGLE_QUOTE = enum.auto()  # 'abc'：在单引号引用中
    IN_DOUBLE_QUOTE = enum.auto()  # "abc"：在双引号引用中
    IN_DOLLAR_SINGLE_QUOTE = enum.auto()  # $'abc'：在 ASCI-C 扩展的单引号引用中
    IN_DOLLAR_DOUBLE_QUOTE = enum.auto()  # $"abc"：在本地化翻译的双引号引用中
    IN_BRACE_PARAM = enum.auto()  # ${abc}：在包含大括号的参数扩展中
    IN_BRACE_PARAM_AFTER_COLON = enum.auto()  # ${abc}：在包含大括号的参数扩展中
    IN_PARAM = enum.auto()  # $abc：在不包含大括号的参数扩展中
    IN_DOLLAR_CURVE = enum.auto()  # $(abc)：在小括号的命令替换中（除等待未被引用的闭小括号外与普通语法相同）
    IN_BACK_QUOTE = enum.auto()  # `abc`：在反引号的命令替换中（除等待未被引用的反引号外与普通语法相同）
    IN_ARITHMETIC_EXPANSION = enum.auto()  # $((abc))：在算术扩展中（除等待未被引用的 `))` 外与普通语法相同）
    IN_PROCESS_SUBSTITUTION = enum.auto()  # 在进程替换中（除等待未被引用的 `)` 外与普通语法相同）
    IN_BRACE = enum.auto()  # {abc}：在大括号扩展中
    IN_SPLIT = enum.auto()  # [abc]：在数组切片中
    IN_GROUPING_BRACE = enum.auto()  # { abc }：在命令组中


@enum.unique  # 保证每个值只有一个名称
class CharState(enum.IntFlag):
    """字符状态，前几个字符是否处于特定 Token 的前缀中"""

    INIT = enum.auto()  # 初始状态（当前词语中没有字符）
    NORMAL = enum.auto()  # 非初始的常规状态（当前词语中存在字符）
    COMMENT = enum.auto()  # 注释中
    ASCII_0x23 = enum.auto()  # 【0x23】井号 #
    DOLLAR = enum.auto()  # 【0x24】美元符 $
    ASCII_0x25 = enum.auto()  # 【0x25】百分号 %
    DOLLAR_0x28 = enum.auto()  # $(
    ASCII_0x26 = enum.auto()  # &
    ASCII_0x26_0x3E = enum.auto()  # &>
    ASCII_0x2C = enum.auto()  # 【0x2C】英文半角逗号 ,
    ASCII_0x28 = enum.auto()  # (
    ASCII_0x29 = enum.auto()  # )
    COLON = enum.auto()  # 【0x3A】冒号 :
    ASCII_0x3C = enum.auto()  # <
    ASCII_0x3C_0x3C = enum.auto()  # <<
    ASCII_0x3E = enum.auto()  # >
    ASCII_0x5B = enum.auto()  # [
    ESCAPE = enum.auto()  # 【0x5C】反斜杠（转义符） \
    ASCII_0x5D = enum.auto()  # ]
    ASCII_0x5E = enum.auto()  # 【0x5E】脱字符 ^
    ASCII_0x7B = enum.auto()  # {
    ASCII_0x7C = enum.auto()  # |
    ASCII_0x3D = enum.auto()  # =

    NUMBER = enum.auto()  # 在单个数字之后
    NUMBER_0x3C = enum.auto()  # n<
    NUMBER_0x3C_0x3C = enum.auto()  # n<<
    NUMBER_0x3E = enum.auto()  # n>


@dataclasses.dataclass(slots=True)
class LexicalStateShell(ms_parser.lexical.LexicalStateCached):
    """Shell 词法解析器的缓存器"""

    # 状态栈
    state_stack: List[Tuple[NestState, CharState]] = dataclasses.field(kw_only=True, default_factory=lambda: [])

    @property
    def nest_state(self) -> NestState:
        return self.state_stack[-1][0]

    @property
    def char_state(self) -> CharState:
        return self.state_stack[-1][1]

    def set_state(self, nest_state: NestState, char_state: CharState):
        self.state_stack[-1] = (nest_state, char_state)

    def set_nest_state(self, nest_state: NestState) -> None:
        self.state_stack[-1] = (nest_state, self.state_stack[-1][1])

    def set_char_state(self, char_state: CharState) -> None:
        self.state_stack[-1] = (self.state_stack[-1][0], char_state)

    def append_state(self, nest_state: NestState, char_state: CharState) -> None:
        self.state_stack.append((nest_state, char_state))

    def pop_state(self) -> None:
        self.state_stack.pop()
