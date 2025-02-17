import enum
import os
from flask import Flask, request, Response
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime._exceptions import ArkAPIError

from utils import build_messages, build_prompt, get_req

app = Flask(__name__)

# 初始化客户端
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

# 定义推理接入点 ID，需替换为你自己的
ENDPOINT_ID = "ep-20250207102932-ckt49"

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

        product_category = data.get('productCategory')
        drawing_category_str = data.get('drawingCategory')
        size = data.get('size')

        if not product_category or not drawing_category_str or not size:
            return Response('{"error": "Missing required fields in request: productCategory, drawingCategory, size"}', status=400, mimetype='application/json')

        # 验证 drawingCategory 是否为有效的枚举值
        try:
            drawing_category = DrawingCategory(drawing_category_str)
        except ValueError:
            valid_values = [cat.value for cat in DrawingCategory]
            return Response(f'{{"error": "Invalid drawingCategory. Valid values are: {valid_values}"}}', status=400, mimetype='application/json')

        # 验证 size 是否包含 width 和 height 字段
        width = size.get('width')
        height = size.get('height')
        if width is None or height is None:
            return Response('{"error": "Missing width or height in size field"}', status=400, mimetype='application/json')

        # 调用独立方法构建提示信息和消息列表
        prompt = build_prompt(product_category, drawing_category, width, height)
        print("prompt",prompt)
        messages = build_messages(prompt)
        print("messages",messages)
        req = get_req(messages,is_stream=False)
        print("req",req)
        
        try:
          response = client.chat.completions.create(**req)
          full_content = ""
          print("response",response)
          if response.choices and response.choices[0].message.content:
            full_content = response.choices[0].message.content

          return Response(full_content, mimetype='text/plain')

          # stream = client.chat.completions.create(**req)
          # def generate():
          #     for chunk in stream:
          #         if chunk.choices and chunk.choices[0].delta.content:
          #             print("chunk",chunk)
          #             yield chunk.choices[0].delta.content

          # return Response(generate(), mimetype='text/plain')

        except Exception as e:
          # 打印异常信息
          print(f"发生异常: {e}")
          # 可以根据实际情况返回错误响应
          return Response(f"发生异常: {e}", status=500, mimetype='text/plain')

    except ArkAPIError as e:
        error_response = f'{{"error": "API exception: {str(e)}"}}'
        return Response(error_response, status=500, mimetype='application/json')
    except Exception as e:
        error_response = f'{{"error": "Unexpected error: {str(e)}"}}'
        return Response(error_response, status=500, mimetype='application/json')
    
def chatwithsteam():
    try:
        # 获取用户请求中的 JSON 数据
        data = request.get_json()
        # 验证请求中是否包含必要的字段
        if not data:
            return Response('{"error": "Missing JSON data in request"}', status=400, mimetype='application/json')

        product_category = data.get('productCategory')
        drawing_category_str = data.get('drawingCategory')
        size = data.get('size')

        if not product_category or not drawing_category_str or not size:
            return Response('{"error": "Missing required fields in request: productCategory, drawingCategory, size"}', status=400, mimetype='application/json')

        # 验证 drawingCategory 是否为有效的枚举值
        try:
            drawing_category = DrawingCategory(drawing_category_str)
        except ValueError:
            valid_values = [cat.value for cat in DrawingCategory]
            return Response(f'{{"error": "Invalid drawingCategory. Valid values are: {valid_values}"}}', status=400, mimetype='application/json')

        # 验证 size 是否包含 width 和 height 字段
        width = size.get('width')
        height = size.get('height')
        if width is None or height is None:
            return Response('{"error": "Missing width or height in size field"}', status=400, mimetype='application/json')

        # 调用独立方法构建提示信息和消息列表
        prompt = build_prompt(product_category, drawing_category, width, height)
        print("prompt",prompt)
        messages = build_messages(prompt)
        print("messages",messages)
        req = get_req(messages)
        print("req",req)
        
        try:
          stream = client.chat.completions.create(**req)
          def generate():
              for chunk in stream:
                  if chunk.choices and chunk.choices[0].delta.content:
                      print("chunk",chunk)
                      yield chunk.choices[0].delta.content

          return Response(generate(), mimetype='text/plain')
        
        
        except Exception as e:
          # 打印异常信息
          print(f"发生异常: {e}")
          # 可以根据实际情况返回错误响应
          return Response(f"发生异常: {e}", status=500, mimetype='text/plain')

    except ArkAPIError as e:
        error_response = f'{{"error": "API exception: {str(e)}"}}'
        return Response(error_response, status=500, mimetype='application/json')
    except Exception as e:
        error_response = f'{{"error": "Unexpected error: {str(e)}"}}'
        return Response(error_response, status=500, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)