import math
import os
from pydantic import Field, BaseModel
from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv

load_dotenv()

class MultiplierParams(BaseModel):
    x:float=Field(...,description="乘数1")
    y:float=Field(...,description="乘数2")

class ReadDirParams(BaseModel):
    dir_path:str=Field(...,description="文件目录地址")

def multiplier(x:float, y:float):
    return x*y

def read_dir(dir_path:str):
    return os.listdir(dir_path)

tools=[
    {
        "type":"function",
        "function":{
            "name":"multiplier",
            "description":"乘法器",
            "parameters":MultiplierParams.model_json_schema()
        }
    },

    {
        "type":"function",
        "function":{
            "name":"read_dir",
            "description":"读取文件目录",
            "parameters":ReadDirParams.model_json_schema()
        }
    },
]

tool_registry={
    "multiplier":(MultiplierParams,multiplier),
    "read_dir":(ReadDirParams,read_dir),
}

client=AsyncOpenAI(
    api_key=os.environ.get("api_key"),
    base_url=os.environ.get("base_url")
)

async def main():
    messages=[
         {"role":"system","content":"你是一个智能agent，可以根据需要使用工具，输出结果。"},
         {"role":"user","content":"帮我看看.env里有什么"}
    ]
    step=0
    max_steps=5
    while step<max_steps:
        response=await client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-V4-Flash",
                    messages=messages,
                    tools=tools,
                    temperature=0.1
                )
        
        msg=response.choices[0].message
        messages.append(msg)


        if not msg.tool_calls:
            print(msg.content)
            break
        else:
            for tool_call in msg.tool_calls:
                name=tool_call.function.name
                try:
                    param,func=tool_registry[name]
                    args=param.model_validate_json(tool_call.function.arguments)
                    result=func(**args.model_dump())
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
                except Exception as e:
                    messages.append({"role":"tool","tool_call_id":tool_call.id,"content":f"工具执行出错{e}"})
        step+=1
asyncio.run(main())