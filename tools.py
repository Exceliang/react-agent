import inspect
from pydantic import create_model

tools=[]
tool_registry={}

def tool(func):
    fields={}
    sig=inspect.signature(func)
    for name, params in sig.parameters.items():
        param_type=str if params.annotation is inspect.Parameter.empty else params.annotation
        default_val=... if params.default is inspect.Parameter.empty else params.default
        fields[name]=(param_type,default_val)

    param_model=create_model(f"{func.__name__}Params", **fields)

    tools.append({
        "type":"function",
        "function":{
            "name":func.__name__,
            "description":func.__doc__ or "",
            "parameters":param_model.model_json_schema(),
        }
    })

    tool_registry[func.__name__]=(param_model,func)

    return func