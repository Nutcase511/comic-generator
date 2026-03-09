# ⚠️ 即梦AI API 集成说明

## 当前状态

即梦AI（字节跳动）的API集成需要进一步确认。代码中已经创建了基础框架，但可能需要根据实际API文档进行调整。

## 需要确认的信息

### 1. API地址
当前配置中的地址是：
```
JIMENG_API_URL = "https://api.jimeng.jianying.com/api"
```

**需要确认**：
- 实际的API基础地址是什么？
- 是否有官方SDK可以使用？

### 2. 认证方式
当前使用的是Bearer Token：
```python
headers = {
    "Authorization": f"Bearer {self.api_key}"
}
```

**需要确认**：
- 实际使用的认证方式（API Key / Access Token / OAuth）
- 密钥在哪里获取？

### 3. API调用方式
当前假设的调用方式：
```python
POST /image/generate
{
    "prompt": "画面描述",
    "negative_prompt": "负面描述",
    "width": 512,
    "height": 512,
    "seed": 12345
}
```

**需要确认**：
- 实际的API端点路径
- 请求参数格式
- 响应数据格式

## 🔄 备选方案

如果即梦AI没有公开API或无法集成，可以考虑以下免费替代方案：

### 方案1：LiblibAI ⭐ 推荐
- ✅ 完善的API文档
- ✅ 每天免费额度
- ✅ 专业的SD模型
- 📝 文档：https://www.liblib.art/docs

### 方案2：火山引擎（字节跳动其他产品）
- ✅ 官方API稳定
- ✅ 有免费额度
- 📝 文档：https://www.volcengine.com/

### 方案3：Stable Diffusion本地部署
- ✅ 完全免费
- ✅ 效果最佳
- ❌ 需要显卡支持

### 方案4：其他免费API
- **堆友**（阿里）：免费额度
- **文心一格**（百度）：有免费试用
- **通义万相**（阿里）：稳定可用

## 🛠️ 如何调整代码

如果需要切换到其他AI绘画服务，只需要修改 `api_clients/jimeng_client.py` 文件：

1. 修改 `JIMENG_API_URL` 为新的API地址
2. 调整 `generate_image()` 方法的请求参数
3. 适配响应数据的解析逻辑

示例：
```python
# 以LiblibAI为例
class LiblibClient:
    API_URL = "https://api.liblib.art/api/v1"

    def generate_image(self, prompt, **kwargs):
        # 根据LiblibAI的API文档调整
        pass
```

## 📞 下一步

请告诉我：
1. 你是否已经找到即梦AI的官方API文档？
2. 如果没有，你想尝试哪个备选方案？

我会根据你的选择调整代码！
