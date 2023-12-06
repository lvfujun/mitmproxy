import re

def replace_path(path):
    # 使用正则表达式替换所有的 [index]，["xxx"]，['xxx'] 或者 [*] 实例
    path = re.sub(r'(\[\d+\]|\[".*?"\]|\[\'*?\'\]|\[\*\])', r'->\1', path)

    return path
user_input = 'JSON->data->tags[*][*]->tname|xxxx'
converted_path = replace_path(user_input)
print(converted_path)