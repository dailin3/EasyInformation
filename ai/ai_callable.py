class MetaAI_callable(type):
    """
    metaclass for the class which extends AI_callable to make it a singleton and auto register
    """
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls.instance = None
        
        if name != "AI_callable":
            ins = cls()
            AI_callable.register_function(ins)

    def __call__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super().__call__(*args, **kwargs)
        return cls.instance
        

class AI_callable(metaclass=MetaAI_callable):
    _functions = []

    @classmethod
    def get_functions(cls):
        return cls._functions

    @classmethod
    def register_function(cls, function):
        if "run" not in dir(function):
            raise ValueError("run method is required")
        if not function.name:
            raise ValueError("name is required")
        if cls._is_bad_description(function.description):
            raise ValueError("description is required")
        if cls._is_bad_usage(function.usage):
            raise ValueError("usage is required")
        
        # 替换相同名字的函数
        for i, func in enumerate(cls._functions):
            if func.name == function.name:
                cls._functions[i] = function
                return
                
        cls._functions.append(function)

    def __init__(self, func=None, usage=None, description=None, name=None, status="1", flags=None):
        self.usage = usage
        self.description = description
        self.name = name
        self.status = status
        self.flags = flags
        self.run = func

        if self.name:
            self.register_function(self)

    @classmethod
    def _is_bad_description(cls, description):
        # TODO: this description must conform to MCP for AI
        return not description
    
    @classmethod
    def _is_bad_usage(cls, usage):
        return not usage

    @property
    def info(self):
        return {
            "function_name": self.name,
            "description": self.description,
            "usage": self.usage,
            "flags": self.flags
        }
    
    def __call__(self,function):
        func = AI_callable()
        func.name = function.__name__
        func.description = self.description if self.description else function.__doc__
        func.usage = self.usage
        func.flags = self.flags
        func.status = self.status
        func.run = function
        AI_callable.register_function(func)
        return func
    
    @classmethod
    def get_callable_functions_info(cls):
        return [func.info for func in AI_callable.get_functions()]