"""语法定义"""

import metasequoia_parser as ms_parser
from metasequoia_shell import ast
from metasequoia_shell.terminal_type import ShellTerminalType as TType


def build_grammar():
    """构造语法结构"""

    # TODO 将 {、} 根据场景拆分词法结果，并辅以不同的语法结果
    # TODO 增加对不同换行方式的支持程度
    # TODO 将补充的换行符修改为实际不显示的终结符
    # TODO 研究最终结果规约 SR 优先级为空是否异常
    # TODO 优化赋值语句的出现位置及场景

    grammar_builder = ms_parser.create_grammar(
        groups=[
            ms_parser.create_group(
                name="entry",
                rules=[
                    ms_parser.create_rule(symbols=["script"]),
                ]
            )
        ],
        terminal_type_enum=TType,
        start="entry",
        sr_priority=[
            # 等于号
            ms_parser.create_sr_priority(symbols=[TType.ASCII_0x3D], combine_type=ms_parser.COMBINE_LEFT),

            # 命令结束符
            ms_parser.create_sr_priority(symbols=[
                TType.ASCII_0x3B, TType.ASCII_0x0A, TType.ASCII_0x26
            ], combine_type=ms_parser.COMBINE_LEFT),

            # 命令列表层级
            ms_parser.create_sr_priority(symbols=[TType.ASCII_0x26_0x26, TType.ASCII_0x7C_0x7C],
                                         combine_type=ms_parser.COMBINE_LEFT),

            # 管道层级
            ms_parser.create_sr_priority(symbols=[TType.ASCII_0x7C, TType.ASCII_0x7C_0x26],
                                         combine_type=ms_parser.COMBINE_LEFT),

            # 普通元素
            ms_parser.create_sr_priority(symbols=[TType.IDENT], combine_type=ms_parser.COMBINE_LEFT),

            # 提高 shell_word_list 的优先级，保证 `shell_word_list` 可以正常解析
            ms_parser.create_sr_priority(symbols=[TType.SPACE], combine_type=ms_parser.COMBINE_LEFT),

            # # 扩展层级
            # ms_parser.create_sr_priority(symbols=[TType.ASCII_0x7B, TType.DOLLAR], combine_type=ms_parser.COMBINE_LEFT),

            # # 重定向层级 TODO
            # ms_parser.create_sr_priority(symbols=[TType.ASCII_0x3C, TType.ASCII_0x3E], combine_type=ms_parser.COMBINE_LEFT),
        ],
    )

    # ------------------------------ Shell 元素层级解析 ------------------------------
    # 解析 Shell 单个元素
    grammar_builder.group_append(ms_parser.create_group(
        name="shell_element",
        rules=[
            ms_parser.create_rule(symbols=["ident"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["array_at"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["array_star"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["array_getter"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["arithmetic_expansion"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["brace_expansion"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["tilde_expansion"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["parameter_expansion"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["param"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["command_substitution"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["single_quote_string"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["dollar_single_quote_string"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["double_quote_string"], sr_priority_as=TType.IDENT),
            ms_parser.create_rule(symbols=["dollar_double_quote_string"], sr_priority_as=TType.IDENT),
        ]
    ))

    # 解析 Shell 元素列表
    grammar_builder.group_append(ms_parser.create_group(
        name="shell_element_list",
        rules=[
            ms_parser.create_rule(
                symbols=["shell_element_list", "shell_element"],
                action=ms_parser.template.action.LIST_APPEND_1
            ),
            ms_parser.create_rule(
                symbols=["shell_element"],
                action=ms_parser.template.action.LIST_INIT_0
            )
        ]
    ))

    # 解析 Shell 元素列表
    grammar_builder.group_append(ms_parser.create_group(
        name="shell_element_list_comma",
        rules=[
            ms_parser.create_rule(
                symbols=["shell_element_list_comma", TType.ASCII_0x2C, "shell_element"],
                action=lambda x: x[0] + [x[2]]
            ),
            ms_parser.create_rule(
                symbols=["shell_element"],
                action=ms_parser.template.action.LIST_INIT_0
            )
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="ident",
        rules=[
            ms_parser.create_rule(symbols=[TType.IDENT], action=lambda x: ast.Ident(string=x[0])),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3D], action=lambda x: ast.Ident(string="=")),
        ]
    ))

    # Array[@]
    grammar_builder.group_append(ms_parser.create_group(
        name="array_at",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.IDENT, TType.ASCII_0x5B, TType.ASCII_0x40, TType.ASCII_0x3B, TType.ASCII_0x5D],
                action=lambda x: ast.ArrayAt(array=x[0]))
        ]
    ))

    # Array[*]
    grammar_builder.group_append(ms_parser.create_group(
        name="array_star",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.IDENT, TType.ASCII_0x5B, TType.ASCII_0x2A, TType.ASCII_0x3B, TType.ASCII_0x5D],
                action=lambda x: ast.ArrayStar(array=x[0]))
        ]
    ))

    # Array[subscript]
    grammar_builder.group_append(ms_parser.create_group(
        name="array_getter",
        rules=[
            ms_parser.create_rule(symbols=[TType.IDENT, TType.ASCII_0x5B, "script", TType.ASCII_0x5D],
                                  action=lambda x: ast.ArrayGetter(array=x[0], script=x[2]))
        ]
    ))

    # 算术扩展
    grammar_builder.group_append(ms_parser.create_group(
        name="arithmetic_expansion",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_0x28_0x28, "script", TType.ASCII_0x29_0x29],
                action=lambda x: ast.ArithmeticExpansion(script=x[1]))
        ]
    ))

    # 大括号扩展
    grammar_builder.group_append(ms_parser.create_group(
        name="brace_expansion",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.ASCII_0x7B, "shell_element_list_comma", TType.ASCII_0x7D],
                action=lambda x: ast.BraceExpansion(element_list=x[1])
            )
        ]
    ))

    # 波浪线扩展
    grammar_builder.group_append(ms_parser.create_group(
        name="tilde_expansion",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.SLIDE, "shell_element_list"],
                action=lambda x: ast.TildeExpansion(element_list=x[1])
            )
        ]
    ))

    # 可选的感叹号
    grammar_builder.group_append(ms_parser.create_group(
        name="opt_indirect",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.ASCII_0x21],
                action=lambda _: True
            ),
            ms_parser.create_rule(
                symbols=[],
                action=lambda _: False
            )
        ]
    ))

    # 参数扩展
    grammar_builder.group_append(ms_parser.create_group(
        name="parameter_expansion",
        rules=[
            # TODO 待确定是否这里只需要 shell_element 或其他更固定的值即可
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_0x7B, "opt_indirect", "shell_element_list", TType.ASCII_0x7D],
                action=lambda x: ast.BraceParamExpansion(element_list=x[2], indirect=x[1])
            ),
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_0x7B, "opt_indirect", "shell_element_list", TType.ASCII_0x3A, "shell_element",
                         TType.ASCII_0x7D],
                action=lambda x: ast.BraceParamExpansion(element_list=x[2], indirect=x[1], offset=x[4])
            ),
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_0x7B, "opt_indirect", "shell_element_list", TType.ASCII_0x3A, "shell_element",
                         TType.ASCII_0x3A, "shell_element", TType.ASCII_0x7D],
                action=lambda x: ast.BraceParamExpansion(element_list=x[2], indirect=x[1], offset=x[4], length=x[6])
            ),
            ms_parser.create_rule(
                symbols=[TType.DOLLAR, TType.IDENT],
                action=lambda x: ast.ParamExpansion(name=x[1])
            )
        ]
    ))

    # 命令替换
    grammar_builder.group_append(ms_parser.create_group(
        name="command_substitution",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_0x28, "script", TType.ASCII_0x29],
                action=lambda x: ast.CommandSubstitution.create_curve(x[1])
            ),
            ms_parser.create_rule(
                symbols=[TType.BACK_QUOTE_OPEN, "script", TType.BACK_QUOTE_CLOSE],
                action=lambda x: ast.CommandSubstitution.create_back_quote(x[1])
            )
        ]
    ))

    # 位置参数和特殊参数：https://zhuanlan.zhihu.com/p/720877125
    grammar_builder.group_append(ms_parser.create_group(
        name="param",
        rules=[
            ms_parser.create_rule(symbols=[TType.DOLLAR_0], action=lambda _: ast.Param0()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_1], action=lambda _: ast.Param1()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_2], action=lambda _: ast.Param2()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_3], action=lambda _: ast.Param3()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_4], action=lambda _: ast.Param4()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_5], action=lambda _: ast.Param5()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_6], action=lambda _: ast.Param6()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_7], action=lambda _: ast.Param7()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_8], action=lambda _: ast.Param8()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_9], action=lambda _: ast.Param9()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_0x21], action=lambda _: ast.ParamExclamation()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_0x23], action=lambda _: ast.ParamPound()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_0x2A], action=lambda _: ast.ParamStar()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_0x2D], action=lambda _: ast.ParamHyphen()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_0x3F], action=lambda _: ast.ParamQuestion()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_0x40], action=lambda _: ast.ParamAt()),
            ms_parser.create_rule(symbols=[TType.DOLLAR_DOLLAR], action=lambda _: ast.ParamDollar()),
        ]
    ))

    # 单引号字符串
    grammar_builder.group_append(ms_parser.create_group(
        name="single_quote_string",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.SINGLE_QUOTE, TType.IDENT, TType.SINGLE_QUOTE],
                action=lambda x: ast.SingleQuoteString(string=x[1])
            ),
            ms_parser.create_rule(
                symbols=[TType.SINGLE_QUOTE, TType.SINGLE_QUOTE],
                action=lambda x: ast.SingleQuoteString(string=None)
            ),
        ]
    ))

    # ANSI-C 扩展单引号字符串
    grammar_builder.group_append(ms_parser.create_group(
        name="dollar_single_quote_string",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_SINGLE_QUOTE, TType.IDENT, TType.SINGLE_QUOTE],
                action=lambda x: ast.DollarSingleQuoteString.create(string=x[1])
            ),
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_SINGLE_QUOTE, TType.SINGLE_QUOTE],
                action=lambda x: ast.DollarSingleQuoteString.create(string=None)
            )
        ]
    ))

    # 双引号字符串
    grammar_builder.group_append(ms_parser.create_group(
        name="double_quote_string",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.DOUBLE_QUOTE_OPEN, "shell_element_list", TType.DOUBLE_QUOTE_CLOSE],
                action=lambda x: ast.DoubleQuoteString(element_list=x[1])
            ),
            ms_parser.create_rule(
                symbols=[TType.DOUBLE_QUOTE_OPEN, TType.DOUBLE_QUOTE_CLOSE],
                action=lambda x: ast.DoubleQuoteString(element_list=None)
            )
        ]
    ))

    # 本地化翻译字符串
    grammar_builder.group_append(ms_parser.create_group(
        name="dollar_double_quote_string",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_DOUBLE_QUOTE, "shell_element_list", TType.DOUBLE_QUOTE_CLOSE],
                action=lambda x: ast.DollarDoubleQuoteString(element_list=x[1])
            ),
            ms_parser.create_rule(
                symbols=[TType.DOLLAR_DOUBLE_QUOTE, TType.DOUBLE_QUOTE_CLOSE],
                action=lambda x: ast.DollarDoubleQuoteString(element_list=None)
            )
        ]
    ))

    # ------------------------------ Shell 单词层级解析 ------------------------------
    # 解析单个 Shell 单词
    grammar_builder.group_append(ms_parser.create_group(
        name="shell_word",
        rules=[
            ms_parser.create_rule(symbols=["normal_word"], sr_priority_as=TType.SPACE),
            ms_parser.create_rule(symbols=["arithmetic_expression"], sr_priority_as=TType.SPACE),
            ms_parser.create_rule(symbols=["conditional_expression"], sr_priority_as=TType.SPACE),
            ms_parser.create_rule(symbols=["grouping_command"], sr_priority_as=TType.SPACE),
            ms_parser.create_rule(symbols=["assignment"], sr_priority_as=TType.SPACE),
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="normal_word",
        rules=[
            ms_parser.create_rule(symbols=["shell_element_list"], action=lambda x: ast.NormalWord(element_list=x[0]))
        ]
    ))

    # 算术表达式
    grammar_builder.group_append(ms_parser.create_group(
        name="arithmetic_expression",
        rules=[
            ms_parser.create_rule(symbols=[TType.ASCII_0x28_0x28, "script", TType.ASCII_0x29_0x29],
                                  action=lambda x: ast.ArithmeticExpression(script=x[1]))
        ]
    ))

    # 条件表达式
    grammar_builder.group_append(ms_parser.create_group(
        name="conditional_expression",
        rules=[
            ms_parser.create_rule(symbols=[TType.ASCII_0x5B_0x5B, "script", TType.ASCII_0x5D_0x5D],
                                  action=lambda x: ast.ConditionalExpression(script=x[1]))
        ]
    ))

    # 命令组
    grammar_builder.group_append(ms_parser.create_group(
        name="grouping_command",
        rules=[
            ms_parser.create_rule(symbols=[TType.ASCII_0x28, "script", TType.ASCII_0x29],
                                  action=lambda x: ast.GroupingCommand.create_sub_process(script=x[1])),
            ms_parser.create_rule(symbols=[TType.KEYWORD_BRACE_OPEN, "script", TType.KEYWORD_BRACE_CLOSE],
                                  action=lambda x: ast.GroupingCommand.create_context(script=x[1])),
        ]
    ))

    # 赋值语句
    grammar_builder.group_append(ms_parser.create_group(
        name="assignment",
        rules=[
            ms_parser.create_rule(
                symbols=[TType.IDENT, TType.ASCII_0x3D, "shell_element_list"],
                action=lambda x: ast.Assignment(name=x[0], value_element_list=x[2])
            ),
            # 数组
            ms_parser.create_rule(
                symbols=[TType.IDENT, TType.ASCII_0x3D, TType.ASCII_0x28, "shell_word_list", TType.ASCII_0x3B,
                         TType.ASCII_0x29],
                action=lambda x: ast.AssignmentArray(name=x[0], value_element_list=x[3])
            )
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="shell_word_list",
        rules=[
            ms_parser.create_rule(symbols=["shell_word_list", TType.SPACE, "shell_word"],
                                  action=lambda x: x[0] + [x[2]]),
            ms_parser.create_rule(symbols=["shell_word"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    # ------------------------------ Shell 命令层级解析 ------------------------------

    grammar_builder.group_append(ms_parser.create_group(
        name="elif_item",
        rules=[
            ms_parser.create_rule(symbols=[TType.ELIF, "script", TType.THEN, "script"],
                                  action=lambda x: ast.ElifItem(test_script=x[1], consequent_script=x[3]))
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="elif_list",
        rules=[
            ms_parser.create_rule(symbols=["elif_list", "elif_item"], action=ms_parser.template.action.LIST_APPEND_1),
            ms_parser.create_rule(symbols=["elif_item"], action=ms_parser.template.action.LIST_INIT_0),
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="other_pattern",
        rules=[
            ms_parser.create_rule(symbols=[TType.ASCII_0x7C, "shell_word"], action=lambda x: x[1])
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="other_pattern_list",
        rules=[
            ms_parser.create_rule(
                symbols=["other_pattern_list", "other_pattern"],
                action=ms_parser.template.action.LIST_APPEND_1
            ),
            ms_parser.create_rule(symbols=["other_pattern"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="pattern_list",
        rules=[
            ms_parser.create_rule(symbols=["shell_word", "other_pattern_list"], action=lambda x: [x[0]] + x[1]),
            ms_parser.create_rule(symbols=["shell_word"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="case_item",
        rules=[
            ms_parser.create_rule(
                symbols=["pattern_list", TType.SPACE, "script"],
                action=lambda x: ast.CaseItem(pattern_list=x[0], script=x[2])
            )
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="case_item_list",
        rules=[
            ms_parser.create_rule(symbols=["case_item_list", "case_item"],
                                  action=ms_parser.template.action.LIST_APPEND_1),
            ms_parser.create_rule(symbols=["case_item"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    # 不包含重定向、管道等的基础命令
    grammar_builder.group_append(ms_parser.create_group(
        name="bare_command",
        rules=[
            # 简单命令
            ms_parser.create_rule(symbols=["shell_word_list"],
                                  action=lambda x: ast.SimpleCommand(word_list=x[0])),

            # UNTIL 命令
            ms_parser.create_rule(symbols=[TType.UNTIL, "script", TType.DO, "script", TType.DONE],
                                  action=lambda x: ast.UntilCommand(test_script=x[1], consequent_script=x[3])),

            # WHILE 命令
            ms_parser.create_rule(symbols=[TType.WHILE, "script", TType.DO, "script", TType.DONE],
                                  action=lambda x: ast.WhileCommand(test_script=x[1], consequent_script=x[3])),

            # FOR 命令（格式 1）
            ms_parser.create_rule(
                symbols=[TType.FOR, "shell_word", "command_end_type", TType.DO, "script", TType.DONE],
                action=lambda x: ast.EnhanceForCommand(name=x[1], script=x[4])),
            ms_parser.create_rule(
                symbols=[TType.FOR, "shell_word", TType.IN, "shell_word_list", "command_end_type", TType.DO,
                         "script", TType.DONE],
                action=lambda x: ast.EnhanceForCommand(name=x[1], word_list=x[3], script=x[6])),

            # FOR 命令（格式 2）
            ms_parser.create_rule(
                symbols=[TType.FOR, TType.ASCII_0x28_0x28, "script", TType.ASCII_0x29_0x29, TType.ASCII_0x3B,
                         TType.DO, "script", TType.DONE],
                action=lambda x: ast.ForCommand(test_script=x[2], consequent_script=x[6])),

            # IF 命令
            ms_parser.create_rule(
                symbols=[TType.IF, "script", TType.THEN, "script", "elif_list", TType.ELSE, "script", TType.FI],
                action=lambda x: ast.IfCommand(test_script=x[1], consequent_script=x[3], else_if_list=x[4],
                                               alternate_script=x[6])),
            ms_parser.create_rule(
                symbols=[TType.IF, "script", TType.THEN, "script", "elif_list", TType.FI],
                action=lambda x: ast.IfCommand(test_script=x[1], consequent_script=x[3], else_if_list=x[4],
                                               alternate_script=None)),
            ms_parser.create_rule(
                symbols=[TType.IF, "script", TType.THEN, "script", TType.ELSE, "script", TType.FI],
                action=lambda x: ast.IfCommand(test_script=x[1], consequent_script=x[3], else_if_list=[],
                                               alternate_script=x[5])),
            ms_parser.create_rule(
                symbols=[TType.IF, "script", TType.THEN, "script", TType.FI],
                action=lambda x: ast.IfCommand(test_script=x[1], consequent_script=x[3], else_if_list=[],
                                               alternate_script=None)),

            # CASE 命令
            ms_parser.create_rule(
                symbols=[TType.CASE, "shell_word", TType.IN, "case_item_list", TType.ESAC],
                action=lambda x: ast.CaseCommand(word=x[1], item_list=x[3])
            ),

            # SELECT 命令
            ms_parser.create_rule(
                symbols=[TType.SELECT, "shell_word", TType.ASCII_0x3B, TType.DO, "script", TType.DONE],
                action=lambda x: ast.SelectCommand(name=x[1], word_list=None, script=x[4])),
            ms_parser.create_rule(symbols=[TType.SELECT, "shell_word", TType.IN, "shell_word_list", TType.ASCII_0x3B,
                                           TType.DO, "script", TType.DONE],
                                  action=lambda x: ast.SelectCommand(name=x[1], word_list=x[3], script=x[6])),

            # 协进程
            ms_parser.create_rule(
                symbols=[TType.COPROC, "shell_word", TType.SPACE, TType.KEYWORD_BRACE_OPEN, "script",
                         TType.KEYWORD_BRACE_CLOSE],
                action=lambda x: ast.Coprocess(name=x[1], script=x[4])
            ),
            ms_parser.create_rule(
                symbols=[TType.COPROC, TType.KEYWORD_BRACE_OPEN, "script", TType.KEYWORD_BRACE_CLOSE],
                action=lambda x: ast.Coprocess(name=None, script=x[2])
            ),

            # 函数 TODO 考虑移除生成的 ;
            # TODO 待将空格改为可选，而不是 4 个规则
            ms_parser.create_rule(
                symbols=[TType.FUNCTION, "shell_word", TType.SPACE, TType.ASCII_0x28, TType.ASCII_0x3B,
                         TType.ASCII_0x29, TType.SPACE, TType.KEYWORD_BRACE_OPEN, "script", TType.KEYWORD_BRACE_CLOSE],
                action=lambda x: ast.Function(name=x[1], script=x[8])
            ),
            ms_parser.create_rule(
                symbols=[TType.FUNCTION, "shell_word", TType.SPACE, TType.ASCII_0x28, TType.ASCII_0x3B,
                         TType.ASCII_0x29, TType.KEYWORD_BRACE_OPEN, "script", TType.KEYWORD_BRACE_CLOSE],
                action=lambda x: ast.Function(name=x[1], script=x[7])
            ),
            ms_parser.create_rule(
                symbols=[TType.FUNCTION, "shell_word", TType.ASCII_0x28, TType.ASCII_0x3B, TType.ASCII_0x29,
                         TType.SPACE, TType.KEYWORD_BRACE_OPEN, "script", TType.KEYWORD_BRACE_CLOSE],
                action=lambda x: ast.Function(name=x[1], script=x[7])
            ),
            ms_parser.create_rule(
                symbols=[TType.FUNCTION, "shell_word", TType.ASCII_0x28, TType.ASCII_0x3B, TType.ASCII_0x29,
                         TType.KEYWORD_BRACE_OPEN, "script", TType.KEYWORD_BRACE_CLOSE],
                action=lambda x: ast.Function(name=x[1], script=x[6])
            ),
        ]
    ))

    # 重定向子句：https://zhuanlan.zhihu.com/p/721327213
    grammar_builder.group_append(ms_parser.create_group(
        name="redirection",
        rules=[
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3C,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3C_0x26, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3C_0x26,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3C_0x3C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3C_0x3C,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3C_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3C_0x3E,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3C_0x3C_0x2D, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3C_0x3C_0x2D,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3C_0x3C_0x3C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3C_0x3C_0x3C,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3E,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3E_0x7C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3E_0x7C,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3E_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3E_0x3E,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.NUMBER_0x3E_0x26, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_number_redirection(
                                      rtype=ast.RedirectionType.NUMBER_0x3E_0x26,
                                      number=int(x[0][0]),
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3C,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3E,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3E_0x7C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3E_0x7C,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3E_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3E_0x3E,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x26_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x26_0x3E,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3E_0x26, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3E_0x26,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x26_0x3E_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x26_0x3E_0x3E,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3C_0x3C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3C_0x3C,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3C_0x3C_0x2D, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3C_0x3C_0x2D,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3C_0x3C_0x3C, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3C_0x3C_0x3C,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3C_0x26, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3C_0x26,
                                      word_list=x[1]
                                  )),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3C_0x3E, "shell_word_list"],
                                  action=lambda x: ast.Redirection.create_redirection(
                                      rtype=ast.RedirectionType.ASCII_0x3C_0x3E,
                                      word_list=x[1]
                                  ))
        ]
    ))

    # 重定向子句的列表
    grammar_builder.group_append(ms_parser.create_group(
        name="redirection_list",
        rules=[
            ms_parser.create_rule(symbols=["redirection_list", "redirection"],
                                  action=ms_parser.template.action.LIST_APPEND_1),
            ms_parser.create_rule(symbols=["redirection"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="opt_redirection_list",
        rules=[
            ms_parser.create_rule(symbols=["redirection_list"], action=ms_parser.template.action.RETURN_0),
            ms_parser.template.rule.EMPTY_RETURN_NULL
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="command_with_redirection",
        rules=[
            ms_parser.create_rule(symbols=["bare_command", "opt_redirection_list"],
                                  action=lambda x: ast.CommandWithRedirection.create(bare_command=x[0],
                                                                                     redirection_list=x[1]))
        ]
    ))

    # -------------------------------------- 解析管道 --------------------------------------

    # pipe_type：管道类型
    grammar_builder.group_append(ms_parser.create_group(
        name="pipe_type",
        rules=[
            ms_parser.create_rule(symbols=[TType.ASCII_0x7C], action=lambda _: ast.PipeType.ASCII_0x7C),
            ms_parser.create_rule(symbols=[TType.ASCII_0x7C_0x26], action=lambda _: ast.PipeType.ASCII_0x7C_0x26)
        ]
    ))

    # pipe：管道子句
    grammar_builder.group_append(ms_parser.create_group(
        name="pipe",
        rules=[
            ms_parser.create_rule(symbols=["pipe_type", "command_with_redirection"],
                                  action=lambda x: ast.Pipe(type=x[0], command=x[1]),
                                  sr_priority_as=TType.ASCII_0x7C)
        ]
    ))

    # pipe_list：一个或多个管道子句
    grammar_builder.group_append(ms_parser.create_group(
        name="pipe_list",
        rules=[
            ms_parser.create_rule(symbols=["pipe_list", "pipe"], action=ms_parser.template.action.LIST_APPEND_1),
            ms_parser.create_rule(symbols=["pipe"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    # opt_pipe_list：零个、一个或多个管道子句
    grammar_builder.group_append(ms_parser.create_group(
        name="opt_pipe_list",
        rules=[
            ms_parser.create_rule(symbols=["pipe_list"], action=ms_parser.template.action.RETURN_0),
            ms_parser.template.rule.EMPTY_RETURN_NULL
        ]
    ))

    # command_with_pipe：包含管道子句的命令
    grammar_builder.group_append(ms_parser.create_group(
        name="command_with_pipe",
        rules=[
            ms_parser.create_rule(symbols=["command_with_redirection", "opt_pipe_list"],
                                  action=lambda x: ast.CommandWithPipe.create(command=x[0], pipe_list=x[1]))
        ]
    ))

    # -------------------------------------- 解析命令列表 --------------------------------------

    # command_relation：命令关系的终结符
    grammar_builder.group_append(ms_parser.create_group(
        name="command_relation",
        rules=[
            ms_parser.create_rule(symbols=[TType.ASCII_0x26_0x26],
                                  action=lambda _: ast.CommandRelationType.ASCII_0x26_0x26),
            ms_parser.create_rule(symbols=[TType.ASCII_0x7C_0x7C],
                                  action=lambda _: ast.CommandRelationType.ASCII_0x7C_0x7C),
        ]
    ))

    # relation_and_command：命令关系和命令的组合
    grammar_builder.group_append(ms_parser.create_group(
        name="relation_and_command",
        rules=[
            ms_parser.create_rule(symbols=["command_relation", "command_with_pipe"],
                                  action=lambda x: ast.CommandWithRelation(relation=x[0], command=x[1]))
        ]
    ))

    # relation_and_command_list：命令关系和命令的组合的列表
    grammar_builder.group_append(ms_parser.create_group(
        name="relation_and_command_list",
        rules=[
            ms_parser.create_rule(symbols=["relation_and_command_list", "relation_and_command"],
                                  action=ms_parser.template.action.LIST_APPEND_1),
            ms_parser.create_rule(symbols=["relation_and_command"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    # opt_command_with_relation_list：可选的命令关系和命令的组合的列表
    grammar_builder.group_append(ms_parser.create_group(
        name="opt_command_with_relation_list",
        rules=[
            ms_parser.create_rule(symbols=["relation_and_command_list"], action=ms_parser.template.action.RETURN_0),
            ms_parser.template.rule.EMPTY_RETURN_NULL
        ]
    ))

    # command_end_type：命令结束符
    grammar_builder.group_append(ms_parser.create_group(
        name="command_end_type",
        rules=[
            ms_parser.create_rule(symbols=[TType.ASCII_0x0A], action=lambda x: ast.CommandEndType.ASCII_0x0A),
            ms_parser.create_rule(symbols=[TType.ASCII_0x26], action=lambda x: ast.CommandEndType.ASCII_0x26),
            ms_parser.create_rule(symbols=[TType.ASCII_0x3B], action=lambda x: ast.CommandEndType.ASCII_0x3B),
        ]
    ))

    # command_with_list：命令列表（即完整的单个命令）
    grammar_builder.group_append(ms_parser.create_group(
        name="command_with_list",
        rules=[
            ms_parser.create_rule(
                symbols=["command_with_pipe", "opt_command_with_relation_list", "command_end_type"],
                action=lambda x: ast.CommandWithList.create(first_command=x[0], other_command_list=x[1],
                                                            end_type=x[2]),
                sr_priority_as=TType.IDENT
            )
        ]
    ))

    # -------------------------------------- 解析脚本 --------------------------------------

    grammar_builder.group_append(ms_parser.create_group(
        name="command_list",
        rules=[
            ms_parser.create_rule(symbols=["command_list", "command_with_list"],
                                  action=ms_parser.template.action.LIST_APPEND_1),
            ms_parser.create_rule(symbols=["command_with_list"], action=ms_parser.template.action.LIST_INIT_0)
        ]
    ))

    grammar_builder.group_append(ms_parser.create_group(
        name="script",
        rules=[
            ms_parser.create_rule(symbols=["command_list"],
                                  action=lambda x: ast.Script(command_list=x[0])),
            ms_parser.template.rule.EMPTY_RETURN_NULL
        ]
    ))

    return grammar_builder.build()


if __name__ == "__main__":
    import time

    start_time = time.time()

    parser = ms_parser.parser.ParserLALR1(build_grammar())
    source_code = ms_parser.compiler.compress_compile_lalr1(parser, import_list=[
        "from metasequoia_shell import ast"
    ])
    with open("parser.py", "w+", encoding="UTF-8") as file:
        for row in source_code:
            file.write(f"{row}\n")

    end_time = time.time()
    print(f"编译完成，耗时 {end_time - start_time:.3f} 秒")
