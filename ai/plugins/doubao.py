from openai import OpenAI
import tool.config as config
import re

class AI_Tool:
    def __init__(self):
        self.name = "豆包"
        self.status = "1"
        self.MODEL_ENDPOINT_ID = config.MODEL_ENDPOINT_ID_DOUBAO
        self.BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
        self.API_KEY= config.API_KET_DOUBAO
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
        pass
    def chat(self):
        pass
    def parse_requirements(self):
        pass
    def get_solution(self):
        pass

class AI_Do():
    def __init__(self):
        pass
    def extute_command(self):
        pass
    def add_data_to_info_table(self):
        pass
    def set_abandoned_flag(self):
        pass
    def query_data_from_info_table(self):
        pass