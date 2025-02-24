"""
初始化模拟执行系统环境
"""

from typing import Callable, Optional

from metasequoia_shell.executor import CommandExecutorDate
from metasequoia_shell.executor import CommandExecutorEcho
from metasequoia_shell.executor import CommandExecutorExport
from metasequoia_shell.simu_env import SimuConfiguration
from metasequoia_shell.simu_env.system import SimuSystem

__all__ = [
    "init_simu_system"
]


def init_simu_system(configuration: Optional[SimuConfiguration] = None,
                     hook_func: Optional[Callable] = None,
                     hook_args: Optional[dict] = None
                     ) -> SimuSystem:
    """初始化模拟执行系统环境

    Returns
    -------
    SimuSystem
        模拟执行系统环境
    """
    simu_system = SimuSystem(configuration, hook_func=hook_func, hook_args=hook_args)
    simu_system.regist_executor("echo", CommandExecutorEcho())
    simu_system.regist_executor("date", CommandExecutorDate())
    simu_system.regist_executor("export", CommandExecutorExport())
    return simu_system
