import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# 加载编码模型（单例，避免重复加载）
_model = None
def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    return _model

def retrieve_knowledge(topic, section, top_k=1):
    """
    从本地知识库中检索与主题最相关的论文片段（OpenClaw模拟）
    知识库文件位于 data/knowledge_base/{section}.json，每个条目包含 "topic" 和 "text"
    :return: 最相关片段的文本，若无则返回空字符串
    """
    kb_path = f'data/knowledge_base/{section}.json'
    if not os.path.exists(kb_path):
        return ''
    
    with open(kb_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    if not entries:
        return ''
    
    model = _get_model()
    # 对每个条目，将 topic 和 text 合并用于编码（实际应用中可只编码topic，但这里简单处理）
    texts = [f"{e['topic']} {e['text'][:200]}" for e in entries]
    text_embs = model.encode(texts)
    
    # 编码查询主题
    query_emb = model.encode([topic])[0]
    
    # 计算余弦相似度（内积）
    scores = np.dot(text_embs, query_emb)
    best_idx = np.argmax(scores)
    
    if scores[best_idx] > 0.75:  # 阈值
        return entries[best_idx]['text'][:800]  # 返回前800字符
    return ''