import calendar
import re
from num2words import num2words
from datetime import datetime

months_dict = {
    "января": "01", "февраля": "02",
    "марта": "03", "апреля": "04",
    "мая": "05", "июня": "06",
    "июля": "07", "августа": "08",
    "сентября": "09", "октября": "10",
    "ноября": "11", "декабря": "12"
}


def normalize_date_from_str(input_string):
    pattern_for_months_years_and_light_dates = r'(\b\d+\b)\s*(?:\(\D+\)\s*)?(?:\b\w+\b\s+)?(лет|год(?:а|ов)?|мес(?:яц[а-я]*)?)'
    matches_for_months_years_and_light_dates = re.findall(pattern_for_months_years_and_light_dates, input_string)

    pattern_for_complex_dates = r'\b\d{2}\.\d{2}\.\d{4}\b'
    matches_for_complex_dates = re.findall(pattern_for_complex_dates, input_string)

    months = "|".join(months_dict.keys())
    pattern_for_light_dates = fr'(\d{{1,2}})\s*({months})\s*(\d{{4}})'
    matches_for_light_dates = re.findall(pattern_for_light_dates, input_string)

    pattern_for_inverted_dates = r'(\d{4})-(\d{2})-(\d{2})'
    matches_for_inverted_dates = re.findall(pattern_for_inverted_dates, input_string)

    pattern_for_searching_for_numbers_in_alphabetic_format = r"(\b(?<!\d\s)(год|года|лет|месяц|месяца|месяцев)\b)"
    matches_for_searching_for_numbers_in_alphabetic_format = re.findall(
        pattern_for_searching_for_numbers_in_alphabetic_format, input_string)

    pattern_for_error = r"^(?:(?!(?:\d+|лет|года|годов|месяц|месяцев)).)*$"
    matches_for_error = re.findall(pattern_for_error, input_string)

    years = 0
    months = 0

    count_date_complex = 0
    count_date_light = 0
    count_date_inverted = 0
    count_date_alphabetic_format = 0
    count_error = 0

    list_dates_complex = []
    list_dates_light = []
    list_dates_inverted = []
    list_dates_alphabetic_format_is_digit = ""
    list_dates_alphabetic_format_is_last_word = []

    if matches_for_months_years_and_light_dates:
        for match in matches_for_months_years_and_light_dates:
            num, unit = match
            if 'лет' in unit or 'год' in unit:
                years += int(num)
            elif 'мес' in unit:
                months += int(num)

    elif matches_for_complex_dates:
        for match in matches_for_complex_dates:
            if match:
                count_date_complex += 1
                list_dates_complex.append(match)
    # print(list_dates_complex, "сложные даты")

    elif matches_for_light_dates:
        for match in matches_for_light_dates:
            if match:
                count_date_light += 1
                list_dates_light.append(match)
    # print(list_dates_light, "легкие даты")

    elif matches_for_inverted_dates:
        for match in matches_for_inverted_dates:
            if match:
                count_date_inverted += 1
                list_dates_inverted.append(match)
    # print(list_dates_inverted, "перевернутые даты")

    elif matches_for_searching_for_numbers_in_alphabetic_format:
        for match in matches_for_searching_for_numbers_in_alphabetic_format:
            if match:
                count_date_alphabetic_format += 1
                list_dates_alphabetic_format_is_digit = input_string
                words = list_dates_alphabetic_format_is_digit.split()
                list_dates_alphabetic_format_is_digit = ' '.join(words[:-1])

                list_dates_alphabetic_format_is_last_word.append(input_string.split()[-1])
    # print(list_dates_alphabetic_format_is_digit, ": цифры/числа в буквах")
    # print(list_dates_alphabetic_format_is_last_word, ": последнее слово")

    elif matches_for_error:
        for match in matches_for_error:
            if match:
                count_error += 1

    if count_date_complex == 2 and years == 0 and months == 0:
        """ex: c 01.01.2012 по 01.01.2027 == 15 лет"""
        date_start = datetime.strptime(f"{list_dates_complex[0]}", "%d.%m.%Y")
        date_end = datetime.strptime(f"{list_dates_complex[1]}", "%d.%m.%Y")

        years = date_end.year - date_start.year
        months = date_end.month - date_start.month
        days = date_end.day - date_start.day

        """Написал эти 2 if ниже, потому что не скачивается либа dateutil.relativedelta"""
        if days < 0:
            months -= 1
            days += calendar.monthrange(date_end.year, date_end.month)[1]

        if months < 0:
            years -= 1
            months += 12

        result = ""
        if years > 0:
            result += f"{years} {'год' if years == 1 else 'года' if 1 < years < 5 else 'лет'}"
        if months > 0:
            result += f" {months} {'месяц' if months == 1 else 'месяца' if 1 < months < 5 else 'месяцев'}"
        if days > 0:
            result += f" {days} {'день' if days == 1 else 'дня' if 1 < days < 5 else 'дней'}"

        return result.strip()

    elif count_error == 1:
        return f"error in data: {input_string}"

    elif count_date_complex == 1 and years == 0 and months == 0:
        """ex: 04.10.2023 == 04.10.2023"""
        data = list_dates_complex[-1]
        return data

    elif count_date_light == 1 and years == 0 and months == 0:
        """ex: 12 июня 2030 == 12.06.2030"""
        data = list_dates_light[0]
        day = data[0]
        month = months_dict.get(data[1])
        year = data[2]

        if month:
            output_date = f"{day}.{month}.{year}"
            return output_date
        return {"message": "Месяц написан с ошибкой"}

    elif count_date_inverted == 1 and years == 0 and months == 0:
        """ex: 2030-01-01 == 01.01.2030"""
        day = list_dates_inverted[0][2]
        month = list_dates_inverted[0][1]
        year = list_dates_inverted[0][0]

        output_date = f"{day}.{month}.{year}"
        if output_date:
            return output_date
        return {"message": "error"}

    elif count_date_alphabetic_format == 1:
        """ex: сто пятьдесят шесть лет == 156 лет"""
        for i in range(1000000):
            if num2words(i, lang='ru') == list_dates_alphabetic_format_is_digit:
                return f"{i} {list_dates_alphabetic_format_is_last_word[0]}"
        return None

    elif years == 0:
        """ex: 360 (триста шестьдесят) месяцев == 360 месяцев"""
        return f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'}"

    elif months == 0:
        """ex: 3 (три) года == 3 года"""
        return f"{years} {'год' if years % 10 == 1 and years % 100 != 11 else 'года' if 2 <= years % 10 <= 4 and (years % 100 < 10 or years % 100 >= 20) else 'лет'}"

    else:
        """ex: 5 (пять) лет и 11 (одиннадцать) месяцев == 5 лет 11 месяцев"""
        years_str = f"{years} {'год' if years % 10 == 1 and years % 100 != 11 else 'года' if 2 <= years % 10 <= 4 and (years % 100 < 10 or years % 100 >= 20) else 'лет'}"
        months_str = f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'}"
        return f"{years_str} {months_str}"


mas = [
    "5 (пять) лет и 11 (одиннадцать) месяцев",
    "3 (три) года",
    "360 (триста шестьдесят) месяцев",
    "1 год 26 месяцев",
    "20 июня 2023",
    "04.10.2023",
    "2023-04-03",
    "три года",
    "пятнадцать лет",
    "двадцать три года",
    "сто пятьдесят шесть лет",
    "одна тысяча сто пятьдесят шесть лет",
    "c 01.01.2024 по 02.12.2038",
    "sadgeshseh",
]

for input_str in mas:
    print(normalize_date_from_str(input_str))
