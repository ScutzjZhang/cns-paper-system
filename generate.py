import sys
from core.skill_scheduler import SkillScheduler
from datetime import datetime

def read_topic(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 简单解析：第一行作为主题，后续可指定章节
    topic = lines[0].strip().replace('#', '').strip()
    sections = ['introduction', 'methodology', 'results']  # 默认章节
    if len(lines) > 1 and '章节' in lines[1]:
        # 支持自定义章节
        custom = lines[1].split('：')[-1].strip()
        sections = [s.strip() for s in custom.split(',')]
    return topic, sections

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    topic, sections = read_topic(input_file)
    
    scheduler = SkillScheduler()
    output_lines = []
    for section in sections:
        print(f"Generating {section}...")
        result = scheduler.execute({"topic": topic, "section": section})
        output_lines.append(f"## {section.upper()}\n{result}\n")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = input_file.replace('.txt', f'_{timestamp}.txt')
    out_path = f"output/{out_name}"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    print(f"Done! Output saved to {out_path}")

if __name__ == "__main__":
    main()
