from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": ["pandas", "openpyxl", "tkinter"],
    "excludes": ["scipy", "matplotlib", "IPython", "numba", "pytest"],
    "optimize": 2,
}

setup(
    name="RechargeAnalyzer",
    version="1.0.0",
    description="集团会员充值明细统计工具",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "src/main.py",
            base="gui",
            target_name="充值明细统计.exe",
        )
    ],
)