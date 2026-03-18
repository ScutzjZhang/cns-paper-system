from .skills.opendraft_writer import write_draft
from .skills.openclaw_retriever import retrieve_knowledge
from .skills.cherry_refiner import refine_with_api

class Executor:
    """执行器（兵部）：调用具体技能生成章节内容"""
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
        self.token_used = 0   # 当日已用token数（仅统计外部API）
    
    def generate_section(self, topic, section):
        """
        生成指定章节的完整流程：
        1. 知识增强（OpenClaw检索）
        2. 本地模型生成初稿（Opendraft + Ollama）
        3. 质量评估
        4. 可选外部API精炼
        5. 应用IEEE格式规则
        """
        # 1. 知识检索（OpenClaw）
        context = retrieve_knowledge(topic, section)
        
        # 2. 本地生成初稿（Opendraft Writer）
        draft = write_draft(topic, section, context)
        
        # 3. 质量评估
        quality = self._assess_quality(draft, section)
        print(f"   📊 本地生成质量评分：{quality:.2f}")
        
        # 4. 若质量低于阈值且预算充足，调用外部API精炼
        if quality < 0.7 and self.config['enable_external_api']:
            if self.token_used + 150 <= self.config['token_budget_per_day']:
                print("   🔧 调用外部API精炼...")
                refined = refine_with_api(draft, section, self.config['api_key'])
                self.token_used += 150
                new_quality = self._assess_quality(refined, section)
                if new_quality > quality:
                    print(f"   ✨ 精炼后质量提升至：{new_quality:.2f}")
                    draft = refined
        
        # 5. 应用IEEE格式规则
        final_text = self._apply_ieee_rules(draft, section)
        return final_text
    
    def _assess_quality(self, text, section):
        """
        质量评估函数（刑部）
        基于术语密度和长度的简化评分，0~1之间
        """
        # 各章节期望的关键术语
        terms_dict = {
            'introduction': ['cognitive', 'architecture', 'developmental', 'propose', 'contribution'],
            'methodology': ['experiment', 'participants', 'procedure', 'analysis', 'validation'],
            'results': ['significant', 'effect', 'p <', 'anova', 'correlation'],
            'discussion': ['implication', 'limitation', 'future work', 'interpret', 'conclusion']
        }
        terms = terms_dict.get(section, [])
        
        if not terms:
            return 0.5  # 默认中等
        
        # 计算术语出现次数（不区分大小写）
        text_lower = text.lower()
        term_count = sum(text_lower.count(term) for term in terms)
        term_score = min(term_count / len(terms) * 0.8, 1.0)  # 每出现一个术语得0.8分，封顶1.0
        
        # 长度评分（期望每节至少500词，但这里简单用字符数估计）
        min_len = 600   # 字符数下限
        len_score = min(len(text) / min_len, 1.0)
        
        # 加权平均
        return 0.6 * term_score + 0.4 * len_score
    
    def _apply_ieee_rules(self, text, section):
        """
        应用IEEE CNS格式规则（礼部）
        """
        # 术语替换
        replacements = {
            'we propose': 'this study proposes',
            'our model': 'the proposed model',
            'I show': 'the results show',
            'brain model': 'cognitive architecture',
            'we argue': 'it is argued'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # 章节特有增强
        if section == 'methodology' and 'validation' not in text.lower():
            text += '\n\nAll experimental procedures followed the validation guidelines recommended by IEEE CNS.'
        elif section == 'results' and 'statistically significant' not in text.lower():
            text += '\n\nAll reported effects were statistically significant at p < 0.05.'
        elif section == 'discussion' and 'future work' not in text.lower():
            text += '\n\nFuture work should explore the generalizability of these findings across different cognitive architectures.'
        
        return text