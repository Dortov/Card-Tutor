import sys

import numpy as np
import pandas as pd

# определяем класс с двумя функциями для проверки и подготовки загружаемого словаря
class Check:

    # функция проверки словаря при загрузке
    # при соответствии словаря ряду параметров передает его вспомогательной функции prepare_dict, получает обратно измененный и возвращает data
    # при несоответствии возвращает None
    def check_dict(self, data):
        quantity_columns = 0  # переменная количество столбцов
        word_column = 0  # переменная количество столбцов "Word"
        translation_column = 0  # переменная количество столбцов "Translation"
        learned_column = 0  # переменная количество столбцов "Learned"
        showed_column = 0  # переменная количество столбцов "Showed"


        for i in data.keys():  # смотрим названия столбцов и заполняем переменные
            quantity_columns += 1
            if i == 'Word':
                word_column += 1
            if i == 'Translation':
                translation_column += 1
            if i == 'Learned':
                learned_column += 1
            if i == 'Showed':
                showed_column += 1

        # далее смотрим словарь на ряд условий в порядке их приоритетности, по итогам которых реализуем один из вариантов:
        # 1. не принимаем словарь и отправляем значение для переменной self.data равное None
        # 2. подготавливаем словарь, обращаясь к функции prepare_dict, и возвращаем в основной код изменный словарь

        if quantity_columns < 2:  # если в словаре только одна колонка - не принимаем словарь
            message = "Dictionary must contain at least two columns: Word and Translation"
            return (None, message)  # Возвращаем значения для переменной self.data и сообщение пользователю

        # если колонок 2 и больше...
        elif (word_column > 1 or translation_column > 1):  # если основных колонок больше, чем по одной, не принимаем и выходим из функции
            message = 'Dictionary must contain maximum one "Word" column and maximum one "Translation" column'
            return (None, message)  # Возвращаем значения для переменной self.data и сообщение пользователю

        elif (learned_column > 1 or showed_column > 1):  # если хотя бы одного из столбцов Learned или Showed больше одного, отменяем загрузку
            message = 'Dictionary must contain maximum one "Learned" column and maximum one "Showed" column'
            return (None, message)  # Возвращаем значения для переменной self.data и сообщение пользователю

        elif (quantity_columns > 2 and (word_column == 0 or translation_column == 0)):  # Если колонок 3 и более (если 2 - вопрос решаемый ниже), при этом одно из обязательных наименований не обозначено, не принимаем
            message = 'If dictionary contains more than two columns, please, mark "Word" and "Translation" columns'
            return (None, message)  # Возвращаем значения для переменной self.data и сообщение пользователю

        elif (word_column == 1 and translation_column == 1):  # ...считаем колонки word and translation. Если по одной - ок

            data = self.prepare_dict(data, learned_column, showed_column)  # проводим словарь через prepare_dict
            return (data, None)  # Возвращаем значения для переменной self.data, сообщение пустое

        # если колонок только две...
        elif (quantity_columns == 2 and (word_column == 0 and translation_column == 0)):  # если колонки две и без наименований, присваиваем/ меняем наименования

            w, t = str(data.keys()[0]), str(data.keys()[1])  # перекидываем значения первой строки (которая перешла в keys) в переменные
            data.columns = ['Word', 'Translation']  # переименовываем наименования рядов

            # дальше возвращаем в дф удаленные при переименовывании рядов значения
            additional_row = pd.DataFrame({'Word': w, 'Translation': t}, index=[-0.5])  # формируем новый дф с одной строкой с удаленными из data значениями, строку будем добавлять в data на нулевую позицию (индекс)
            data = data.append(additional_row,ignore_index=False)  # добавляем наш дф, ignore_index - игнорируем или нет метку индекса
            data = data.sort_index().reset_index(drop=True)  # сортируем ряды, переназначая номера рядов (чтобы не маячил наш -0.5)

            data = self.prepare_dict(data, learned_column, showed_column)  # проводим словарь через prepare_dict
            return (data, None)  # возвращаем измененный словарь

        elif (quantity_columns == 2 and (word_column == 0 and translation_column == 1)):  # если не хватает одного из наименований, присваиваем его альтернативной колонке
            for i in data.keys():
                if i != 'Translation':
                    data = data.rename(columns={i: 'Word'})  # меняем название несовпадающей колонки

            data = self.prepare_dict(data, learned_column, showed_column)  # проводим словарь через prepare_dict
            return (data, None)  # возвращаем измененный словарь

        elif (quantity_columns == 2 and (word_column == 1 and translation_column == 0)):
            for i in data.keys():
                if i != 'Word':
                    data = data.rename(columns={i: 'Translation'})  # меняем название несовпадающей колонки

            data = self.prepare_dict(data, learned_column, showed_column)  # проводим словарь через prepare_dict
            return (data, None)  # возвращаем измененный словарь


    # функция обработки словаря  при загрузке (вспомогательная для check_dict, вызывается ТОЛЬКО из нее)
    # принимает data, возвращает измененный data или None
    def prepare_dict(self, data, learned_column,showed_column):  # на вход принимаем измененный файл с данными, а также количество столбцов Learned и Showed

        if learned_column == 0:  # если в файле отсутствуют столбцы Learned и Showed, создаем их с нулевыми значениями
            data['Learned'] = 0
        if showed_column == 0:
            data['Showed'] = 0

        # приводим столбец Showed к числовому типу и заменяем нечисловые значения на 0
        data['Showed'] = pd.to_numeric(data['Showed'], errors='coerce',downcast='unsigned')  # errors='coerce' - проставляет Nan вместо несоответствующих значений, downcast = 'unsigned' - присваивает тип integer
        data['Showed'].fillna(0, inplace=True)  # заменяем nan на 0 в столбце
        data['Showed'] = pd.to_numeric(data['Showed'],downcast='unsigned')  # вновь применяем функцию для перевода в integer из float (необязательное действие)

        # если в столбце Learned есть не булевые значения, работаем над ним
        if data['Learned'].dtypes != bool:
            for i in data.index:  # ищем в столбце значения, отличные от True (в str, так как в object все значения в str). Ищем по index на случай, если номера идут не подряд (при удалении строк из фрейма на предыдущих этапах)

                if data.loc[i, 'Learned'] != 'True':  # значения Тру оставляем как есть, все остальное стираем, чтобы при конвертации в boolean пустые значения переконвертились в False
                    data.loc[i, 'Learned'] = ''

            data['Learned'] = data['Learned'].astype(bool)  # и меняем тип колонки

        data = data.dropna(subset=['Word', 'Translation'])  # удаляем строки с пустыми значениями в ячейках 'Word' или/и 'Translation'

        return (data)  # возвращаем измененный словарь

