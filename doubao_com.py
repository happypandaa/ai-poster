from volcenginesdkarkruntime import Ark
import os
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

# 定义推理接入点 ID，需替换为你自己的
ENDPOINT_ID = "ep-20250207102932-ckt49"

def get_doubao_completions(messages):
    # 调用通用推理接口
    response = client.chat.completions.create(
      model=ENDPOINT_ID,
      messages=messages
    )
    # response = client.chat.completions.create(**req)
    full_content = ""
    # print("response",response)
    if response.choices and response.choices[0].message.content:
      full_content = response.choices[0].message.content
    print("response",full_content)