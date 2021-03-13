import kivy

from kivy.app import App


from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivy.factory import Factory

from check import Check

import numpy as np
import pandas as pd
import random

#Config.set('graphics', 'width', '380')    # устанавливаем ширину и высоту окна
#Config.set('graphics', 'height', '640')


class Popup_m:

    # функция для вызова общего всплывающего окна, куда по ключу cont_key помещаем какой-либо контент
    def popup_menu(
                    self,
                    cont_key='menu',
                    sizes=(0.5, 0.5),
                    position={'right': 1, 'top': 1},
                    **kwargs
                    ):

        popup_window = ModalView(
            size_hint=sizes,
            pos_hint=position)

        # в зависимости от полученного ключа формируем контент всплывающего окна
        if cont_key == 'menu':  # по ключу Меню включаем класс Меню во всплывающем окне
            content = Menu()

        elif cont_key == 'open_file':  # включаем класс для выбора файла
            content = Open_file()
            content.turn_on(pw = popup_window)   # в функцию передаем также ссылку на экземпляр popup_window, чтобы обеспечить возможность его закрытия из другого класса

        elif cont_key == 'save_file':  # включаем класс для выбора файла
            content = Save_file()
            content.turn_on(pw = popup_window)

        elif cont_key == 'clear_dict':  # включаем класс Confirm_popup() для подтверждения очистки статистики словаря
            content = Confirm_popup()
            content.turn_on(text_to_label='Statistics of the dictionary will be cleared.\nAre you sure?',
                            text_to_button='Yes', func_key='clear_dict', pw = popup_window)   # в функцию передаем также ссылку на экземпляр popup_window, чтобы обеспечить возможность его закрытия из другого класса

        elif cont_key == 'statistics':  # включаем класс Confirm_popup() для демонстрации статистики
            content = Confirm_popup()
            content.turn_on(text_to_label='', text_to_button='Ок', func_key='stats + popup_dismiss', pw = popup_window)
            # текст для лейбла будет сформирован внутри класса Confirm_Popup вместе с переменными для статистики,
            # поэтому пока отправляем пустое сообщение

        elif cont_key == 'learned_popup':  # включаем класс Confirm_popup() для подтверждения нажатия кнопки Learned
            content = Confirm_popup()
            content.turn_on(pw = popup_window)  # запускаем метод для передачи элементам класса значений по умолчанию и экземпляра pw

        elif cont_key == 'dict_not_imported_popup':  # включаем класс Confirm_popup() для предупреждения о необходимости загрузки словаря
            content = Confirm_popup()
            content.turn_on(text_to_label='Import dictionary, please', text_to_button='Import', func_key='import_dict', pw = popup_window)

        else:   # по остальным ключам передаем в popup сообщение из вызывающей функции через cont_key
            content = Confirm_popup()
            content.turn_on(text_to_label = cont_key, text_to_button='Ок', func_key = 'popup_dismiss', pw = popup_window)

        # загружаем контент и открываем попап
        popup_window.add_widget(content)
        popup_window.open()


