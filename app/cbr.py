"""Модуль содержит определение класса для получения данных из ЦБР."""

import requests
import xml.etree.ElementTree as ET


class Cbr:
    """Класс для получения данных из ЦБР."""

    def __init__(self):
        """Конструктор класса."""

        # Адрес для запросов
        self.URL = 'http://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx'
        self.data = []

    def _find_data(self, xml_data, fields):
        """Метод ищет в объекте класса ElementTree поля с нужными названиями.
        :param xml_data: объект класса ElementTree, в котором нужно провести
        поиск;
        :param fields: список названий искомых полей."""

        for child in xml_data:
            if isinstance(child, ET.Element) and child.tag == 'ValuteData':
                for valuta in child:
                    valuta_data = {}  # словарь для данных валюты
                    for att in valuta:
                        if att.tag in fields:
                            if att.tag == 'Vname':
                                valuta_data['name'] = att.text.strip()
                            elif att.tag in ('Vcode', 'VnumCode'):
                                valuta_data['code'] = att.text.strip()
                            elif att.tag == 'Vcurs':
                                valuta_data['exchange'] =\
                                    float(att.text.strip())
                    if len(valuta_data) == len(fields):
                        self.data.append(valuta_data)
            elif isinstance(child, ET.Element):
                self._find_data(child, fields)

    def get_exchanges(self, date):
        """Метод получает список курсов валют на заданную дату.
        :param date: дата в формате yyyy-mm-dd.
        :return: список словарей: {name: имя валюты, code: код валюты,
        exchange: курс}."""

        headers = {'Content-Type': 'text/xml; charset=utf-8',
                   'SOAPAction': 'http://web.cbr.ru/GetCursOnDate'}
        data = f'<?xml version="1.0" encoding="utf-8"?>\
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\
                <soap:Body>\
                    <GetCursOnDate xmlns="http://web.cbr.ru/">\
                        <On_date>{date}</On_date>\
                    </GetCursOnDate>\
                </soap:Body>\
            </soap:Envelope>'
        r = requests.post(self.URL, headers=headers, data=data)
        if r.status_code != 200:
            # Произошла ошибка, данные не получены
            return []
        xml_data = ET.fromstring(r.content.decode('utf-8'))
        field_names = ('Vname', 'Vcode', 'Vcurs')  # имена искомых полей
        self._find_data(xml_data, field_names)
        return self.data

    def get_valutas(self):
        """Метод получает список валют.
        :return: список словарей: {name: имя валюты, code: код валюты}."""

        headers = {'Content-Type': 'text/xml; charset=utf-8',
                   'SOAPAction': 'http://web.cbr.ru/EnumValutes'}
        data = f'<?xml version="1.0" encoding="utf-8"?>\
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\
                <soap:Body>\
                    <EnumValutes xmlns="http://web.cbr.ru/">\
                        <Seld>false</Seld>\
                    </EnumValutes>\
                </soap:Body>\
            </soap:Envelope>'
        r = requests.post(self.URL, headers=headers, data=data)
        if r.status_code != 200:
            # Произошла ошибка, данные не получены
            return []
        xml_data = ET.fromstring(r.content.decode('utf-8'))
        field_names = ('Vname', 'VnumCode')  # имена искомых полей
        self._find_data(xml_data, field_names)
        return self.data
