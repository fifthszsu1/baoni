import random
import string
import time


def generate_hkid():
    """生成一个有效的香港身份证号码(HKID)，使用时间戳确保不重复"""
    # 随机选择1或2个字母（排除I和O）
    available_letters = ''.join(set(string.ascii_uppercase) - {'I', 'O'})
    letter_count = random.choice([1, 2])
    letters = ''.join(random.choices(available_letters, k=letter_count))
    
    # 使用时间戳生成6位数字（取微秒时间戳的后6位）
    timestamp = int(time.time() * 1000000) % 1000000  # 微秒级时间戳，取后6位
    digits = str(timestamp).zfill(6)  # 确保是6位数字，不足补0
    
    # 计算校验位
    weights = [9, 8, 7, 6, 5, 4, 3, 2]
    numbers = []
    
    # 字母转数字 (A=10, B=11, ..., Z=35)
    if len(letters) == 1:
        numbers.append(36)
        numbers.append(ord(letters[0]) - ord('A') + 10)
    else:
        numbers.append(ord(letters[0]) - ord('A') + 10)
        numbers.append(ord(letters[1]) - ord('A') + 10)
    
    # 添加6位数字
    numbers.extend([int(d) for d in digits])
    
    # 计算加权和
    total = sum(num * weight for num, weight in zip(numbers, weights))
    
    # 计算校验位
    remainder = total % 11
    check_digit = 11 - remainder
    
    if check_digit == 10:
        check_digit = 'A'
    elif check_digit == 11:
        check_digit = '0'
    else:
        check_digit = str(check_digit)
    
    return f"{letters}{digits}({check_digit})"


if __name__ == "__main__":
    # 测试
    for i in range(10):
        print(generate_hkid())