class Func(Check):   # класс с основными функциями приложения
    def __init__(self, *args, **kwargs):
        self.current_card = 0   # вводим переменную для проверки факта загрузки словаря
        self.app = App.get_running_app()  # в теле программы обращаться к элементам класса будем через (пример) self.app.root.label...
        self.ch = Check()   # задействуем класс для проверки загружаемого словаря
        self.txt_size = 1

    # функция импорта словаря в переменную data
    def import_dictionary(self,file_pass):

        #self.popup_window.dismiss()   # перед импортирование файла закрываем окно меню, аналог self.app.root.popup_window.dismiss().

        try:
            dict = pd.read_csv(file_pass[0], delimiter='|')   # загружаем словарь в переменную

            # ...и запускаем проверку словаря
            # в случае удачной проверки вернется подготовленный словарь
            # после неудачной проверки вернется None
            answer, message = self.ch.check_dict(dict)

        except:   # в случае неудачной загрузки файла присваиваем значения
            answer, message = None, 'Wrong file extention or data.\nCSV file required'


        if answer is not None:

            self.data = answer   # при удачной загрузки словаря меняем основной датафрейм и...
            self.current_card = pd.DataFrame({'Showed' : [0]}).iloc[0]   # ...меняем переменную для первичной обработки внутри функции show_card

            # в момент загрузки словаря задействуем функцию обновления бара (пересчет переменных внутри функции)
            self.progress_update()

            self.show_card(mode='random')   # запускаем загрузку первой карточки
            # переделать на проверку режима!!!

        else:   # при неудачной загрузке передаем в попап сообщение о причинах неудачной загрузки с рекомендациями о корректировках словаря
            self.popup_menu (cont_key = message, sizes = (0.65, 0.3), position = {'center_x': 0.5, 'center_y': 0.5})
            return ()

    # функция обновления прогресс бара
    def progress_update(self):

        self.progress_bar.max = len(self.data.index)  # общее количество карточек в словаре
        self.progress_bar.value = len(self.data[self.data.Learned == True].index)  # количество выученных карточек


    def show_card(self, mode='random', learned=False):  # data - принимаемый словарь в dataframe, mode - режим демонстрации

        ccn = self.current_card.name  # индекс current_card в data
        self.data.loc[ccn, 'Showed'] += 1
        #self.current_card.Showed += 1   # альтернативная запись двух предыдущих строк. НЕ работает. Оставлена в коде как памятник невежеству )))

        if learned == True:
            self.data.loc[ccn, 'Learned'] = True   # вносим изменения в ячейку Learned текущей карточки по номеру
            self.progress_update()    # задействуем функцию обновления бара

        # очищаем поле перевода
        self.app.root.label_2.text = ''

        # выбираем следующую сроку
        self.current_card = self.data[self.data.Learned == False].sample().iloc[0]  # рандомно выбираем строку файла из тех, что не имеют статуса learned = True. .sample - аналог random для df

        # исходя из режима демонстрации, присваиваем значения cc_word,cc_translation
        # изменение режима демонстрации НЕ реализовано в текущей версии. По умолчанию всегда задействован random
        if mode == 'forward':
            cc_word = self.current_card.Word
            self.cc_translation = self.current_card.Translation

        if mode == 'reverse':
            cc_word = self.current_card.Translation
            self.cc_translation = self.current_card.Word

        if mode == 'random':
            cc_word = random.choice([self.current_card.Word, self.current_card.Translation])
            if cc_word == self.current_card.Word:
                self.cc_translation = self.current_card.Translation
            else:
                self.cc_translation = self.current_card.Word

        # выводим cc_word в label_1
        self.app.root.label_1.text = cc_word  # через такую конструкцию получаем доступ к Контейнеру из любого класса

        # объяснение в примере https://stackoverflow.com/questions/47854990/objectproperty-has-no-attribute-kivy-python-3-x

    # функция проверки перевода (при нажатии кнопки Check) - выводит перевод в Label
    def check_translation(self):   # функция на кнопке Check, выводим перевод в label_2
        self.app.root.label_2.text = self.cc_translation
        print(self.button_learned.height, self.button_learned.size)

    # функция предварительной проверки факта загрузки словаря
    # direction = 0. Если словарь НЕ загружен, выдает предупреждение, если загружен - продолжает выполнение функции по cont_key)
    # direction = 1. Если словарь загружен, выдает предупреждение, если НЕ загружен - продолжает выполнение функции по cont_key)
    def dict_presence(self, cont_key, direction = 0):

        #self.popup_window.dismiss()  # перед импортирование файла закрываем окно меню, аналог self.app.root.popup_window.dismiss()

        if direction == 0:
        # если словарь загружен не был, отправляем предупреждение во всплывающем окне
            if type(self.current_card) is int:
                self.popup_menu(cont_key = 'dict_not_imported_popup', sizes = (0.65, 0.3), position = {'center_x': 0.5, 'center_y': 0.5})

            else:   # если словарь загружен, вызываем нужный попап или функцию
                # кнопки окна Меню:
                if cont_key == 'clear_dict':
                    self.popup_menu(cont_key='clear_dict', sizes=(0.65, 0.3), position={'center_x': 0.5, 'center_y': 0.5})
                elif cont_key == 'statistics':
                    self.popup_menu(cont_key='statistics')
                elif cont_key == 'save_file':
                    self.popup_menu(cont_key='save_file', sizes = (0.7, 0.7))
                # кнопки основного окна:
                elif cont_key == 'learned_popup':
                    self.popup_menu(cont_key='learned_popup', sizes=(0.65, 0.3), position={'center_x': 0.5, 'center_y': 0.5})
                elif cont_key == 'show_card':
                    self.show_card()
                elif cont_key == 'check_translation':
                    self.check_translation()


        elif direction == 1:
            # независимо от того, загружен ли словарь, открываем вызванный попап
            self.popup_menu(cont_key='open_file', sizes=(0.7, 0.7))

            # далее, если словарь уже загружен, дополнительно отправляем предупреждение
            if type(self.current_card) is not int:

                self.popup_menu(cont_key='If import new dictionary before saving current one, current statistics will be lost', sizes=(0.65, 0.3),
                                position={'center_x': 0.5, 'center_y': 0.5})


    # функция очистки статистики словаря. Вызывается по кнопке Menu/ Clear statistics через функцию dict_presence, после подтверждения очистки пользователем в попап очищает статистику
    def clear_dictionary(self):
        self.data['Showed'] = 0
        self.data['Learned'] = 0
        self.progress_update()   # обновляем прогресс бар


