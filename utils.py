def translate_number(urdu_num: str):
    num_map = {
        '.': '.',
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9'
    }

    for urd, eng in num_map.items():
        urdu_num = urdu_num.replace(urd, eng)
    
    return urdu_num

if __name__ == '__main__':
    print(float(translate_number("۱.۲۳۳۴")))