import yaml
from .memory import LocalMemory
from .executor import Executor

class Scheduler:
    """任务调度器（吏部）：协调整个生成流程"""
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.memory = LocalMemory()          # 户部：记忆库
        self.executor = Executor(self.memory, self.config)  # 兵部：执行器

    def run(self, topic, sections=None):
        """
        根据主题生成论文各章节
        :param topic: 论文主题字符串
        :param sections: 章节列表，默认使用['introduction','methodology','results','discussion']
        :return: 字典 {章节名: 内容}
        """
        if sections is None:
            sections = ['introduction', 'methodology', 'results', 'discussion']
        
        results = {}
        for sec in sections:
            print(f"🧪 处理章节：{sec}")
            # 第一步：查询本地记忆库（户部检索）
            cached = self.memory.search(topic, sec)
            if cached:
                print(f"   ✅ 命中本地记忆，直接复用")
                results[sec] = cached
                continue
            
            # 第二步：执行生成流水线（兵部调用各技能）
            text = self.executor.generate_section(topic, sec)
            results[sec] = text
            
            # 第三步：将新生成的内容存入记忆库（户部存储）
            self.memory.store(topic, sec, text)
        
        return results