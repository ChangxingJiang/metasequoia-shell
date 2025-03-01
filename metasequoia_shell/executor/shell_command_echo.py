"""
模拟执行 Shell 命令：echo
"""

from metasequoia_shell.simu_env import SimuCommandInput
from metasequoia_shell.simu_env import SimuCommandOutput
from metasequoia_shell.simu_env import SimuExecutor
from metasequoia_shell.simu_env import SimuProcess
from metasequoia_shell.simu_env import SimuVariableString

__all__ = [
    "CommandExecutorEcho"
]


class CommandExecutorEcho(SimuExecutor):
    """模拟执行 Shell 命令：echo"""

    def execute(self, simu_process: SimuProcess, command_input: SimuCommandInput) -> SimuCommandOutput:
        """模拟执行 Shell 命令：echo"""
        if command_input.command_params == [None]:
            raise
        return SimuCommandOutput(
            return_code=0,
            output_stream=SimuVariableString.create_by_array(command_input.command_params, sep=" ")  # TODO 分隔符待验证
        )
