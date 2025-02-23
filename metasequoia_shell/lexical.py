"""
词法解析器
"""

from typing import List, Optional

import metasequoia_parser as ms_parser
from metasequoia_shell.lexical_map import FSM_OPERATION_MAP, FSM_OPERATION_MAP_DEFAULT
from metasequoia_shell.lexical_operator import Operator
from metasequoia_shell.lexical_state import CharState, LexicalStateShell, NestState
from metasequoia_shell.terminal_type import (END_TERMINAL_SET, PIPE_TERMINAL_SET, REDIRECTION_TERMINAL_SET,
                                             RELATION_TERMINAL_SET, ShellTerminalType as TType)

# 需要过滤掉前后空格的终结符
SPECIAL_TERMINAL_SET = (
        REDIRECTION_TERMINAL_SET |  # 重定向终结符
        PIPE_TERMINAL_SET |  # 通道终结符
        RELATION_TERMINAL_SET |  # 命令列表的命令关系终结符
        END_TERMINAL_SET |  # 命令结束终结符
        {TType.UNTIL, TType.DO, TType.DONE, TType.WHILE, TType.FOR, TType.IN,
         TType.IF, TType.ELIF, TType.THEN, TType.ELSE, TType.FI,
         TType.CASE, TType.IN, TType.ESAC, TType.ASCII_0x7C,
         TType.SELECT, TType.COPROC, TType.FUNCTION}  # 关键字
)


class LexicalFSMShell(ms_parser.lexical.LexicalFSM):
    """Shell 词法解析器"""

    def __init__(self, text: str):
        super().__init__(text)
        self.state = LexicalStateShell(text=text)
        self.state.append_state(NestState.NORMAL, CharState.INIT)

        # ------------------------------ 词法解析器 ------------------------------
        # 因为 Shell 的语法部分不满足 LALR(1) 语义，所以需要在语法解析前，先进行词法结果简化，使其满足 LALR(1) 语义
        is_not_finish = True  # 是否仍未解析结束（即遇到 END 终结符）
        cache_0: List[ms_parser.symbol.Terminal] = []  # 已经解析的终结符列表（不包含最后的 END 终结符）
        while is_not_finish:
            while True:
                char = self.state.char()

                # print(char, self.state.nest_state.name, self.state.char_state.name)

                operate: Optional[Operator] = FSM_OPERATION_MAP.get(
                    (self.state.nest_state, self.state.char_state, char))

                if operate is None:
                    # 如果没有则使用当前状态的默认处理规则
                    operate: Operator = FSM_OPERATION_MAP_DEFAULT[(self.state.nest_state, self.state.char_state)]

                # 执行处理方法
                try:
                    res: Optional[ms_parser.symbol.Terminal] = operate(self.state)
                except Exception as e:
                    print("当前终结符:", char)
                    raise e
                if res is not None:
                    if res.is_end:
                        is_not_finish = False
                    else:
                        cache_0.append(res)
                    break

        # ------------------------------ 词法结果简化器 ------------------------------
        # TODO 从长远来看，我们希望将语法结果简化器中的逻辑，尽可能移动到词法解析层或语法解析层中
        # 移除开头、结尾的多余空格
        start_idx = 0
        end_idx = len(cache_0) - 1
        while start_idx <= end_idx and cache_0[start_idx].symbol_id == TType.SPACE:
            start_idx += 1
        while end_idx >= start_idx and cache_0[end_idx].symbol_id == TType.SPACE:
            end_idx -= 1
        cache_0 = cache_0[start_idx: end_idx + 1]

        # 如果脚本末尾没有显式的结束符，则补充一个结束符
        if len(cache_0) > 0:
            if cache_0[-1].symbol_id not in END_TERMINAL_SET:
                cache_0.append(ms_parser.symbol.Terminal(symbol_id=TType.ASCII_0x3B, value=";"))

        # 删除指定终结符之前的换行符和空格
        cache_1 = []
        for token in cache_0:
            if token.symbol_id in {TType.BACK_QUOTE_CLOSE, TType.ASCII_0x5D_0x5D, TType.ASCII_0x29_0x29}:
                while cache_1 and cache_1[-1].symbol_id in {TType.SPACE, TType.ASCII_0x0A}:
                    cache_1.pop()
            cache_1.append(token)

        # 合并多个连续的空格、以及特殊符号（重定向终结符、通道终结符、命令关系终结符和命令结束终结符）前后的空格
        cache_2 = []
        mode = 0  # 处理状态；0=正常、1=之前有一个或多个空格，2=特殊符号之后需要继续过滤空格
        for token in cache_1:
            if mode == 0:
                if token.symbol_id == TType.SPACE:
                    mode = 1
                elif token.symbol_id in SPECIAL_TERMINAL_SET:
                    cache_2.append(token)
                    mode = 2
                else:
                    cache_2.append(token)
            elif mode == 1:
                if token.symbol_id == TType.SPACE:  # 合并多个连续的空格
                    continue
                elif token.symbol_id in SPECIAL_TERMINAL_SET:  # 需要剔除前后空格的终结符
                    cache_2.append(token)
                    mode = 2
                else:
                    cache_2.append(ms_parser.symbol.Terminal(symbol_id=TType.SPACE, value=" "))
                    cache_2.append(token)
                    mode = 0
            elif mode == 2:
                if token.symbol_id == TType.SPACE:
                    pass
                elif token.symbol_id in SPECIAL_TERMINAL_SET:
                    cache_2.append(token)
                else:
                    cache_2.append(token)
                    mode = 0

        # 忽略空命令
        cache_3 = []
        last = True
        for token in cache_2:
            if token.symbol_id in END_TERMINAL_SET:
                if last is True:
                    continue
                last = True
            else:
                last = False
            cache_3.append(token)

        # 在子命令之后补充结束符
        cache_4 = []
        last = False
        for token in cache_3:
            if token.symbol_id in END_TERMINAL_SET:
                cache_4.append(token)
                last = True
            elif last is False and token.symbol_id in {TType.ASCII_0x29, TType.BACK_QUOTE_CLOSE, TType.ASCII_0x5D_0x5D,
                                                       TType.ASCII_0x29_0x29, TType.ASCII_0x5D}:
                cache_4.append(ms_parser.symbol.Terminal(symbol_id=TType.ASCII_0x3B, value=";"))
                cache_4.append(token)
            else:
                cache_4.append(token)
                last = False

        # 删除指定终结符之后的换行符和空格
        cache_5 = []
        last = False
        for token in cache_4:
            if token.symbol_id in {TType.DO, TType.ELIF, TType.ELSE, TType.THEN, TType.KEYWORD_BRACE_OPEN,
                                   TType.ASCII_0x5B_0x5B, TType.ASCII_0x28_0x28, TType.DOLLAR_0x28_0x28,
                                   TType.BACK_QUOTE_OPEN}:
                cache_5.append(token)
                last = True
            elif last is True and token.symbol_id in {TType.SPACE, TType.ASCII_0x0A}:
                pass
            else:
                cache_5.append(token)
                last = False

        self.cache: List[ms_parser.symbol.Terminal] = cache_5  # 已经解析的终结符列表（不包含最后的 END 终结符）
        self.index: int = 0  # 当前下标位置

    def lex(self) -> ms_parser.symbol.Terminal:
        if self.index < len(self.cache):
            res = self.cache[self.index]
            self.index += 1
            return res
        else:
            return ms_parser.symbol.Terminal.end()
