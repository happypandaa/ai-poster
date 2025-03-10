import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

DSClient = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def get_completions(messages,):

    response = client.chat.completions.create(
        # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",
        messages=messages,
        stream=True
    )

    def stream_generator():
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                # 逐块获取内容并生成
                content_chunk = chunk.choices[0].delta.content
                print(chunk.choices[0])
                yield content_chunk

    return stream_generator


def get_fc_completions(messages):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handleElement",
                "description": "处理Element类型的数据，可对多个Element对象进行创建、修改等操作",
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["text", "image", "user-image"],
                                "description": "元素的类型，可选值为 'text'、'image' 或 'user-image'"
                            },
                            "css": {
                                "type": "string",
                                "description": "CSS样式字符串，包含各种样式属性，必须是absolute定位,必须包含left,top,width,heigh,z-index属性。"
                            },
                            "cotent": {
                                "type": "string",
                                "description": "如果是text，则是文字内容"
                            },
                            "image": {
                                "type": "string",
                                "description": "仅在type是image的时候有，如果是logo，则logo，如果是用户图片，则是用户图片名称"
                            },
                            "design_method": {
                                "type": "string",
                                "description": "仅在type是image的时候有，详细描述图片设计的颜色，结构，风格,为设计师设计提供完整描述"
                            },
                            "reason": {
                                "type": "string",
                                "description": "这么设计的原因，可选"
                            }
                        },
                        "required": ["type", "css", "reason", "design_method"],
                        "description": "CssElement 对象的参数结构"
                    },
                    "description": "CssElement 对象数组的参数结构"
                }
            }
        }
    ]
    response = client.chat.completions.create(
        # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",
        messages=messages,
        tools=tools,
        stream=True
    )

    def stream_generator():
        for chunk in response:
            print("---111---")
            # print(chunk.choices[0].delta.tool_calls)

            if chunk.choices and chunk.choices[0].delta.tool_calls:
                # 逐块获取内容并生成
                content_chunk = chunk.choices[0].delta.tool_calls[0].function.arguments
                yield content_chunk.encode()

    return stream_generator


def get_ds_completions(messages):
    response = DSClient.chat.completions.create(
        # model="deepseek-v3",
        model="qwen-plus",
        messages=messages,
        stream=True
    )

    def stream_generator():
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                # 逐块获取内容并生成
                content_chunk = chunk.choices[0].delta.content
                print(chunk.choices[0])
                yield content_chunk

    return stream_generator


def get_ds_fc_completions(messages):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "handleElement",
                "description": "处理Element类型的数据，可对多个Element对象进行创建、修改等操作",
                "parameters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["text", "image", "rectangle"],
                                "description": "元素的类型，可选值为 'text'、'image' 或 'rectangle'"
                            },
                            "css": {
                                "type": "string",
                                "description": "CSS样式字符串，包含各种样式属性，必须是absolute定位,必须包含left,top,width,heigh,z-index属性。"
                            },
                            "cotent": {
                                "type": "string",
                                "description": "如果是text，则是文字内容"
                            },
                            "image": {
                                "type": "string",
                                "description": "仅在type是image的时候有，如果是logo，则logo，如果是用户图片，则是用户图片名称"
                            },
                            "design_method": {
                                "type": "string",
                                "description": "仅在type是image的时候有，详细描述图片设计的颜色，结构，风格"
                            },
                            "reason": {
                                "type": "string",
                                "description": "这么设计的原因，可选"
                            }
                        },
                        "required": ["type", "css", "reason"],
                        "description": "CssElement 对象的参数结构"
                    },
                    "description": "CssElement 对象数组的参数结构"
                }
            }
        }
    ]
    print(messages, tools)
    try:
        response = client.chat.completions.create(
            # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            model="deepseek-v3",
            messages=messages,
            tools=tools,
            stream=True
        )

        def stream_generator():
            for chunk in response:
                print(chunk.model_dump_json())
                print(chunk.choices[0].delta.tool_calls)

                if chunk.choices and chunk.choices[0].delta.tool_calls:
                    # 逐块获取内容并生成
                    content_chunk = chunk.choices[0].delta.tool_calls[0].function.arguments
                    yield content_chunk.encode()

        return stream_generator

    except Exception as e:
        print("error------------------------------------")
        print("response", e)
