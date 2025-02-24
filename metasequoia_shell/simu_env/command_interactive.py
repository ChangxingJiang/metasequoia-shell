"""
模拟执行的命令交互信息类
"""

import dataclasses
from typing import List, Optional

from metasequoia_shell.simu_env.variable import SimuVariableString

__all__ = [
    "SimuCommandInput",
    "SimuCommandOutput"
]


@dataclasses.dataclass(slots=True)
class SimuCommandInput:
    """模拟执行的命令输入信息类"""

    command_name: str = dataclasses.field(kw_only=True)  # 命令名称
    command_params: List[Optional[str]] = dataclasses.field(kw_only=True)  # 命令参数
    input_stream: Optional[str] = dataclasses.field(kw_only=True, default=None)  # 输入流


@dataclasses.dataclass(slots=True)
class SimuCommandOutput:
    """模拟执行的命令输出信息类"""

    return_code: int = dataclasses.field(kw_only=True)
    output_stream: SimuVariableString = dataclasses.field(kw_only=True)  # 如果为 None 则表示无法推断
