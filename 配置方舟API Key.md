# 配置火山方舟API Key

## 配置步骤

### 1. 打开配置文件

使用文本编辑器打开：
```
D:\自动化生产动漫工具\comic-generator\.env
```

### 2. 添加API Key

在文件末尾或合适位置，找到或添加这一行：
```bash
JIMENG_ARK_API_KEY=你的方舟API_Key填在这里
```

### 3. 替换为你的API Key

将 `你的方舟API_Key填在这里` 替换为你在火山方舟控制台获取的API Key。

示例：
```bash
JIMENG_ARK_API_KEY=ark-1234567890abcdef
```

### 4. 保存文件

保存并关闭.env文件。

## 验证配置

运行测试脚本验证配置是否正确：

```bash
cd D:\自动化生产动漫工具\comic-generator
python test_jimeng_api.py
```

如果看到 "API连接成功!"，说明配置正确！

## 开始生成漫画

配置成功后，运行完整测试：

```bash
python test_full.py
```

## API Key格式说明

火山方舟的API Key格式通常是：
- 以 `ark-` 开头
- 后面跟一串字母数字组合
- 示例：`ark-abc123def456789`

## 如果API Key无效

如果测试失败，请检查：
1. API Key是否完整复制（没有多余空格）
2. API Key是否来自火山方舟控制台（不是火山引擎控制台）
3. API Key是否已过期

## 获取火山方舟API Key

如果还没有API Key：

1. 访问火山方舟控制台：https://console.volcengine.com/ark
2. 创建推理接入点
3. 选择模型：豆包-Seedream（图像生成）
4. 在接入点详情页获取API Key
