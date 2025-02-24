"""
模拟执行 Shell 命令：export
"""

from metasequoia_shell.simu_env import SimuCommandInput
from metasequoia_shell.simu_env import SimuCommandOutput
from metasequoia_shell.simu_env import SimuExecutor
from metasequoia_shell.simu_env import SimuProcess
from metasequoia_shell.simu_env import SimuVariableString

__all__ = [
    "CommandExecutorExport"
]


class CommandExecutorExport(SimuExecutor):
    """模拟执行 Shell 命令：export"""

    def execute(self, simu_process: SimuProcess, command_input: SimuCommandInput) -> SimuCommandOutput:
        """模拟执行 Shell 命令：export"""
        return SimuCommandOutput(
            return_code=0,
            output_stream=SimuVariableString.create("", is_unknown=False)  # TODO 当前赋值语句直接执行，之后需考虑如何执行
        )
