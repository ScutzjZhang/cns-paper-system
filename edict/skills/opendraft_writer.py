import requests

def write_draft(topic, section, context=''):
    """
    使用Ollama本地模型生成章节初稿（Opendraft Writer）
    :param topic: 论文主题
    :param section: 章节名
    :param context: 检索到的相关知识片段（可选）
    :return: 生成的文本
    """
    prompt = f"""Write the {section} section of an IEEE CNS paper about "{topic}".
Use formal academic language, avoid first person, and follow these guidelines:
- Introduction: state the problem, review related work, and present the main contribution.
- Methodology: describe the proposed approach, experimental setup, and validation methods.
- Results: present the findings with statistical details and figures (described in text).
- Discussion: interpret the results, discuss limitations, and suggest future work.

Context from similar papers (for reference):
{context[:800]}

Now write the {section} section:"""
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'mistral:7b-instruct-v0.2-q4_K_M',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': 600,        # 最多生成600个token
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            print(f"Ollama HTTP error: {response.status_code}")
    except Exception as e:
        print(f"Ollama request failed: {e}")
    
    # 失败时返回占位符
    return f"[Local generation failed for {section} due to Ollama error.]"