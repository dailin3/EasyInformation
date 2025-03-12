from openai import OpenAI
import tool.config as config
import re, os
from ai.ai_callable import AI_callable

class AI_Tool:
    def __init__(self):
        self.name = "豆包"
        self.status = "1"
        self.MODEL_ENDPOINT_ID = config.MODEL_END_POINT_ID_DOUBAO
        self.BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
        self.API_KEY= config.API_KEY_DOUBAO
        self.client = OpenAI(base_url=self.BASE_URL,api_key=self.API_KEY)
        self.description = config.DESCRIPTION
        self.example = config.EXAMPLE

    def summerize(self, text):
        response = self.client.chat.completions.create(
            model=self.MODEL_ENDPOINT_ID,
            messages=[
                {"role": "system", "content": "你是总结器,为后续文本生成一个简短的总结，总结内容用双$包裹，如果你认为无法做到返回$空$,最好是一句话"},
                {"role": "user", "content": text}
            ]
        )
        result = re.findall(r"\$(.*?)\$",response.choices[0].message.content)[0]
        return result
    
    def parse_importance(self, text):
        response = self.client.chat.completions.create(
            model=self.MODEL_ENDPOINT_ID,
            messages=[
                {"role": "system", "content": f"你是推送分析器,用户有特点:{self.description},用户会感兴趣的例子:{self.example}.推荐度以$符号包裹且范围是0～100的整数,如果无法得到数值返回$空$,用户可能不感兴趣返回：$10$"},
                {"role": "user", "content": text}
            ]
        )
        result = re.findall(r"\$(.*?)\$",response.choices[0].message.content)[0]
        if result == "空":
            print("parse_importance failed:"+text)
            return 0
        return int(result)
    
    def parse_category(self, text):
        category = "学术,活动,通知,政务,娱乐,其他"
        response = self.client.chat.completions.create(
            model=self.MODEL_ENDPOINT_ID,
            messages=[
                {"role": "system", "content": f"你是分类器,有如下类{category},把文本归为其中一类，类别以$符号包裹，比如类别是学术，返回：$学术$，如果你认为无法做到返回$空$"},
                {"role": "user", "content": text}
            ]
        )
        result = re.findall(r"\$(.*?)\$",response.choices[0].message.content)[0]
        if result == "空":
            print("parse_category failed:"+text)
            return "其他"
        return result
    
    def parse_ralation(self,text1,text2):
        response = self.client.chat.completions.create(
            model=self.MODEL_ENDPOINT_ID,
            messages=[
                {"role": "system", "content": f"你是相关(相似)性分析器,相似性以$符号包裹，比如几乎没有相关性，返回：$5$，如果你认为无法做到返回$空$,文本是:{text1},分析后续文本与之相似性"},
                {"role": "user", "content": text2}
            ]
        )
        result = re.findall(r"\$(.*?)\$",response.choices[0].message.content)[0]
        if result == "空":
            print("parse_ralation failed:"+text1+" "+text2)
            return 0
        return int(result)

class AI_Brain():
    def __init__(self):
        self.name = "豆包"
        self.status = "1"
        self.MODEL_ENDPOINT_ID = config.MODEL_END_POINT_ID_DOUBAO
        self.BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
        self.API_KEY= config.API_KEY_DOUBAO
        self.client = OpenAI(base_url=self.BASE_URL,api_key=self.API_KEY)
        self.description = config.DESCRIPTION
        self.example = config.EXAMPLE
        self.ai_tool = AI_Tool()
        self.pre_messages = [
            {"role": "system", "content": "你认为有需要调用函数时可以这样去调用函数(一次只能调用一个函数,一个回答执行一个函数,不支持函数嵌套与变量,para不需要加引号等符号,只会执行第一个funtion标签中的内容):<function>function_name(para1,para2);</function>,平时不要随意使用标记,否则会导致程序出错.不可以一直多次调用某个函数.回复需要说人话,没必要返回函数调用结果,少废话,合理调用函数"},
            {"role": "system", "content": f"可用函数信息:{AI_callable.get_callable_functions_info()}"},
            {"role": "system", "content": "对话开始"}
        ]
        self.history_messages = []
    
    def save_message(self):
        name = self.ai_tool.summerize(self.history_messages)
        path = os.path.join(config.CWD,"db","chat_history",name)
        with open(path,"w") as f:
            for message in self.history_messages:
                f.write(f"{message["role"]}: {message["content"]}\n")

    def read_message(self,name):
        path = os.path.join(config.CWD,"db","chat_history",name)
        self.history_messages = self.pre_messages
        with open(path,"r") as f:
            for line in f.readlines():
                role,content = line.split(":")
                self.history_messages.append({"role":role,"content":content})
    
    def get_response(self, messages):
        response = self.client.chat.completions.create(
            model=self.MODEL_ENDPOINT_ID,
            messages=messages
        )
        result = response.choices[0].message.content
        self.history_messages.append({"role":"assistant","content":result})

        chat = re.sub(r'<function>.*?</function>', '', result)
        function_call = re.findall(r"<function>(.*?)</function>", result)

        feed_back ={
            "chat":chat,
            "function_call":function_call
        }
        return feed_back

class AI_Do():
    def __init__(self):
        self.name = "豆包"
        self.status = "1"
        self.MODEL_ENDPOINT_ID = config.MODEL_END_POINT_ID_DOUBAO
        self.BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
        self.API_KEY= config.API_KEY_DOUBAO
        self.client = OpenAI(base_url=self.BASE_URL,api_key=self.API_KEY)

    def extute_fuctioncall(self,function_call):
        if function_call:
            function_calls = function_call[0].split(';')
            result = {}
            for function_call in function_calls:
                if not function_call:
                    continue
                function_name = re.findall(r"^(.*?)\(.*?\)", function_call)[0]
                para = re.findall(r"\((.*?)\)", function_call)[0].split(',') if re.findall(r"\((.*?)\)", function_call)[0] else []
                print(function_name, para)
                return_value = self.function_run(function_name, para)
                result[function_name] = return_value
        return result
    
    def function_run(self,function_name, para):
        for func in AI_callable.functions:
            if func.name == function_name:
                return func.run(*para)
        return "error: function not found"