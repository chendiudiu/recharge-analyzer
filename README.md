# 充值明细统计工具

用于分析集团会员账户明细的充值数据统计工具。

## 功能

- 读取 Excel 文件（集团会员账户明细）
- 筛选"充值"和"充值退款"记录
- 按消费门店名称 + 充值金额分组统计
- 净笔数 = 正向充值笔数 - 退款笔数（相互抵消）
- 输出结果到新的 Excel 文件
- **微信支付充值** - 支持扫码充值（500/800/1500/2000元档位）

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

## 微信支付配置

程序支持微信扫码充值功能。使用前需要配置微信支付参数：

### 配置文件位置

编辑 `src/ui/wechat_pay.py`，修改 `WECHAT_CONFIG` 字典：

```python
WECHAT_CONFIG = {
    "APPID": "your_appid",           # 微信公众号APPID
    "MCHID": "your_mchid",           # 商户号
    "API_KEY": "your_api_key",        # API密钥（32位）
    "CERT_PATH": "apiclient_cert.pem",  # 商户证书
    "KEY_PATH": "apiclient_key.pem",    # 商户私钥
    "NOTIFY_URL": "https://your-domain.com/notify",  # 支付回调地址
}
```

### 获取微信支付参数

1. **APPID** - 登录微信公众平台获取
2. **MCHID** - 商户号，登录微信支付商户平台获取
3. **API_KEY** - API密钥，在商户平台设置（32位）
4. **证书** - 在商户平台下载 `apiclient_cert.pem` 和 `apiclient_key.pem`
5. **回调地址** - 需要一个公网可访问的HTTPS地址接收支付通知

### 未配置时

未配置微信支付参数时，程序自动进入演示模式，可以演示充值流程（5秒后自动确认）。

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
│   ├── main.py              # GUI 程序入口
│   ├── core/
│   │   ├── config.py        # 配置常量
│   │   └── processor.py     # 数据处理逻辑
│   ├── utils/
│   │   ├── excel_reader.py
│   │   └── excel_writer.py
│   └── ui/
│       ├── wechat_pay.py    # 微信支付核心
│       └── wechat_pay_gui.py # 微信支付界面
├── requirements.txt         # Python 依赖
└── build_windows.bat       # Windows 构建脚本
```