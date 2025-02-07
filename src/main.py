import os
from flask import Flask, request, Response
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime._exceptions import ArkAPIError

app = Flask(__name__)

# 初始化客户端
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

# 定义推理接入点 ID，需替换为你自己的
ENDPOINT_ID = "ep-20250207102932-ckt49"

# 定义对话接口
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 获取用户请求中的问题
        data = request.get_json()
        prompt = data.get('prompt')
        if not prompt:
            return Response('{"error": "Missing \'prompt\' in request"}', status=400, mimetype='application/json')

        # 构建对话请求的消息列表
        messages = [
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            {"role": "user", "content": prompt}
        ]

        # 发起流式对话请求
        stream = client.chat.completions.create(
            model=ENDPOINT_ID,
            messages=messages,
            stream=True
        )

        def generate():
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        return Response(generate(), mimetype='text/plain')

    except ArkAPIError as e:
        error_response = f'{{"error": "API exception: {str(e)}"}}'
        return Response(error_response, status=500, mimetype='application/json')
    except Exception as e:
        error_response = f'{{"error": "Unexpected error: {str(e)}"}}'
        return Response(error_response, status=500, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)