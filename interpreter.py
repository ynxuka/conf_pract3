import sys
import json


class UVMInterpreter:
    def __init__(self):
        self.code_memory = bytearray(65536)
        self.data_memory = bytearray(65536)
        self.pc = 0
        self.halted = False
        self.commands_executed = 0

        print("УВМ интерпретатор инициализирован")

    def load_program(self, bin_file):
        with open(bin_file, 'rb') as f:
            program = f.read()

        if len(program) > len(self.code_memory):
            raise ValueError("Программа слишком большая")

        self.code_memory[:len(program)] = program
        print(f" Программа загружена: {len(program)} байт")

    def run(self):
        print("\nВЫПОЛНЕНИЕ ПРОГРАММЫ")

        while not self.halted and self.pc < len(self.code_memory):
            cmd_info = self._read_command()
            if cmd_info is None:
                break

            cmd_type, cmd_size, params = cmd_info

            if self.pc - cmd_size < 0:
                current_pc = 0
            else:
                current_pc = self.pc - cmd_size

            print(f"PC=0x{current_pc:04X} {cmd_type:12} {params}")

            self._execute(cmd_type, params)
            self.commands_executed += 1

            if self.commands_executed > 1000:
                print("Слишком много команд, остановка")
                break

        print(f"\n Выполнение завершено на PC=0x{self.pc:04X}")
        print(f" Выполнено команд: {self.commands_executed}")

    def _read_command(self):
        if self.pc >= len(self.code_memory):
            self.halted = True
            return None

        first_byte = self.code_memory[self.pc]

        if first_byte == 0x2C:
            if self.pc + 8 > len(self.code_memory):
                self.halted = True
                return None

            cmd_bytes = self.code_memory[self.pc:self.pc + 8]
            result = 0
            for i, b in enumerate(cmd_bytes):
                result |= b << (i * 8)

            B = (result >> 7) & 0x1FFFFFFF
            C = (result >> 36) & 0xFFFFFF

            self.pc += 8
            return ('LOAD_CONST', 8, {'B': B, 'C': C})

        elif first_byte == 0xA9:
            if self.pc + 9 > len(self.code_memory):
                self.halted = True
                return None

            cmd_bytes = self.code_memory[self.pc:self.pc + 9]
            result = 0
            for i, b in enumerate(cmd_bytes):
                result |= b << (i * 8)

            B = (result >> 7) & 0x1FFFFFFF
            C = (result >> 36) & 0x1FFFFFFF

            self.pc += 9
            return ('READ_MEM', 9, {'B': B, 'C': C})

        elif first_byte == 0x0B:
            if self.pc + 9 > len(self.code_memory):
                self.halted = True
                return None

            cmd_bytes = self.code_memory[self.pc:self.pc + 9]
            result = 0
            for i, b in enumerate(cmd_bytes):
                result |= b << (i * 8)

            B = (result >> 7) & 0x1FFFFFFF
            C = (result >> 36) & 0x1FFFFFFF

            self.pc += 9
            return ('WRITE_MEM', 9, {'B': B, 'C': C})

        elif first_byte == 0xDF:
            if self.pc + 12 > len(self.code_memory):
                self.halted = True
                return None

            cmd_bytes = self.code_memory[self.pc:self.pc + 12]
            result = 0
            for i, b in enumerate(cmd_bytes):
                result |= b << (i * 8)

            B = (result >> 7) & 0x1FFFFFFF
            C = (result >> 36) & 0x1FFFFFFF
            D = (result >> 65) & 0x1FFFFFFF

            self.pc += 12
            return ('BITWISE_OR', 12, {'B': B, 'C': C, 'D': D})

        else:
            self.halted = True
            return None

    def _execute(self, cmd_type, params):
        if cmd_type == 'LOAD_CONST':
            B = params['B']
            C = params['C']
            if 0 <= B < len(self.data_memory):
                self.data_memory[B] = C & 0xFF
                if B + 1 < len(self.data_memory):
                    self.data_memory[B + 1] = (C >> 8) & 0xFF
                if B + 2 < len(self.data_memory):
                    self.data_memory[B + 2] = (C >> 16) & 0xFF

        elif cmd_type == 'READ_MEM':
            src_addr = params['C']
            dst_addr = params['B']

            if 0 <= src_addr < len(self.data_memory) and 0 <= dst_addr < len(self.data_memory):
                value = self.data_memory[src_addr]
                if src_addr + 1 < len(self.data_memory):
                    value |= self.data_memory[src_addr + 1] << 8
                if src_addr + 2 < len(self.data_memory):
                    value |= self.data_memory[src_addr + 2] << 16

                self.data_memory[dst_addr] = value & 0xFF
                if dst_addr + 1 < len(self.data_memory):
                    self.data_memory[dst_addr + 1] = (value >> 8) & 0xFF
                if dst_addr + 2 < len(self.data_memory):
                    self.data_memory[dst_addr + 2] = (value >> 16) & 0xFF

        elif cmd_type == 'WRITE_MEM':
            src_addr = params['B']
            dst_addr = params['C']

            if 0 <= src_addr < len(self.data_memory) and 0 <= dst_addr < len(self.data_memory):
                value = self.data_memory[src_addr]
                if src_addr + 1 < len(self.data_memory):
                    value |= self.data_memory[src_addr + 1] << 8
                if src_addr + 2 < len(self.data_memory):
                    value |= self.data_memory[src_addr + 2] << 16

                self.data_memory[dst_addr] = value & 0xFF
                if dst_addr + 1 < len(self.data_memory):
                    self.data_memory[dst_addr + 1] = (value >> 8) & 0xFF
                if dst_addr + 2 < len(self.data_memory):
                    self.data_memory[dst_addr + 2] = (value >> 16) & 0xFF

        elif cmd_type == 'BITWISE_OR':
            addr1 = params['B']
            addr2 = params['C']
            dst_addr = params['D']

            if (0 <= addr1 < len(self.data_memory) and
                    0 <= addr2 < len(self.data_memory) and
                    0 <= dst_addr < len(self.data_memory)):

                val1 = self.data_memory[addr1]
                if addr1 + 1 < len(self.data_memory):
                    val1 |= self.data_memory[addr1 + 1] << 8
                if addr1 + 2 < len(self.data_memory):
                    val1 |= self.data_memory[addr1 + 2] << 16

                val2 = self.data_memory[addr2]
                if addr2 + 1 < len(self.data_memory):
                    val2 |= self.data_memory[addr2 + 1] << 8
                if addr2 + 2 < len(self.data_memory):
                    val2 |= self.data_memory[addr2 + 2] << 16

                result = val1 | val2

                self.data_memory[dst_addr] = result & 0xFF
                if dst_addr + 1 < len(self.data_memory):
                    self.data_memory[dst_addr + 1] = (result >> 8) & 0xFF
                if dst_addr + 2 < len(self.data_memory):
                    self.data_memory[dst_addr + 2] = (result >> 16) & 0xFF

    def save_memory_dump(self, output_file, start_addr=0, end_addr=256):
        end_addr = min(end_addr, len(self.data_memory))

        dump = {
            'code_size': self.pc,
            'data_memory': {
                'start': start_addr,
                'end': end_addr,
                'bytes': self.data_memory[start_addr:end_addr].hex()
            },
            'commands_executed': self.commands_executed,
            'pc_final': self.pc
        }

        with open(output_file, 'w') as f:
            json.dump(dump, f, indent=2)
        print(f"Дамп памяти сохранен: {output_file}")


def main():
    if len(sys.argv) < 4:
        print("Использование: python interpreter.py <program.bin> <memory_dump.json> [start_addr end_addr]")
        print("Пример: python interpreter.py output.bin dump.json 90 220")
        sys.exit(1)

    bin_file = sys.argv[1]
    dump_file = sys.argv[2]

    start_addr = 0
    end_addr = 256
    if len(sys.argv) >= 5:
        start_addr = int(sys.argv[3])
        end_addr = int(sys.argv[4])

    interpreter = UVMInterpreter()

    try:
        interpreter.load_program(bin_file)
        interpreter.run()
        interpreter.save_memory_dump(dump_file, start_addr, end_addr)

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()