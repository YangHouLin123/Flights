import json

# 步骤 1: 读取 getallcityandairports.json 文件
with open('getallcityandairports.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 步骤 2: 遍历 'body' 中的每个字母分组，过滤数据
for group in data['body']:
    # 使用列表推导式过滤每个字母分组中的城市数据
    data['body'][group] = [
        city for city in data['body'][group]
        if not (city['airportName'] == "" and city['airportShortName'] == "")
    ]

# 步骤 3: 将处理后的数据保存为新的 JSON 文件
with open('filtered_getallcityandairports.json', 'w', encoding='utf-8') as output_file:
    json.dump(data, output_file, ensure_ascii=False, indent=4)

# 打印处理后的数据（可选）
print(json.dumps(data, ensure_ascii=False, indent=4))
