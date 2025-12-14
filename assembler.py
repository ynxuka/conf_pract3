import sys
import yaml
import re

# Спецификация УВМ для варианта 15
SPEC = {
    "load_const": {
        "opcode": 44,
        "fields": ["A", "B", "C"],
        "bit_ranges": [(0, 6), (7, 35), (36, 59)],
        "size": 8
    },
    "read_mem": {
        "opcode": 41,
        "fields": ["A", "B", "C"],
        "bit_ranges": [(0, 6), (7, 35), (36, 64)],
        "size": 9
    },
    "write_mem": {
        "opcode": 11,
        "fields": ["A", "B", "C"],
        "bit_ranges": [(0, 6), (7, 35), (36, 64)],
        "size": 9
    },
    "bitwise_or": {
        "opcode": 95,
        "fields": ["A", "B", "C", "D"],
        "bit_ranges": [(0, 6), (7, 35), (36, 64), (65, 93)],
        "size": 12
    }
}


class Assembler:
    def __init__(self):
        self.commands = []

    def parse_yaml_program(self, yaml_content):
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Ошибка синтаксиса YAML: {e}")

        if not isinstance(data, list):
            raise ValueError("YAML должен содержать список команд")

        for cmd_idx, cmd_data in enumerate(data):
            if not isinstance(cmd_data, dict):
                raise ValueError(f"Команда {cmd_idx + 1} должна быть словарем (dict)")

            # Определяем тип команды
            cmd_type = None
            for spec_type in SPEC.keys():
                if spec_type in cmd_data:
                    cmd_type = spec_type
                    break

            if not cmd_type:
                raise ValueError(f"Неизвестный тип команды в элементе {cmd_idx + 1}: {cmd_data}")

            # Извлекаем параметры
            params = cmd_data[cmd_type]
            if not isinstance(params, dict):
                raise ValueError(f"Параметры для {cmd_type} должны быть словарем")

            spec = SPEC[cmd_type]

            # Проверяем наличие всех полей
            for field in spec["fields"][1:]:  # Пропускаем поле A (оно определяется opcode)
                if field not in params:
                    raise ValueError(f"Отсутствует поле {field} в команде {cmd_type}")

            # Формируем команду
            cmd = {
                "type": cmd_type,
                "opcode": spec["opcode"]
            }

            # Добавляем значения полей
            for field in spec["fields"][1:]:
                value = params[field]
                if isinstance(value, str):
                    # Обработка шестнадцатеричных значений
                    if value.startswith("0x"):
                        cmd[field] = int(value, 16)
                    else:
                        cmd[field] = int(value)
                else:
                    cmd[field] = int(value)

            self.commands.append(cmd)

    def assemble(self, source_path):
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.parse_yaml_program(content)

    def print_intermediate(self):
        # Вывод промежуточного представления в формате полей
        for cmd in self.commands:
            fields = [f"A={cmd['opcode']}"]
            for field, value in cmd.items():
                if field in ["type", "opcode"]:
                    continue
                fields.append(f"{field}={value}")
            print(f"{{{', '.join(fields)}}}")


def main():
    if len(sys.argv) < 3:
        print("Использование: python assembler.py <исходный_yaml_файл> <выходной_файл> [--test]")
        sys.exit(1)

    source_path = sys.argv[1]
    output_path = sys.argv[2]
    test_mode = len(sys.argv) > 3 and sys.argv[3] == "--test"

    assembler = Assembler()

    try:
        assembler.assemble(source_path)
    except Exception as e:
        print(f"Ошибка ассемблирования: {e}")
        sys.exit(1)

    if test_mode:
        assembler.print_intermediate()

    with open(output_path, 'wb') as f:
        f.write(b"")

    print(f"Ассемблировано команд: {len(assembler.commands)}")


if __name__ == "__main__":
    main()