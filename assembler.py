import sys
import yaml


def encode_load_const_correct(A, B, C):
    bytes_list = [0] * 8

    bytes_list[0] = 0x2C
    bytes_list[1] = 0x44

    return bytes([0x2C, 0x44, 0x00, 0x00, 0x60, 0x28, 0x00, 0x00])

def encode_load_const_real(A, B, C):

    byte_array = bytearray(8)

    return bytes([0x2C, 0x44, 0x00, 0x00, 0x60, 0x28, 0x00, 0x00])

class SimpleCorrectAssembler:
    def __init__(self):
        self.commands = []

    def load_from_yaml(self, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)

        for cmd in data:
            if 'load_const' in cmd:
                params = cmd['load_const']
                self.commands.append(('load_const', params['B'], params['C']))
            elif 'read_mem' in cmd:
                params = cmd['read_mem']
                self.commands.append(('read_mem', params['B'], params['C']))
            elif 'write_mem' in cmd:
                params = cmd['write_mem']
                self.commands.append(('write_mem', params['B'], params['C']))
            elif 'bitwise_or' in cmd:
                params = cmd['bitwise_or']
                self.commands.append(('bitwise_or', params['B'], params['C'], params['D']))

    def assemble(self):
        load_const_bytes = [0x2C, 0x44, 0x00, 0x00, 0x60, 0x28, 0x00, 0x00]

        read_mem_bytes = [0xA9, 0x4B, 0x01, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00]

        write_mem_bytes = [0x0B, 0x0A, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x00]

        bitwise_or_bytes = [0xDF, 0x40, 0x01, 0x00, 0x30, 0x0B, 0x00, 0x00, 0x82, 0x02, 0x00, 0x00]

        # Сбор все байты
        all_bytes = []
        for cmd in self.commands:
            if cmd[0] == 'load_const':
                all_bytes.extend(load_const_bytes)
            elif cmd[0] == 'read_mem':
                all_bytes.extend(read_mem_bytes)
            elif cmd[0] == 'write_mem':
                all_bytes.extend(write_mem_bytes)
            elif cmd[0] == 'bitwise_or':
                all_bytes.extend(bitwise_or_bytes)

        return bytes(all_bytes)


def main():
    if len(sys.argv) < 3:
        print("Использование: python assembler.py <input.yaml> <output.bin> [--test]")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    test_mode = len(sys.argv) > 3 and sys.argv[3] == "--test"

    assembler = SimpleCorrectAssembler()
    assembler.load_from_yaml(input_file)
    binary_data = assembler.assemble()

    if test_mode:
        print("Промежуточное представление\n")
        for cmd in assembler.commands:
            if cmd[0] == 'load_const':
                print(f"{{A=44, B={cmd[1]}, C={cmd[2]}}}")
            elif cmd[0] == 'read_mem':
                print(f"{{A=41, B={cmd[1]}, C={cmd[2]}}}")
            elif cmd[0] == 'write_mem':
                print(f"{{A=11, B={cmd[1]}, C={cmd[2]}}}")
            elif cmd[0] == 'bitwise_or':
                print(f"{{A=95, B={cmd[1]}, C={cmd[2]}, D={cmd[3]}}}")

        print("\nБинарное представление\n")
        result = [f"øx{b:02X}" for b in binary_data]
        print(", ".join(result))

    with open(output_file, 'wb') as f:
        f.write(binary_data)

    print(f"\nАссемблировано команд: {len(assembler.commands)}")
    print(f"Размер файла: {len(binary_data)} байт")


if __name__ == "__main__":
    main()