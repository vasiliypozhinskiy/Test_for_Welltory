import json, os, re

from jsonschema import Draft7Validator

"""Мне показалась некорректной формулировка задания. Предложение 'Часть схем 100% правильных, часть нет.' 
   интерпретировал как 'Часть файлов соответствуют схеме, часть нет'. Также не понятно что делать с файлами,
   для которых нет схемы."""


class JsonData:
    def __init__(self, json_file_path, schema_dir_path):
        self.json_file_path = json_file_path
        self.schema_dir_path = schema_dir_path
        self.schema_names = self.get_schema_names()
        self.json_data = self.get_data()
        self.log = f"\nФайл {self.json_file_path}\n"
        self.suitable_schema = self.find_suitable_schema()
        if self.suitable_schema:
            self.schema = self.get_schema()
            self.validator = Draft7Validator(self.schema)
        else:
            self.schema = None
            self.validator = None
            self.log += "Подходящая схема не найдена\n"

    def get_data(self):
        with open(self.json_file_path, "r", encoding='utf-8') as f:
            return json.load(f)

    def get_schema_names(self):
        names = [name.split(".")[0] for name in os.listdir(self.schema_dir_path)]
        return names

    def get_schema(self):
        path = self.schema_dir_path + "/" + self.suitable_schema + ".schema"
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)

    def find_suitable_schema(self):
        for schema_name in self.schema_names:
            split_name = schema_name.split('_')
            pattern = r"[\D\d]+".join(split_name)
            try:
                if self.json_data["event"] == schema_name:
                    return schema_name
                elif re.findall(pattern, self.json_data["event"]):
                    self.log += "Ошибка в ключе ['event']. Неправильное название схемы\n"
                    return schema_name
            except TypeError:
                self.log += "Файл не содержит данных\n"
                return
            except KeyError:
                self.log += "Файл не содержит ключа ['event'], невозможно определить соответствующую схему\n"
                return

    def find_errors(self):
        if self.schema:
            self.log += f"Проверен по схеме {self.suitable_schema}\n"
            try:
                errors = self.validator.iter_errors(self.json_data['data'])
            except KeyError:
                self.log += "Нет ключа ['Data']\n"
                return
            no_errors = True
            for error in errors:
                if error.path:
                    self.log += "Ошибка в ключе: ['Data']" + str(list(error.path)) + ". "
                else:
                    self.log += "Ошибка в ключе: ['Data']. "
                self.log += error.message + "\n"

                no_errors = False
            if no_errors:
                current_file.log += "Ошибок нет\n"


if __name__ == "__main__":

    json_list = os.listdir("event")

    for json_file_name in json_list:
        path = f"event\\{json_file_name}"
        current_file = JsonData(path, "schema")
        current_file.find_errors()
        with open("json_errors.txt", "a", encoding="utf-8") as f:
            f.write(current_file.log)





