"""
即梦AI客户端 - 处理binary_data_base64
"""
import json
import hashlib
import hmac
import datetime
import time
import base64
from pathlib import Path
import requests
from config import config


class VolcEngineSigner:
    """火山引擎签名"""

    @staticmethod
    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    @staticmethod
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = VolcEngineSigner.sign(key.encode("utf-8"), date_stamp)
        k_region = VolcEngineSigner.sign(k_date, region_name)
        k_service = VolcEngineSigner.sign(k_region, service_name)
        k_signing = VolcEngineSigner.sign(k_service, "request")
        return k_signing

    @staticmethod
    def sign_v4_request(access_key, secret_key, region, service, host, method, req_query, req_body):
        secret = secret_key
        t = datetime.datetime.now(datetime.timezone.utc)
        x_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")
        canonical_uri = "/"
        canonical_querystring = req_query
        signed_headers = "content-type;host;x-content-sha256;x-date"
        payload_hash = hashlib.sha256(req_body.encode("utf-8")).hexdigest()
        content_type = "application/json"
        canonical_headers = f"content-type:{content_type}\nhost:{host}\nx-content-sha256:{payload_hash}\nx-date:{x_date}\n"
        canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        algorithm = "HMAC-SHA256"
        credential_scope = f"{date_stamp}/{region}/{service}/request"
        string_to_sign = f"{algorithm}\n{x_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        signing_key = VolcEngineSigner.get_signature_key(secret, date_stamp, region, service)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        authorization_header = f"{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        headers = {
            "Content-Type": content_type,
            "Host": host,
            "X-Date": x_date,
            "X-Content-Sha256": payload_hash,
            "Authorization": authorization_header
        }
        return headers


class JimengClient:
    """即梦AI客户端"""

    def __init__(self):
        self.access_key_id = config.JIMENG_ACCESS_KEY_ID
        self.secret_access_key = config.JIMENG_SECRET_ACCESS_KEY
        self.region = "cn-north-1"
        self.service = "cv"
        self.host = "visual.volcengineapi.com"
        self.req_key = "jimeng_t2i_v40"
        print(f"即梦AI客户端初始化")
        print(f"  模型: {self.req_key}")

    def submit_task(self, prompt: str, width: int = 2048, height: int = 2048) -> str:
        """提交任务"""
        query_params = {"Action": "CVSync2AsyncSubmitTask", "Version": "2022-08-31"}
        body_params = {"req_key": self.req_key, "prompt": prompt, "seed": -1, "scale": 7.5, "return_url": False, "width": width, "height": height}
        req_query = "&".join([f"{k}={v}" for k, v in sorted(query_params.items())])
        req_body = json.dumps(body_params)
        headers = VolcEngineSigner.sign_v4_request(self.access_key_id, self.secret_access_key, self.region, self.service, self.host, "POST", req_query, req_body)
        url = f"https://{self.host}?{req_query}"
        response = requests.post(url, headers=headers, data=req_body, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 10000:
                return data.get("data", {}).get("task_id")
            else:
                raise Exception(f"提交失败: {data.get('message')}")
        else:
            raise Exception(f"HTTP {response.status_code}")

    def get_result(self, task_id: str, max_wait: int = 600) -> bytes:
        """获取结果"""
        print(f"  等待完成（最多{max_wait//60}分钟）...")
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                query_params = {"Action": "CVSync2AsyncGetResult", "Version": "2022-08-31"}
                body_params = {"req_key": self.req_key, "task_id": task_id}
                req_query = "&".join([f"{k}={v}" for k, v in sorted(query_params.items())])
                req_body = json.dumps(body_params)
                headers = VolcEngineSigner.sign_v4_request(self.access_key_id, self.secret_access_key, self.region, self.service, self.host, "POST", req_query, req_body)
                url = f"https://{self.host}?{req_query}"
                response = requests.post(url, headers=headers, data=req_body, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 10000:
                        result_data = data.get("data", {})
                        status = result_data.get("status")

                        # 处理不同的状态
                        if isinstance(status, int):
                            if status == 1:
                                pass  # 成功，继续处理
                            elif status == 0:
                                print(f"    处理中... {int(time.time() - start_time)}秒")
                                time.sleep(5)
                                continue
                            elif status == 2:
                                raise Exception(f"任务失败: {result_data.get('message')}")
                        elif isinstance(status, str):
                            if status == "success":
                                pass  # 成功，继续处理
                            elif status in ["in_queue", "processing"]:
                                print(f"    等待中... ({int(time.time() - start_time)}秒")
                                time.sleep(5)
                                continue

                        # 提取图片数据
                        if result_data.get("binary_data_base64") and len(result_data["binary_data_base64"]) > 0:
                            image_data = base64.b64decode(result_data["binary_data_base64"][0])
                            print(f"  [OK] 从base64获取图片: {len(image_data)} bytes")
                            return image_data
                        elif result_data.get("image_urls"):
                            image_urls = result_data.get("image_urls")
                            if image_urls and len(image_urls) > 0:
                                image_url = image_urls[0]
                                print(f"  [OK] 从URL获取图片...")
                                return requests.get(image_url, timeout=60).content

                    else:
                        print(f"    状态: {status}")
                        time.sleep(5)
                time.sleep(3)
            except Exception as e:
                print(f"    查询异常: {e}")
                time.sleep(5)
        raise Exception("超时")

    def generate_image(self, prompt: str, style: str = "cute", width: int = 2048, height: int = 2048) -> bytes:
        """生成图片"""
        styles = {"cute": "可爱Q版风格，高质量，细节丰富", "manga": "日漫风格，高质量，精致画工", "simple": "简笔画风格"}
        full_prompt = f"{styles.get(style, '可爱Q版')}，{prompt}"
        task_id = self.submit_task(full_prompt, width, height)
        print(f"  任务ID: {task_id}")
        return self.get_result(task_id)

    def generate_four_panel_comic(self, prompts: list, style: str = "cute", base_seed=None) -> list:
        """生成四格漫画"""
        paths = []
        for i, prompt in enumerate(prompts, 1):
            print(f"\n第{i}格...")
            try:
                if i > 1:
                    print(f"  等待5秒避免并发限制...")
                    time.sleep(5)
                data = self.generate_image(prompt, style, width=2048, height=2048)
                path = config.TEMP_DIR / f"panel_{i}.png"
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "wb") as f:
                    f.write(data)
                file_size = len(data)
                print(f"[OK] 完成 ({file_size/1024:.1f} KB)")
                paths.append(path)
            except Exception as e:
                print(f"[ERROR] 失败: {e}")
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (1024, 1024), '#f0f0f0')
                ImageDraw.Draw(img).rectangle([40, 40, 984, 984], outline='#e74c3c', width=8)
                path = config.TEMP_DIR / f"panel_{i}.png"
                img.save(path)
                paths.append(path)
        return paths


jimeng_client = JimengClient()