class Menu(AnchorLayout, Popup_m):   # определяем класс для kv файла (окно основного меню)
    anchor_x = 'left' # если не указывать, то слой будет выводиться по центру по обоим осям
    anchor_y = 'top'


class Open_file(AnchorLayout):  # определяем класс для kv файла (окно выбора файла для загрузки)
    anchor_x ='left' # если не указывать, то слой будет выводиться по центру по обоим осям
    anchor_y='top'

    o_f_filechooser = ObjectProperty()
    o_f_button = ObjectProperty()

    def turn_on(self, pw):
        self.app = App.get_running_app()
        self.pw = pw  # проводим ссылку на popup_window в класс
        self.o_f_button.bind(on_release = self.of_but_import_dict)

    def of_but_import_dict(self, instance):
        self.pw.dismiss()  # закрываем текущее окно
        self.app.root.import_dictionary(self.o_f_filechooser.selection)

class Save_file(AnchorLayout):
    anchor_x = 'left'
    anchor_y = 'top'

    s_f_filechooser = ObjectProperty()
    s_f_text_input = ObjectProperty()
    s_f_cancel_button = ObjectProperty()
    s_f_save_button = ObjectProperty()


    def turn_on(self, pw):
        self.app = App.get_running_app()
        self.pw = pw  # проводим ссылку на popup_window в класс
        self.s_f_cancel_button.bind(on_release=self.pw.dismiss)
        self.s_f_save_button.bind(on_release=self.sf_but_export_dict)

    def sf_but_export_dict(self, instance):
        self.pw.dismiss()  # закрываем текущее окно

        try:
            # далее проверяем, содержит ли текст s_f_text_input адрес s_f_filechooser.path
            # (адрес переносится в s_f_text_input при выборе какого=либо файла в окне - в kv файле s_f_filechooser.on_selection)
            # если содержит и начало совпадения на нулевом индексе, не включаем адрес повторно
            if self.s_f_text_input.text.find(self.s_f_filechooser.path) == 0:
                adress = self.s_f_text_input.text
            # если не содержит (возвращает индекс -1):
            elif self.s_f_text_input.text.find(self.s_f_filechooser.path) == -1:
                if self.s_f_filechooser.path[-1] != '\\':   # смотрим, какой символ в конце адреса. Если не бэкслэш, добавляем его при конкатенации адреса и названия файла
                    adress = self.s_f_filechooser.path + '\\' + self.s_f_text_input.text
                else:   # если в конце адреса \, просто конкатенатим
                    adress = self.s_f_filechooser.path + self.s_f_text_input.text
            else:   # если совпадение адреса не на нулевом индексе текста, вызываем попап с ошибкой
                self.app.root.popup_menu(cont_key = 'Probably, wrong adress, filename or extention', sizes = (0.65, 0.3), position = {'center_x': 0.5, 'center_y': 0.5})
                return()

            # сохраняем файл по полученному адресу
            self.app.root.data.to_csv(adress, sep = '|')

        except:   # если другая ошибка (к приимеру, нет прав на сохранение на выбранном диске)
            self.app.root.popup_menu(cont_key='No access to disk or another mistake',
                                     sizes=(0.65, 0.3), position={'center_x': 0.5, 'center_y': 0.5})



