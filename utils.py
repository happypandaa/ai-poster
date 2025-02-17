
def build_prompt(product_category, drawing_category, width, height):
    """
    构建对话请求的提示信息
    :param product_category: 产品类别
    :param drawing_category: 绘制类别
    :param width: 尺寸宽度
    :param height: 尺寸高度
    :return: 拼接好的提示信息字符串
    """
    design_tip = f"这个布局用用户图片[mainpic]作为底图，上面最好包含3-4个文字元素，为文字设置背景和边框，元素之间的关系要合理，元素的颜色要搭配，元素的大小要合适，元素的位置要合理。足够吸引人，帮我返回的格式应该是handleElement的参数。"

    return f"这个的产品类别: {product_category}, 我们要绘制: {drawing_category.value}, 尺寸: {width}x{height}，{design_tip}"

def build_messages(prompt):
    """
    构建对话请求的消息列表
    :param prompt: 提示信息字符串
    :return: 消息列表
    """
    return [
        {"role": "system", "content": "你是一个平面设计师，帮我规划设计布局。"},
        {"role": "user", "content": prompt}
    ]

def get_req(messages,is_stream=False):
    req = {
        "model": "ep-20250214164426-t8s6k",
        "messages": messages,
        "stream": is_stream,
        "temperature": 0.8,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "handleElement",
                    "description": "处理Element类型的数据，可对Element对象进行创建、修改等操作",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["text", "image", "rectangle"],
                                "description": "元素的类型，可选值为 'text'、'image' 或 'rectangle'"
                            },
                            "position": {
                                "type": "object",
                                "properties": {
                                    "x": {
                                        "type": "number",
                                        "description": "元素在 x 轴的位置"
                                    },
                                    "y": {
                                        "type": "number",
                                        "description": "元素在 y 轴的位置"
                                    }
                                },
                                "required": ["x", "y"],
                                "description": "元素的位置信息，包含 x 和 y 坐标"
                            },
                            "backgroundColor": {
                                "type": "string",
                                "description": "元素的背景颜色"
                            },
                            "opacity": {
                                "type": "number",
                                "description": "元素的不透明度"
                            },
                            "border": {
                                "type": "object",
                                "properties": {
                                    "width": {
                                        "type": "number",
                                        "description": "边框的宽度"
                                    },
                                    "color": {
                                        "type": "string",
                                        "description": "边框的颜色"
                                    },
                                    "radius": {
                                        "type": "number",
                                        "description": "边框的圆角半径"
                                    }
                                },
                                "required": ["width", "color", "radius"],
                                "description": "元素的边框信息，包含宽度、颜色和圆角半径"
                            },
                            "size": {
                                "type": "object",
                                "properties": {
                                    "width": {
                                        "type": "number",
                                        "description": "元素的宽度"
                                    },
                                    "height": {
                                        "type": "number",
                                        "description": "元素的高度"
                                    }
                                },
                                "required": ["width", "height"],
                                "description": "元素的尺寸信息，包含宽度和高度"
                            },
                            "content": {
                                "type": "string",
                                "description": "文字元素特有的内容信息"
                            },
                            "font": {
                                "type": "object",
                                "properties": {
                                    "family": {
                                        "type": "string",
                                        "description": "字体家族"
                                    },
                                    "size": {
                                        "type": "number",
                                        "description": "字体大小"
                                    },
                                    "color": {
                                        "type": "string",
                                        "description": "字体颜色"
                                    },
                                    "bold": {
                                        "type": "boolean",
                                        "description": "是否加粗"
                                    },
                                    "italic": {
                                        "type": "boolean",
                                        "description": "是否倾斜"
                                    },
                                    "underline": {
                                        "type": "boolean",
                                        "description": "是否有下划线"
                                    }
                                },
                                "required": ["family", "size", "color"],
                                "description": "文字元素特有的字体信息"
                            },
                            "url": {
                                "type": "string",
                                "description": "图片元素特有的图片链接"
                            },
                            "display": {
                                "type": "string",
                                "enum": ["cover", "contain", "center"],
                                "description": "图片元素特有的显示方式，可选值为 'cover'、'contain' 或 'center'"
                            }
                        },
                        "required": [ "type", "position", "backgroundColor", "opacity", "size"],
                        "description": "Element 对象的参数结构"
                    }
                }
            }
        ]
    }
    return req