import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class LocalMemory:
    """本地记忆库（户部）：基于FAISS的向量存储，实现内容复用"""
    def __init__(self, kb_path="data/knowledge_base"):
        self.kb_path = kb_path
        os.makedirs(kb_path, exist_ok=True)
        
        # 加载句子编码模型（CPU）
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        
        # 索引文件路径
        self.index_file = os.path.join(kb_path, "faiss.index")
        self.meta_file = os.path.join(kb_path, "metadata.json")
        
        # 加载或初始化索引
        self.index = None
        self.metadata = []  # 每个元素为 {"topic": str, "section": str, "content": str}
        self._load_or_build_index()
    
    def _load_or_build_index(self):
        """从磁盘加载已有索引，或创建新索引"""
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            # 创建空索引：内积（余弦相似度） 384维（all-MiniLM-L6-v2输出维度）
            self.index = faiss.IndexFlatIP(384)
            self.metadata = []
            self._save_index()  # 保存空索引文件
    
    def _save_index(self):
        """保存索引和元数据到磁盘"""
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _get_embedding(self, text):
        """将文本转换为向量"""
        return self.model.encode([text])[0].astype(np.float32)
    
    def search(self, topic, section, threshold=0.75):
        """
        在记忆库中查找与 (topic, section) 最相似的已有内容
        :return: 如果找到相似度超过阈值的内容，返回其文本；否则返回None
        """
        if self.index.ntotal == 0:
            return None
        
        # 查询向量：结合主题和章节名
        query_text = f"{topic} {section}"
        query_vec = self._get_embedding(query_text).reshape(1, -1)
        
        # 搜索最相似的3个
        distances, indices = self.index.search(query_vec, k=3)
        
        # 遍历结果，返回第一个章节匹配且相似度达标的
        for i, idx in enumerate(indices[0]):
            if distances[0][i] >= threshold:
                meta = self.metadata[idx]
                # 确保章节一致（避免跨章节误匹配）
                if meta["section"] == section:
                    return meta["content"]
        return None
    
    def store(self, topic, section, content):
        """
        将新生成的内容存入记忆库
        """
        # 生成文本向量
        store_text = f"{topic} {section} {content[:200]}"  # 用前200字符作为代表
        vec = self._get_embedding(store_text).reshape(1, -1)
        
        # 添加到索引
        self.index.add(vec)
        
        # 保存元数据
        self.metadata.append({
            "topic": topic,
            "section": section,
            "content": content
        })
        
        # 持久化到磁盘
        self._save_index()