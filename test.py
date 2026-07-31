import re


def validate_score(score):
    pattern_score = r'^(\d{1,2}|100)$'
    match = re.fullmatch(pattern_score, score)
    if match:
        print(f"{score} 匹配成功")
    else:
        print(f"{score} 匹配失败")


test_scores = ['23', '5', '100', '101', 'abc']
for score in test_scores:
    validate_score(score)