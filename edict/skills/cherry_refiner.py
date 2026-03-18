import openai

def refine_with_api(text, section, api_key):
    """
    通过Cherry Studio调用外部API（如GPT-3.5）对草稿进行精炼
    """
    if not api_key:
        print("   ⚠️ 未提供API密钥，跳过精炼")
        return text
    
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',  # 可替换为其他模型
            messages=[
                {'role': 'system', 'content': 'You are an expert reviewer for IEEE Transactions on Cognitive and Developmental Systems. Your task is to improve the academic quality of a paper section.'},
                {'role': 'user', 'content': f'Please refine the following {section} section to meet the high standards of IEEE CNS. Make it more formal, precise, and include relevant terminology. Keep the original ideas but enhance clarity and impact.\n\n{text}'}
            ],
            max_tokens=200,
            temperature=0.3
        )
        refined = response.choices[0].message.content.strip()
        return refined
    except Exception as e:
        print(f"   ❌ API调用失败：{e}")
        return text