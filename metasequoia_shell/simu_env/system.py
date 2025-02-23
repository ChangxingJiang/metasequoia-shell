"""
模拟执行系统环境
"""

import abc
from typing import Callable, Dict, List, Optional

from metasequoia_shell.simu_env.command_interactive import SimuCommandInput
from metasequoia_shell.simu_env.command_interactive import SimuCommandOutput
from metasequoia_shell.simu_env.configuration import SimuConfiguration
from metasequoia_shell.simu_env.variable import SimuVariable
from metasequoia_shell.simu_env.variable import SimuVariableString

__all__ = (
    "SimuSystem",
    "SimuProcess",
    "SimuExecutor",
)


class SimuSystem:
    """模拟执行系统环境

    模拟执行系统环境，负责维护：
    - 模拟的进程之间的关系
    - 模拟的文件系统
    """

    def __init__(self,
                 configuration: Optional[SimuConfiguration] = None,
                 default_shell_flags: str = "himBH",
                 hook_func: Optional[Callable] = None,
                 hook_args: Optional[dict] = None):
        """

        Parameters
        ----------
        configuration : Optional[SimuConfiguration]
            模拟执行配置
        default_shell_flags : str, default = "himBH"
            Shell 的默认标志
        hook_func : Optional[Callable], default = None
            执行命令的回调函数
        hook_args : Optional[dict], default = None
            执行命令的回调函数的关键字参数
        """
        if configuration is None:
            configuration = SimuConfiguration()

        self._configuration = configuration
        self._default_shell_flags = default_shell_flags

        self._process_idx = 1

        # 登记执行器的字典
        self.regist_executor_dict: Dict[str, "SimuExecutor"] = {}

        # 回调函数和回调函数的参数
        self.hook_func = hook_func  # 回调函数
        self.hook_args = hook_args  # 回调函数的参数

    @property
    def configuration(self) -> SimuConfiguration:
        return self._configuration

    @property
    def default_shell_flags(self) -> str:
        return self._default_shell_flags

    def regist_executor(self, name: str, executor: "SimuExecutor") -> None:
        """注册执行器"""
        self.regist_executor_dict[name] = executor

    def remove_executor(self, name: str) -> None:
        """移除执行器"""
        del self.regist_executor_dict[name]

    def create_process(self) -> "SimuProcess":
        process_id = self._process_idx
        self._process_idx += 1
        return SimuProcess(
            system=self,
            process_id=process_id
        )


class SimuProcess:
    """模拟执行进程"""

    def __init__(self,
                 system: SimuSystem,
                 process_id: int,
                 script_name: str = "",
                 pos_params: Optional[List[str]] = None):
        """

        Parameters
        ----------
        system : SimuSystem
            模拟执行系统环境
        process_id : int
            模拟执行环境的进程 ID
        script_name : str, default = ""
            模拟执行环境的 shell 名称或脚本名称
        pos_params : Optional[List[str]], default = None
            模拟执行环境的 shell 命令的位置参数
        """
        if pos_params is None:
            pos_params = []

        self._system = system
        self._process_id = process_id
        self._script_name = script_name
        self._param_space = {}  # 参数空间
        self._file_space = {}  # 文件空间

        # 初始化位置参数
        self._pos_params = pos_params

        # 初始化其他参数
        self._last_status: Optional[int] = None  # 上一个前台管道的退出状态
        self._last_sub_process_id: Optional[int] = None  # 上一个放入后台运行的作业的进程 ID  TODO 待增加修改逻辑

        # 未知命令（无法执行）
        self._unknown_command_list = []

    @property
    def system(self) -> SimuSystem:
        return self._system

    @property
    def process_id(self) -> int:
        return self._process_id

    def set_script_name(self, script_name: str) -> None:
        """设置脚本名称"""
        self._script_name = script_name

    def get_script_name(self) -> str:
        """获取脚本名称"""
        return self._script_name

    def set_pos_params(self, pos_params: List[str]) -> None:
        """设置位置参数的列表"""
        self._pos_params = pos_params

    def get_pos_param(self, idx: int, default: Optional[str] = None) -> Optional[str]:
        """获取指定位置参数"""
        if idx >= len(self._pos_params):
            return default
        return self._pos_params[idx - 1]

    def get_pos_params(self) -> List[str]:
        """获取所有位置参数的列表"""
        return self._pos_params

    def set_param(self, key: str, value: SimuVariable) -> None:
        """设置参数值"""
        self._param_space[key] = value

    def del_param(self, key: str) -> None:
        """移除参数值"""
        del self._param_space[key]

    def get_param(self, key: str, default: Optional[SimuVariable] = None) -> SimuVariable:
        """获取参数值"""
        if default is None:
            default = SimuVariable.unknown()
        return self._param_space.get(key, default)

    def write_file(self, path: str, data: str, mode: str = "w") -> None:
        """将数据写入到文件"""
        if mode == "w" or (mode == "a" and path not in data):
            self._file_space[path] = data
        elif mode == "a" and path in data:
            self._file_space[path] += data

    def read_file(self, path: str) -> Optional[str]:
        """读取文件中的内容"""
        return self._file_space.get(path)

    def set_status(self, status: int) -> None:
        """设置任务的返回状态，作为下一个命令的上一个前台管道的返回状态"""
        self._last_status = status

    def get_last_status(self) -> Optional[int]:
        return self._last_status

    def get_last_sub_process_id(self) -> Optional[int]:
        return self._last_sub_process_id

    def add_unknown_command(self, source: str, reason: str) -> None:
        """添加未知的执行命令"""
        self._unknown_command_list.append((source, reason))

    def execute_simple_command(self, words: List[str], input_stream: Optional[str]) -> SimuVariable:
        """模拟执行命令"""
        # 过滤命令中的空白元素
        words = [word for word in words if word != ""]

        # 过滤空命令
        if len(words) == 0:
            return SimuVariable.empty()

        command_name = words[0]
        command_params = words[1:]

        command_input = SimuCommandInput(
            command_name=command_name,
            command_params=command_params,
            input_stream=input_stream
        )

        # 调用回调函数
        if self.system.hook_func is not None:
            self.system.hook_func(self, command_input, **self.system.hook_args)

        # 模拟执行命令
        if command_name in self.system.regist_executor_dict:
            executor = self.system.regist_executor_dict[command_name]
            command_output = executor.execute(self, command_input)
            return SimuVariableString.create(command_output.output_stream)

        self.add_unknown_command(str(words), "unknown command")
        return SimuVariable.unknown()


class SimuExecutor(abc.ABC):
    """模拟命令执行器"""

    @abc.abstractmethod
    def execute(self, simu_process: SimuProcess, command_input: SimuCommandInput) -> SimuCommandOutput:
        """模拟执行方法"""
