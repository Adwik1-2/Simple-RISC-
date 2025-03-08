import streamlit as st

# Existing opcode_map and registers definitions
opcode_map = {
    "add": "00000", "sub": "00001", "mul": "00010", "div": "00011", "mod": "00100",
    "cmp": "00101", "and": "00110", "or": "00111", "not": "01000", "mov": "01001",
    "lsl": "01010", "lsr": "01011", "asr": "01100", "nop": "01101", "ld": "01110",
    "st": "01111", "beq": "10000", "bgt": "10001", "b": "10010", "call": "10011",
    "ret": "10100", "hlt": "11111",
}

registers = {f"r{i}": i for i in range(16)}  # r0 to r15 mapped dynamically

def parse_instruction(line):
    parts = line.strip().replace(",", " ").split()  # To remove commas
    if not parts:
        return "Error: Empty instruction line"

    instr = parts[0]  # First token is the instruction

    # Handle unsigned (u) or half-word (h) versions
    is_unsigned = instr.endswith("u")
    is_halfword = instr.endswith("h")
    base_instr = instr.rstrip("uh")  # Remove 'u' or 'h' suffix

    if base_instr not in opcode_map:
        return f"Error: Unknown instruction '{instr}' in line: {line}"

    opcode = opcode_map[base_instr]

    # Ensure every return path provides a string
    if base_instr in ("add", "sub", "mul", "div", "mod", "and", "or", "lsl", "lsr", "asr"):
        if len(parts) < 4:
            return f"Error: Missing operands for instruction '{instr}' in line: {line}"
        if parts[1] not in registers or parts[2] not in registers:
            return f"Error: Invalid register(s) in '{instr}' in line: {line}"

        rd = registers[parts[1]]
        rs1 = registers[parts[2]]
        if parts[3] in registers:
            rs2 = registers[parts[3]]
            return f"{opcode}0{rd:04b}{rs1:04b}{rs2:04b}".ljust(32, '0')
        else:
            try:
                imm_val = int(parts[3])
            except ValueError:
                return f"Error: Invalid immediate value '{parts[3]}' for '{instr}' in line: {line}"
            return f"{opcode}1{rd:04b}{rs1:04b}00{imm_val:016b}"

    if instr in ["nop", "ret","hlt"]:
        if len(parts) > 1:
            return f"Error: Unexpected operands for '{instr}' in line: {line}"
        return f"{opcode}".ljust(32, '0')

    if instr in ["call", "b", "beq", "bgt"]:
        if len(parts) < 2:
            return f"Error: Missing offset for branch instruction '{instr}' in line: {line}"
        try:
            offset = int(parts[1])  # Convert offset
        except ValueError:
            return f"Error: Invalid offset '{parts[1]}' for '{instr}' in line: {line}"

        offset_bin = format(offset & 0x7FFFFFF, '027b')  # Ensure two's complement representation
        return opcode + offset_bin

    if instr in ["cmp", "not", "mov"]:
        if len(parts) < 3:
            return f"Error: Missing operands for '{instr}' in line: {line}"
        rd = registers[parts[1]]
        if parts[2] in registers:
            rs = registers[parts[2]]
            return f"{opcode}0{rd:04b}0000{rs:04b}".ljust(32, '0')
        else:
            try:
                imm_val = int(parts[2])
            except ValueError:
                return f"Error: Invalid immediate value '{parts[2]}' for '{instr}' in line: {line}"
            return f"{opcode}1{rd:04b}000000{imm_val:016b}"

    if instr in ["ld", "st"]:
        if len(parts) < 3:
            return f"Error: Missing operands for '{instr}' in line: {line}"

        rd_or_rs2 = parts[1]
        base_reg = parts[2]
        a = base_reg.find("[")
        b = base_reg.find("]")
        if a == -1 or b == -1:
            return f"Error: Invalid memory access format in '{instr}' in line: {line}"
        base = base_reg[a+1:b]
        if a == 0:
            offset = 0
        else:
            try:
                offset = int(base_reg[0:a])
            except ValueError:
                return f"Error: Invalid offset format in '{instr}' in line: {line}"

        if rd_or_rs2 not in registers or base not in registers:
            return f"Error: Invalid register(s) in '{instr}' in line: {line}"

        reg1 = registers[rd_or_rs2]
        base1 = registers[base]

        return f"{opcode}1{reg1:04b}{base1:04b}{offset:04b}".ljust(32, '0')

    return f"Error: Unknown instruction '{instr}' in line: {line}"  # Ensure error return

# Streamlit UI
st.title("Assembly to Binary Converter")

# Text area for assembly code input
assembly_code = st.text_area("Write your assembly code here:", height=300)

# Button to trigger assembly
if st.button("Assemble"):
    if not assembly_code.strip():
        st.error("Please enter some assembly code.")
    else:
        # Assemble the code
        binary_output = []
        errors = []
        for line_number, line in enumerate(assembly_code.splitlines(), start=1):
            if not line.strip():
                continue  # Skip empty lines
            binary_code = parse_instruction(line)
            if binary_code.startswith("Error"):
                errors.append(f"Error in line {line_number}: {line.strip()} → {binary_code}")
            else:
                binary_output.append(binary_code)

        if errors:
            for error in errors:
                st.error(error)
            st.error("Assembly stopped due to errors.")
        else:
            st.success("Assembly completed successfully!")
            binary_result = "\n".join(binary_output)

            # Display binary output
            st.text_area("Binary Output:", binary_result, height=300)

            # Provide binary output as a downloadable file
            st.download_button(
                label="Download Binary File",
                data=binary_result,
                file_name="output.bin",
                mime="application/octet-stream"
            )