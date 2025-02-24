"""
模拟执行 Shell 命令：date
"""

import datetime

from metasequoia_shell.simu_env import SimuCommandInput
from metasequoia_shell.simu_env import SimuCommandOutput
from metasequoia_shell.simu_env import SimuExecutor
from metasequoia_shell.simu_env import SimuProcess
from metasequoia_shell.simu_env import SimuVariableString

__all__ = [
    "CommandExecutorDate"
]


class CommandExecutorDate(SimuExecutor):
    """模拟执行 Shell 命令：date"""

    def execute(self, simu_process: SimuProcess, command_input: SimuCommandInput) -> SimuCommandOutput:
        """模拟执行 Shell 命令：date"""

        # 初始化参数默认值
        current = datetime.datetime.now()
        format_string = "%Y-%m-%d %H:%M:%S"

        # 遍历参数
        idx = 0
        params = command_input.command_params
        while idx < len(params):
            param = params[idx]
            if param == "-d":
                idx += 1
                if idx >= len(params):
                    print(f"命令执行失败: date {params}, -d 后没有参数")
                    return SimuCommandOutput(return_code=0, output_stream=SimuVariableString.create("", True))  # TODO 待优化
                if params[idx] == "yesterday":
                    current -= datetime.timedelta(days=1)
                else:
                    print(f"命令执行失败: date {params}, -d 后参数未知")
                    return SimuCommandOutput(return_code=0, output_stream=SimuVariableString.create("", True))  # TODO 待优化
            elif param.startswith("+"):
                format_string = param[1:]
            idx += 1

        return SimuCommandOutput(
            return_code=0,
            output_stream=SimuVariableString.create(current.strftime(format_string))
        )
