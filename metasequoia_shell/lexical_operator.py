"""
Shell 解析器：词法解析行为类

行为类的类名包含如下 3 个部分：
- 行为名称
- 状态操作
- 推断行为

行为名称包含如下 10 种：
1. Nothing：不做任何操作，仅调整状态
2. Shift：移进操作，将当前字符添加到当前词语中，并将指针向后移动 1 个字符
3. Skip：跳过操作，不将当前字符添加到当前词语中，并将指针向后移动 1 个字符
4. Add：添加操作，将指定字符添加到当前词语中，不移动指针
5. Reduce：结束规约操作，结束当前词语（不包含当前字符），不移动指针
6. MoveReduce：结束规约操作，结束当前词语（包含当前字符），并将指针向后移动 1 个字符
7. Fixed：结束固定操作，结束当前词语（不包含当前字符），并为构造的终结符直接赋值，不移动指针
8. MoveFixed：结束固定操作，结束当前词语（包含当前字符），并为构造的终结符直接赋值，并将指针向后移动 1 个字符
9. Error：报错操作
10. Finish：结束操作

状态操作包含如下 4 种，如果不标记则表示不操作状态：
1. SetCharState：设置字符状态
2. SetNestState：设置嵌套状态
3. SetState：设置嵌套状态和字符状态
4. AppendState：向状态栈中入栈状态元组
5. PopState：从状态栈中出栈状态元组

推断行为包含如下 1 种，如果不标记则不进行推断：
1. MaybeKeyword：检查是否为关键字，如果是关键字则将关键字类型作为终结符类型，否则返回使用 IDENT 作为终结符类型
"""

import abc
from typing import Optional

import metasequoia_parser as ms_parser
from metasequoia_shell.lexical_state import CharState, LexicalStateShell, NestState
from metasequoia_shell.terminal_type import KEYWORD_HASH, ShellTerminalType


class Operator(abc.ABC):
    """执行逻辑的抽象基类"""

    @abc.abstractmethod
    def __call__(self, state: LexicalStateShell) -> Optional[ms_parser.symbol.Terminal]:
        pass


class NothingSetCharState(Operator):
    """【不移动指针】
    1. 将字符状态更新为 char_state
    """

    def __init__(self, char_state: CharState):
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.set_char_state(self._char_state)


class NothingPopState(Operator):
    """【不移动指针】
    1. 从状态栈中出栈栈顶元素
    """

    def __call__(self, state: LexicalStateShell):
        state.pop_state()


class Shift(Operator):
    """【移进 + 移动指针】"""

    def __call__(self, state: LexicalStateShell):
        state.shift()


class ShiftSetCharState(Operator):
    """【移进 + 移动指针】

    1. 将当前字符添加到当前词语，并将指针向后移动 1 个字符
    2. 将字符状态更新为 char_state
    """

    def __init__(self, char_state: CharState):
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.set_char_state(self._char_state)
        state.shift()


class Skip(Operator):
    """【跳过 + 移动指针】"""

    def __call__(self, state: LexicalStateShell):
        state.skip()


class SkipSetCharState(Operator):
    """【移进 + 移动指针】

    1. 跳过当前字符（不添加到当前词语），指针向后移动 1 个字符
    2. 将字符状态更新为 char_state
    """

    def __init__(self, char_state: CharState):
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.set_char_state(self._char_state)
        state.skip()


class AddSetCharState(Operator):
    """【添加 + 不移动指针】通常用于不起特殊作用的特殊字符之后，用于补写字符

    1. 将字符 char 添加到当前词语
    2. 将字符状态更新为 char_state
    """

    def __init__(self, char: str, char_state: CharState):
        self._char = char
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.add(self._char)
        state.set_char_state(self._char_state)


