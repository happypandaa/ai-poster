import time
import json
import os
import uuid
import threading
from http import HTTPStatus
from flask import request, Response
from queue import Queue
from threading import Lock
from dashscope import ImageSynthesis

# 创建一个请求队列和一个锁
request_queue = Queue()
queue_lock = Lock()
processing_thread = None
is_processing = False


def process_queue():
    """处理队列中的请求，每次只处理一个，处理完后等待1秒"""
    global is_processing

    while not request_queue.empty():
        with queue_lock:
            if request_queue.empty():  # 再次检查，防止竞态条件
                is_processing = False
                return

            # 从队列获取下一个请求
            req_data = request_queue.get()

        try:
            # 处理请求
            result = process_single_request(req_data)

            # 发送结果给客户端
            # 这里需要一个回调机制来通知客户端，因为我们现在是异步处理
            # 可以使用WebSocket、Server-Sent Events或在数据库中存储结果
            # 简单起见，这个例子中我们假设有一个通知函数
            notify_client(req_data['client_id'], result)

        except Exception as e:
            print(f"处理请求异常: {e}")
            notify_client(req_data['client_id'], {
                "error": "处理请求异常",
                "message": str(e)
            })

        # 等待1秒钟再处理下一个请求
        time.sleep(1)

    with queue_lock:
        is_processing = False


def download_image(url, file_path):
    """下载图片到指定路径"""
    import requests
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"图片已保存到 {file_path}")
            return True
        else:
            print(f"下载图片失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"下载图片异常: {e}")
        return False


def process_single_request(req_data):
    """处理单个图像生成请求"""
    try:
        prompt = req_data.get('prompt')
        size = req_data.get('size', '1024*1024')

        # 调用图像生成 API
        rsp = ImageSynthesis.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="wanx2.1-t2i-turbo",
            prompt=prompt,
            n=1,
            size=size
        )

        if rsp.status_code != HTTPStatus.OK:
            error_message = rsp.message if hasattr(rsp, "message") else "未知错误"
            return {
                "error": "API请求失败",
                "status": rsp.status_code,
                "message": error_message
            }

        # 处理响应
        result_urls = []

        # 确保目录存在
        os.makedirs('./t2is', exist_ok=True)

        # 注意：这里我们不再使用多线程下载，而是按顺序下载
        for result in rsp.output.results:
            print('image result', result)
            # 生成唯一文件名
            file_name = f"{uuid.uuid4()}.jpg"
            file_path = f"./t2is/{file_name}"

            # 直接下载图片，不使用线程
            download_success = download_image(result.url, file_path)

            # 将文件路径添加到结果列表
            result_urls.append({
                "original_url": result.url,
                "local_path": file_path,
                "file_name": file_name,
                "download_success": download_success
            })

        return {
            "success": True,
            "message": "图片生成成功",
            "images": result_urls
        }

    except Exception as e:
        print(f"生成图片异常: {e}")
        return {
            "error": "生成图片异常",
            "message": str(e)
        }


def notify_client(client_id, result):
    """通知客户端处理结果"""
    # 这里应该实现您的客户端通知逻辑
    # 可以是WebSocket消息、数据库更新等
    print(f"通知客户端 {client_id}: {result}")
    # 实际实现省略...


@app.route('/text-to-image', methods=['POST'])
def text_to_image():
    global is_processing, processing_thread

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

        # 为每个请求生成一个客户端ID
        client_id = str(uuid.uuid4())

        # 创建请求数据对象
        req_data = {
            'client_id': client_id,
            'prompt': prompt,
            'size': size
        }

        # 将请求添加到队列
        with queue_lock:
            request_queue.put(req_data)

            # 如果没有正在处理的线程，启动一个新线程
            if not is_processing:
                is_processing = True
                processing_thread = threading.Thread(target=process_queue)
                processing_thread.daemon = True  # 设置为守护线程
                processing_thread.start()

        # 2. 返回接受请求的响应
        return Response(
            json.dumps({
                "success": True,
                "message": "请求已接受，正在处理中",
                "request_id": client_id  # 返回请求ID给客户端用于后续查询
            }),
            status=202,  # 202 Accepted
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            json.dumps({"error": "请求处理异常", "message": str(e)}),
            status=500,
            mimetype='application/json'
        )