# класс для всплывающего онка с подтверждением действия и для окна статистики
# внутренняя функция принимает значения для окна: надписи на лейбл и кнопку, а также ключ для выбора функции для кнопки
class Confirm_popup(AnchorLayout):  # определяем класс для kv файла

    label_popup = ObjectProperty()
    button_popup = ObjectProperty()

    def turn_on(self, pw, text_to_label='Sure?', text_to_button='Yes', func_key='show_card'):   # на вход принимаем в т.ч. ссылку на popup_window (pw), чтобы была возможность закрывать окно из текущего класса
        # передаем в класс всплывающего окна тексты в лейбл, кнопку и вешаем на кнопку функцию
        self.app = App.get_running_app()
        self.pw = pw   # проводим ссылку на popup_window в класс
        self.label_popup.text = text_to_label
        self.button_popup.text = text_to_button


        if func_key == 'import_dict':
            self.button_popup.bind(on_release = self.cp_but_import_dict)

        elif func_key == 'show_card':
            self.button_popup.bind(on_release = self.cp_but_show_card)   # вешаем на кнопку функцию подтверждения выученного слова

        elif func_key == 'clear_dict':
            self.button_popup.bind(on_release = self.cp_but_clear_dict)

        elif func_key == 'popup_dismiss':
            self.button_popup.bind(on_release = self.pw.dismiss)

        elif func_key == 'stats + popup_dismiss':

            # формируем переменные статистики:
            all_cards = len(self.app.root.data.index)  # общее количество карточек в словаре
            learned_cards = len(self.app.root.data[self.app.root.data.Learned == True].index)  # количество выученных карточек
            learned_cards_p = round(learned_cards / all_cards * 100)   # процент выученных от общего количества
            in_study_cards = all_cards - learned_cards   # карточки в изучении
            in_study_cards_p = round(in_study_cards / all_cards * 100)   # процент в изучении от общего количества
            if learned_cards > 0:
                average = round(sum(self.app.root.data[self.app.root.data.Learned == True].Showed) / learned_cards)   # среднее количество показов перед нажатием "Выучено"
            else:
                average = 0

            # поскольку переменные для статистики формируем здесь (в классе попап их сформировать сложнее), сообщение в лейбл тоже ставим здесь
            self.label_popup.text = 'Total in dictionary: {}\nLearned: {} ({}%)\nIn study: {} ({}%)\nOn average showed \nbefore learned: {}'.format(
                all_cards, learned_cards, learned_cards_p, in_study_cards, in_study_cards_p, average)

            self.button_popup.bind(on_release = self.pw.dismiss)

    def cp_but_import_dict(self, instance):
        self.pw.dismiss()   # закрываем текущее окно
        self.app.root.popup_menu(cont_key='open_file', sizes=(0.7, 0.7))   # вызываем окно выбора файла для загрузки

    def cp_but_show_card(self, instance):
        self.pw.dismiss()  # закрываем текущее окно
        self.app.root.show_card(learned=True)   # ставим пометку "Выучено" в текущем слове и вызываем выбор следующего слова

    def cp_but_clear_dict(self, instance):
        self.pw.dismiss()   # закрываем текущее окно
        self.app.root.clear_dictionary()


class Container(BoxLayout, Popup_m, Func):   # определяем класс для kv файла

    # определяем свойства элементов kv
    progress_bar = ObjectProperty()
    label_1 = ObjectProperty()
    label_2 = ObjectProperty()
    button_menu = ObjectProperty()
    button_learned = ObjectProperty()
    button_next = ObjectProperty()
    button_check = ObjectProperty()


class MyApp(App):
    title = 'Cards Tutor'
    def build(self):
        self.root = Container()   # устанавливаем в качестве рута всего приложения Контейнер, чтобы к его элементам был доступ изо всех классов
        return self.root   # запускаем родительский класс


Factory.register('Container', cls=Container)
Factory.register('Menu', cls=Menu)
Factory.register('Open_file', cls=Open_file)
Factory.register('Confirm_popup', cls=Confirm_popup)

if __name__ == "__main__":
    MyApp().run() 