class ReduceSetCharState(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符）
    2. 生成 end_as 类型终结符并返回
    3. 将字符状态修改为 char_state
    """

    def __init__(self, end_as: ShellTerminalType, char_state: CharState):
        self._end_as = end_as
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_exclude_now_and_return()
        state.set_char_state(self._char_state)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=value)


class ReduceSetCharStateMaybeKeyword(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符）
    2. 生成 end_as 类型终结符并返回
    3. 将字符状态修改为 char_state
    """

    def __init__(self, char_state: CharState):
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_exclude_now_and_return()
        end_as = KEYWORD_HASH.get(value.upper(), ShellTerminalType.IDENT)
        state.set_char_state(self._char_state)
        return ms_parser.symbol.Terminal(symbol_id=end_as, value=value)


class ReduceSetNestState(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符）
    2. 生成 end_as 类型终结符并返回
    3. 将嵌套状态修改为 nest_state
    """

    def __init__(self, end_as: ShellTerminalType, nest_state: NestState):
        self._end_as = end_as
        self._nest_state = nest_state

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_exclude_now_and_return()
        state.set_nest_state(self._nest_state)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=value)


class ReducePopState(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符）
    2. 生成 end_as 类型终结符并返回
    3. 从状态栈中出栈栈顶元素
    """

    def __init__(self, end_as: ShellTerminalType):
        self._end_as = end_as

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_exclude_now_and_return()
        state.pop_state()
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=value)


class MoveReduce(Operator):
    """【规约 + 移动指针】"""

    def __init__(self, end_as: ShellTerminalType):
        self._end_as = end_as

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_include_now_and_return()
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=value)


class MoveReduceSetCharState(Operator):
    """【规约 + 移动指针】"""

    def __init__(self, end_as: ShellTerminalType, char_state: CharState):
        self._end_as = end_as
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_include_now_and_return()
        state.set_char_state(self._char_state)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=value)


class MoveReduceAppendState(Operator):
    """【规约 + 移动指针】
    1. 结束当前词语（包含当前字符，指针向后移动 1 个字符）
    2. 生成 end_as 类型终结符并返回
    3. 当状态栈中当前层级的 CharState 修改为 CharState.INIT
    4. 在状态栈中入栈 (nest_state, CharState.INIT)
    """

    def __init__(self, end_as: ShellTerminalType, nest_state: NestState):
        self._end_as = end_as
        self._nest_state = nest_state

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_include_now_and_return()
        state.set_char_state(CharState.INIT)
        state.append_state(self._nest_state, CharState.INIT)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=value)


class MoveReducePopState(Operator):
    """【规约 + 移动指针】
    1. 结束当前词语（包含当前字符，指针向后移动 1 个字符）
    2. 生成 end_as 类型终结符并返回
    3. 从状态栈中出栈栈顶元素
    """

    def __init__(self, end_as: ShellTerminalType):
        self._end_as = end_as

    def __call__(self, state: LexicalStateShell):
        value = state.end_word_include_now_and_return()
        state.pop_state()
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=value)


