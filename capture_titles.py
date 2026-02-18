import re
from mitmproxy import http

class VideoTitleFilter:
    def response(self, flow: http.HTTPFlow):
        # 仅处理包含文本内容的响应
        if flow.response and flow.response.content:
            content = flow.response.get_text()

            # 正则解释：
            # "videoDetails"\s*:\s*\{  -> 匹配 videoDetails 后面跟着左大括号
            # .*?                      -> 非贪婪匹配中间任何内容（跳过其它字段）
            # "title"\s*:\s*"([^"]+)"  -> 捕获 title 字段的双引号内的内容
            # re.DOTALL                -> 允许 . 匹配换行符，应对格式化后的 JSON
            pattern = r'"videoDetails"\s*:\s*\{.*?"title"\s*:\s*"([^"]+)"'
            
            # 查找所有匹配项
            titles = re.findall(pattern, content, re.DOTALL)

            for title in titles:
                # 检测是否包含中文字符 (Unicode 范围: \u4e00-\u9fa5)
                if re.search(r'[\u4e00-\u9fa5]', title):
                    print(f"!!! 拦截到中文标题: {title}")
                    
                    # 构造拒绝响应
                    flow.response = http.Response.make(
                        403, 
                        b"Blocked: Chinese characters detected in video title.",
                        {"Content-Type": "text/plain"}
                    )
                    break 

addons = [
    VideoTitleFilter()
]
