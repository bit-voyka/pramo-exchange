#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
from collections import Counter

def normalize_all_codes(xml_content):
    """
    Заменяет ВСЕ теги <Код> в файле на уникальные последовательные номера
    """
    # Находим все теги <Код>...</Код>
    # Используем lookahead, чтобы найти все, включая вложенные
    code_pattern = re.compile(r'<Код>(\d+)</Код>')
    
    # Находим все коды
    all_codes = list(code_pattern.finditer(xml_content))
    
    print(f"📊 Найдено тегов <Код>: {len(all_codes)}")
    
    if len(all_codes) == 0:
        return xml_content, 0
    
    # Анализируем текущие коды
    codes_values = [m.group(1) for m in all_codes]
    print(f"📊 Уникальных кодов: {len(set(codes_values))}")
    
    counter = Counter(codes_values)
    duplicates = [k for k, v in counter.items() if v > 1]
    if duplicates:
        print(f"📊 Дублирующихся кодов: {len(duplicates)}")
        print(f"   Примеры: {', '.join(duplicates[:5])}")
    
    # Заменяем коды на уникальные
    result = xml_content
    new_code = 1
    replaced = 0
    
    # Идем с конца, чтобы не сломать индексы
    for match in reversed(all_codes):
        old_code = match.group(1)
        # Заменяем этот конкретный код на новый
        # Используем замену с ограничением, чтобы заменить только это вхождение
        start = match.start()
        end = match.end()
        # Находим позицию этого тега в result (учитывая изменения)
        # Проще: заменяем с помощью replace с ограничением
        result = result.replace(f'<Код>{old_code}</Код>', f'<Код>{new_code}</Код>', 1)
        new_code += 1
        replaced += 1
    
    print(f"✅ Обновлено тегов: {replaced}")
    print(f"📌 Последний присвоенный код: {new_code - 1}")
    
    # Проверяем уникальность
    final_codes = re.findall(r'<Код>(\d+)</Код>', result)
    final_counter = Counter(final_codes)
    final_duplicates = {k: v for k, v in final_counter.items() if v > 1}
    
    if final_duplicates:
        print(f"⚠️ ВНИМАНИЕ: Осталось {len(final_duplicates)} дублирующихся кодов!")
        for code, count in list(final_duplicates.items())[:5]:
            print(f"   Код {code}: встречается {count} раз")
    else:
        print("✅ Все коды теперь уникальны!")
    
    return result, replaced, new_code - 1

def main():
    if len(sys.argv) < 2:
        print("❌ Использование: python3 normalize_codes.py <файл_правил_обмена>")
        print("   Пример: python3 normalize_codes.py ПравилаОбменаДанными_УТ-ERP.xml")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Формируем имя выходного файла
    if input_file.endswith('.xml'):
        output_file = input_file.replace('.xml', '_нормализованный.xml')
    else:
        output_file = 'ПравилаОбмена_нормализованный.xml'
    
    try:
        # Читаем файл
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📂 Обработка файла: {input_file}")
        print(f"📄 Размер: {len(content):,} символов")
        print("=" * 50)
        
        # Нормализуем
        result, replaced, max_code = normalize_all_codes(content)
        
        if replaced == 0:
            print("❌ Не найдено ни одного <Код>")
            sys.exit(1)
        
        # Сохраняем результат
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("=" * 50)
        print(f"✅ Готово! Файл сохранен: {output_file}")
        print(f"📊 Статистика:")
        print(f"   • Обработано тегов <Код>: {replaced}")
        print(f"   • Присвоено уникальных кодов: {max_code} (от 1 до {max_code})")
        print(f"   • Размер результата: {len(result):,} символов")
        
        # Проверяем дубли
        final_codes = re.findall(r'<Код>(\d+)</Код>', result)
        final_counter = Counter(final_codes)
        duplicates = {k: v for k, v in final_counter.items() if v > 1}
        
        if duplicates:
            print(f"   ⚠️ Внимание: осталось {len(duplicates)} дублирующихся кодов!")
            print(f"   📊 Топ-5 дублирующихся кодов:")
            for code, count in sorted(duplicates.items(), key=lambda x: -x[1])[:5]:
                print(f"      Код {code}: встречается {count} раз")
        else:
            print("   ✅ Все коды уникальны!")
        
    except FileNotFoundError:
        print(f"❌ Файл '{input_file}' не найден!")
        sys.exit(1)
    except PermissionError:
        print(f"❌ Нет прав на чтение файла '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()