class Fixed(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    """

    def __init__(self, end_as: ShellTerminalType, value: str):
        self._end_as = end_as
        self._value = value

    def __call__(self, state: LexicalStateShell):
        state.end_word_exclude_now()
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class FixedSetCharState(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符，不移动指针）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    3. 当状态栈中当前层级的 CharState 修改为 char_state
    """

    def __init__(self, end_as: ShellTerminalType, value: str, char_state: CharState):
        self._end_as = end_as
        self._value = value
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.end_word_exclude_now()
        state.set_char_state(self._char_state)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class FixedSetState(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符，不移动指针）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    3. 将栈顶的嵌套状态修改为 nest_state，将字符状态修改为 char_state
    """

    def __init__(self, end_as: ShellTerminalType, value: str, nest_state: NestState, char_state: CharState):
        self._end_as = end_as
        self._value = value
        self._nest_state = nest_state
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.end_word_exclude_now()
        state.set_state(self._nest_state, self._char_state)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class FixedAppendState(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符，不移动指针）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    3. 当状态栈中当前层级的 CharState 修改为 CharState.INIT
    4. 在状态栈中入栈 (nest_state, CharState.INIT)
    """

    def __init__(self, end_as: ShellTerminalType, value: str, nest_state: NestState):
        self._end_as = end_as
        self._value = value
        self._nest_state = nest_state

    def __call__(self, state: LexicalStateShell):
        state.end_word_exclude_now()
        state.set_char_state(CharState.INIT)
        state.append_state(self._nest_state, CharState.INIT)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class FixedPopState(Operator):
    """【规约 + 不移动指针】
    1. 结束当前词语（不包含当前字符，不移动指针）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    3. 从状态栈中出栈栈顶元素
    """

    def __init__(self, end_as: ShellTerminalType, value: str):
        self._end_as = end_as
        self._value = value

    def __call__(self, state: LexicalStateShell):
        state.end_word_exclude_now()
        state.pop_state()
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class MoveFixed(Operator):
    """【规约 + 移动指针】
    1. 结束当前词语（包含当前字符，指针向后移动 1 个字符）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    """

    def __init__(self, end_as: ShellTerminalType, value: str):
        self._end_as = end_as
        self._value = value

    def __call__(self, state: LexicalStateShell):
        state.end_word_include_now()
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class MoveFixedSetCharState(Operator):
    """【规约 + 移动指针】
    1. 结束当前词语（包含当前字符，指针向后移动 1 个字符）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    3. 当状态栈中当前层级的 CharState 修改为 char_state
    """

    def __init__(self, end_as: ShellTerminalType, value: str, char_state: CharState):
        self._end_as = end_as
        self._value = value
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.end_word_include_now()
        state.set_char_state(self._char_state)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class MoveFixedAppendState(Operator):
    """【规约 + 移动指针】
    1. 结束当前词语（包含当前字符，指针向后移动 1 个字符）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    3. 当状态栈中当前层级的 CharState 修改为 CharState.INIT
    4. 在状态栈中入栈 (nest_state, CharState.INIT)
    """

    def __init__(self, end_as: ShellTerminalType, value: str, nest_state: NestState):
        self._end_as = end_as
        self._value = value
        self._nest_state = nest_state

    def __call__(self, state: LexicalStateShell):
        state.end_word_include_now()
        state.set_char_state(CharState.INIT)
        state.append_state(self._nest_state, CharState.INIT)
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class MoveFixedPopState(Operator):
    """【规约 + 移动指针】
    1. 结束当前词语（包含当前字符，指针向后移动 1 个字符）
    2. 生成类型为 end_as，值为 value 的终结符并返回
    3. 从状态栈中出栈栈顶元素
    """

    def __init__(self, end_as: ShellTerminalType, value: str):
        self._end_as = end_as
        self._value = value

    def __call__(self, state: LexicalStateShell):
        state.end_word_include_now()
        state.pop_state()
        return ms_parser.symbol.Terminal(symbol_id=self._end_as, value=self._value)


class Error(Operator):
    """【异常】抛出异常"""

    def __call__(self, state: LexicalStateShell):
        raise Exception(f"未知的词法结构，"
                        f"nest_state={state.nest_state.name}({state.nest_state.value}), "
                        f"char_state={state.char_state.name}({state.char_state.value})")


class Finish(Operator):
    """【结束】"""

    def __call__(self, state: LexicalStateShell):
        return ms_parser.symbol.Terminal.end()


class AddAndShiftSetCharState(Operator):
    """【添加 + 移进】

    1. 将字符 char 添加到当前词语
    2. 经当前字符到当前词语，并将指针向后移动 1 个字符
    3. 将字符状态更新为 char_state
    """

    def __init__(self, char: str, char_state: CharState):
        self._char = char
        self._char_state = char_state

    def __call__(self, state: LexicalStateShell):
        state.add(self._char)
        state.shift()
        state.set_char_state(self._char_state)
