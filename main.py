import enum
import json
import os
import requests
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from flask import Flask, request, Response, send_from_directory
from volcenginesdkarkruntime._exceptions import ArkAPIError
import threading
import uuid

from model_req import get_completions, get_ds_completions, get_ds_fc_completions, get_fc_completions
from utils import build_fc_prompt, build_messages, build_prompt, download_image
from dashscope import ImageSynthesis
# from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException

app = Flask(__name__)

# 初始化客户端

# 定义对话接口

# 假设这里已经有 client 和 ENDPOINT_ID 的定义
# 为了和前端的枚举对应，定义 Python 版本的枚举
class DrawingCategory(enum.Enum):
    DETAIL = '详情'
    MAIN_IMAGE = '主图'
    ACTIVITY = '活动'
    POSTER = '海报'

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 获取用户请求中的 JSON 数据
        data = request.get_json()
        # 验证请求中是否包含必要的字段
        if not data:
            return Response('{"error": "Missing JSON data in request"}', status=400, mimetype='application/json')

        design_style = data.get('designStyle')
        template_purpose = data.get('templatePurpose')
        size = data.get('size')
        isfc = data.get('isfc')
        recive_prompt = data.get('prompt')

        if not design_style or not template_purpose or not size:
            return Response('{"error": "Missing required fields in request: productCategory, drawingCategory, size"}', status=400, mimetype='application/json')

        # 验证 drawingCategory 是否为有效的枚举值
  
        # 验证 size 是否包含 width 和 height 字段
        width = size.get('width')
        height = size.get('height')
        if width is None or height is None:
            return Response('{"error": "Missing width or height in size field"}', status=400, mimetype='application/json')

        
        try:
          if isfc:
              print("recive_prompt",recive_prompt)
              messages = build_fc_prompt(recive_prompt)
              # generator = get_ds_fc_completions(messages)
              generator = get_fc_completions(messages)
              return Response(generator(), mimetype='text/plain')
          else:
              prompt = build_prompt(design_style, template_purpose, width, height)
              messages = build_messages(prompt)
              print("messages no",messages)
              generator = get_ds_completions(messages)
              # generator = get_completions(messages)
              return Response(generator(), mimetype='text/plain')
 

        except Exception as e:
          # 打印异常信息
          print(f"发生异常: {e}")
          # 可以根据实际情况返回错误响应
          return Response(f"发生异常: {e}", status=500, mimetype='text/plain')

    except Exception as e:
          # 打印异常信息
          print(f"发生异常: {e}")
          # 可以根据实际情况返回错误响应
          return Response(f"发生异常: {e}", status=500, mimetype='text/plain')

# 假设 ImageSynthesis 是您已有的一个类，保留它的导入方式
# from your_module import ImageSynthesis
# 假设 ArkAPIError 是您已有的一个异常类，保留它的导入方式
# from your_module import ArkAPIError


@app.route('/text-to-image', methods=['POST'])
def text_to_image():
    # 1. 解析请求数据
    try:
        data = request.get_json()
        if not data:
            return Response('{"error": "缺少JSON数据"}', status=400, mimetype='application/json')
        
        # 检查必要参数
        prompt = data.get('prompt')
        if not prompt:
            return Response('{"error": "缺少 prompt 参数"}', status=400, mimetype='application/json')
        
        # 如果 size 参数未提供，可以设置默认值
        size = data.get('size', '1024*1024')
    except Exception as e:
        return Response(json.dumps({"error": f"参数解析异常: {str(e)}"}), status=400, mimetype='application/json')
    
    # 2. 调用图像生成 API
    try:
        rsp = ImageSynthesis.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="wanx2.1-t2i-turbo",
            prompt=prompt,
            n=1,
            size=size
        )
        
        if rsp.status_code != HTTPStatus.OK:
            error_message = rsp.message if hasattr(rsp, "message") else "未知错误"
            return Response(
                json.dumps({
                    "error": "API请求失败", 
                    "status": rsp.status_code, 
                    "message": error_message
                }),
                status=500,
                mimetype='application/json'
            )
        
        # 3. 处理响应
        result_urls = []
        download_threads = []
        
        # 确保目录存在
        os.makedirs('./t2is', exist_ok=True)
        
        for result in rsp.output.results:
            # 生成唯一文件名
            file_name = f"{uuid.uuid4()}.jpg"
            file_path = f"./t2is/{file_name}"
            
            # 创建下载线程
            thread = threading.Thread(
                target=download_image,
                args=(result.url, file_path)
            )
            thread.start()
            download_threads.append(thread)
            
            # 将文件路径添加到结果列表
            result_urls.append({
                "original_url": result.url,
                "local_path": file_path,
                "file_name": file_name
            })
        
        # 可选：等待所有线程完成（注意：这仍会阻塞请求）
        # for thread in download_threads:
        #     thread.join()
        
        # 4. 返回成功响应
        return Response(
            json.dumps({
                "success": True, 
                "message": "图片生成成功", 
                "images": result_urls
            }),
            status=200,
            mimetype='application/json'
        )
    
    except Exception as e:
        print(f"生成图片异常: {e}")
        return Response(
            json.dumps({"error": "生成图片异常", "message": str(e)}),
            status=500,
            mimetype='application/json'
        )
T2IS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't2is')

@app.route('/t2is/<path:filename>')
def serve_t2is(filename):
    return send_from_directory(T2IS_FOLDER, filename)
if __name__ == '__main__':
    app.run(debug=True)