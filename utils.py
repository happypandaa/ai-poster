import requests


def build_prompt(design_style, template_purpose, width, height):
    """
    构建设计规范文档，用于指导多位设计师实施设计
    :param design_style: 设计风格
    :param template_purpose: 模板用途
    :param width: 尺寸宽度(像素)
    :param height: 尺寸高度(像素)
    :return: 拼接好的设计规范文档
    """
    essential_parameters = (
        f"每个元素必须明确定义以下核心参数：\n"
        f"1. 元素类别：明确标注是主体图片/文字/装饰图片/背景图片\n"
        f"2. 位置参数：精确的X,Y坐标(单位px)，以左上角为基准点\n"
        f"3. 尺寸参数：宽度和高度(单位px)，或半径(圆形)，或具体路径点(复杂形状)\n"
        f"4. 层级顺序：z-index值或前后层级描述，确保元素间正确的重叠关系\n"
        f"5. 颜色值：所有颜色必须使用十六进制码(如#FF5733)，必要时包含透明度\n"
    )

    element_specifications = (
        f"设计需包含以下类型元素，每种元素都需定义上述核心参数外，还需提供专属参数：\n\n"

        f"1. 主体用户图片(mainpic)：\n"
        f"   - 裁剪方式(方形/圆形/自定义形状)\n"
        f"   - 边框(粗细、颜色、样式)、圆角值\n"
        f"   - 阴影/滤镜效果(如有)\n\n"

        f"2. 文字元素：\n"
        f"   - 文字内容示例\n"
        f"   - 字体系列、大小(px)、字重、样式\n"
        f"   - 对齐方式、行高、字间距\n"
        f"   - 文字装饰(下划线/阴影/背景等)\n\n"

        f"3. 装饰图片元素(需特别详细描述)：\n"
        f"   - 图片主题与内容的详细描述(具体到场景、物品、人物等)\n"
        f"   - 图片风格(写实/卡通/插画/线条等)的明确要求\n"
        f"   - 图片色调与配色(亮度、饱和度、色相倾向等)\n"
        f"   - 图片质感(平面/立体/材质表现等)\n"
        f"   - 图片情绪表达与设计意图\n"
        f"   - 与整体设计的风格匹配说明\n"
        f"   - 裁剪/蒙版具体效果\n"
        f"   - 边框要求(有无、粗细、颜色、样式)\n"
        f"   - 圆角要求(有无、大小)\n"
        f"   - 阴影效果(有无、偏移、模糊度、颜色)\n"
        f"   - 透明度/滤镜具体参数\n"
        f"   - 旋转角度(如适用)\n"
        f"   - 在整体设计中的作用与布局关系\n\n"

        f"4. 背景图片(需特别详细描述)：\n"
        f"   - 背景图片主题与内容的详细描述\n"
        f"   - 背景风格(抽象/具象/纹理/图案等)\n"
        f"   - 色调要求(明确的色调范围和主色调)\n"
        f"   - 饱和度与明度的明确要求\n"
        f"   - 背景复杂度(简洁/适中/复杂)及视觉重量\n"
        f"   - 与前景元素的对比关系\n"
        f"   - 平铺/拉伸/居中等显示方式\n"
        f"   - 图片渐变/虚化/蒙版效果的具体参数\n"
        f"   - 纹理细节要求(如有)\n"
        f"   - 背景图片如何衬托主题的说明\n\n"

        f"5. 纯色/渐变背景(如适用)：\n"
        f"   - 纯色：精确的十六进制色值\n"
        f"   - 渐变：类型(线性/径向)、方向、各色标位置及色值\n"
        f"   - 与整体设计风格的关系说明\n"
    )

    design_rules = (
        f"设计规则要点：\n"
        f"1. 提供明确的设计风格与主配色方案\n"
        f"2. 所有元素必须有精确的像素级定位与尺寸\n"
        f"3. 文字在图片上方时，必须确保可读性\n"
        f"4. 装饰图片与背景图片必须详尽描述，确保设计师能准确把握风格和要求\n"
        f"5. 图片的色调、风格、质感描述必须具体而非笼统\n"
        f"6. 元素间距、层级关系必须明确定义\n"
        f"7. 整体视觉平衡与引导动线须清晰描述\n"
        f"8. 重要的是各种元素数量不拘泥，可以没有某种元素，也可以有多个某种元素。\n"
    )

    output_format = (
        f"输出格式：\n"
        f"1. 设计风格与配色：\n"
        f"2. 元素列表：按从背景到前景顺序排列，包含：\n"
        f"   - 元素类别\n"
        f"   - 核心参数(位置、尺寸、层级、颜色)\n"
        f"   - 元素专属详细参数\n"
        f"   - 设计意图与整体关系说明\n"
    )

    return (f"设计规范文档\n\n"
            f"项目信息:\n"
            f"- 设计风格: {design_style}\n"
            f"- 用途: {template_purpose}\n"
            f"- 画布尺寸: {width}x{height}px\n\n"
            f"{essential_parameters}\n\n"
            f"{element_specifications}\n\n"
            f"{design_rules}\n\n"
            f"{output_format}\n\n"
            f"请根据以上规范提供完整元素清单，确保特别详细描述所有图片类元素(背景图片和装饰图片)的具体风格、色调、内容要求，使设计师能准确理解并实施。")


def build_fc_prompt(message):
    fc_prompt = (f"参照下面这些描述和设计元素，生成代码，按照格式生成调用handleElement的参数，"
                 f"注意是生成代码，保证可用。要注意元素之间的位置尺寸。"
                 f"注意top,left 是元素左上角距离画布左上角距离，不要让元素超出画布"
                 f"注意z-index,注意层次,用户图片放在最小，点缀元素大。"
                 f"文字背景则在文字元素设置，无需单独元素，"
                 f"可以适当调整他们的关系，{message}")
    return [
        {"role": "system", "content": "你是一个平面设计师，帮我规划设计布局。按照格式生成调用handleElement的参数，注意是生成代码，保证可用。"},
        {"role": "user", "content": fc_prompt}
    ]


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
