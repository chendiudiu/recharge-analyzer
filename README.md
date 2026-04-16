# 充值明细统计工具

用于分析集团会员账户明细的充值数据统计工具。

## 功能

- 读取 Excel 文件（集团会员账户明细）
- 筛选"充值"和"充值退款"记录
- 按消费门店名称 + 充值金额分组统计
- 净笔数 = 正向充值笔数 - 退款笔数（相互抵消）
- 输出结果到新的 Excel 文件

## 环境要求

- Python 3.8+
- Windows 10/11

## 快速开始

### 1. 安装依赖

```cmd
pip install -r requirements.txt
```

### 2. 运行程序

```cmd
python src/main.py
```

或直接双击运行 `dist\充值明细统计.exe`（如果已构建）

### 3. 构建 Windows 可执行程序

```cmd
pyinstaller --onefile --name "充值明细统计" -w src\main.py
```

构建完成后，可执行文件位于 `dist\充值明细统计.exe`

## 输入文件格式

Excel 文件需要包含以下列：
- `消费门店名称` - 门店名称
- `交易类型` - 包含"充值"或"充值退款"
- `交易金额（实付）` - 充值金额（正数）或退款金额（负数）

## 输出格式

生成的 Excel 文件包含以下列：
- `消费门店名称` - 门店名称
- `充值金额` - 充值金额
- `净笔数` - 净充值笔数（正向笔数 - 退款笔数）

## 项目结构

```
recharge_analyzer/
├── src/
│   ├── main.py           # GUI 程序入口
│   ├── core/
│   │   └── processor.py  # 数据处理逻辑
│   └── utils/
│       ├── excel_reader.py
│       └── excel_writer.py
├── requirements.txt      # Python 依赖
└── build_windows.bat    # Windows 构建脚本
```