"""
异常类
"""

from typing import List, Optional


class ShellCommandExecuteError(Exception):
    """Shell 命令执行异常"""

    def __init__(self, command_name: str, command_params: List[Optional[str]], reason: str):
        params_str = " ".join(command_params)
        super().__init__(f"Shell 命令执行异常：{command_name} {params_str}, reason = {reason}")
        self.command_name = command_name
        self.command_params = command_params
        self.reason = reason
