
import streamlit as st
import re
import tempfile
import os

# Set page configuration
st.set_page_config(
    page_title="SIMPLE RISC CONVERTER",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for whiteish theme
st.markdown("""
    <style>
        body {
            background-color: #f5f5f5;
            color: #333333;
        }
        .stApp {
            background-color: #f5f5f5;
            color: #333333;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        h1 {
            color: #333333;
            font-size: 2.5em;
            letter-spacing: 1px;
            text-align: center;
        }
        .subtitle {
            color: #666666;
            text-align: center;
            margin-top: -10px;
            margin-bottom: 20px;
        }
        .instructions {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #dddddd;
        }
        .instructions h3 {
            margin-top: 0;
            color: #333333;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border: none;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .section {
            border: 1px solid #dddddd;
            padding: 25px;
            border-radius: 8px;
            background-color: #ffffff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: #eeeeee;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #dddddd;
            color: #333333;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            border: none;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50;
            color: white;
        }
        .stTextArea textarea {
            background-color: #ffffff;
            color: #333333;
        }
        .stFileUploader label {
            color: #333333;
        }
        /* Custom CSS for error messages */
        .error-message {
            color: #ff0000;  /* Red color for error messages */
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("<h1>SIMPLE RISC CONVERTER</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Convert your assembly code to binary format for RISC architecture</p>", unsafe_allow_html=True)

# Instructions section
st.markdown("""
<div class="instructions">
    <h3>Instructions</h3>
    <p>Enter your RISC assembly code or upload an .asm file to convert it to binary format. The converter supports all standard RISC instructions and will validate your syntax.</p>
</div>
""", unsafe_allow_html=True)

# Your existing assembler code
opcode_map = {
    "add": "00000", "sub": "00001", "mul": "00010", "div": "00011", "mod": "00100",
    "cmp": "00101", "and": "00110", "or": "00111", "not": "01000", "mov": "01001",
    "lsl": "01010", "lsr": "01011", "asr": "01100", "nop": "01101", "ld": "01110",
    "st": "01111", "beq": "10000", "bgt": "10001", "b": "10010", "call": "10011",
    "ret": "10100", "hlt": "11111",
}
registers = {f"r{i}": i for i in range(16)}  # r0 to r15 mapped dynamically

def parse_instruction(line1, address, labels_dict):
    if ':' in line1:
        a = line1.find(":")
        line = line1[a+1:]
    else:
        line = line1    

    parts = [x.strip() for x in re.split(r"[\s,]+", line) if x] # Remove commas and spaces
    if not parts:
        return None  # Skip lines that only contain a label

    instr = parts[0]  # First token is the instruction

    # Handle unsigned (u) or half-word (h) versions
    modifier = ''
    if instr.endswith("u"):
        modifier = 'u'
    elif instr.endswith("h"):
        modifier = 'h'
    base_instr = instr.rstrip("uh")  # Remove 'u' or 'h' suffix

    if base_instr not in opcode_map:
        return f"Error: Unknown instruction '{instr}' in line: {line}"

    opcode = opcode_map[base_instr]
    

    # Ensure every return path provides a string
    if base_instr in ("add", "sub", "mul", "div", "mod", "and", "or", "lsl", "lsr", "asr"):
        if len(parts) < 4:
            return f"Error: Missing operands for instruction '{instr}' in line: {line}"
        if len(parts) > 4:
            return f"Error: Unexpected operands for instruction '{instr}' in line: {line}"
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
                if imm_val < 0:
                    imm_val = (1 << 16) + imm_val
            except ValueError:
                return f"Error: Invalid immediate value '{parts[3]}' for '{instr}' in line: {line}"
            if modifier=='u':
                return f"{opcode}1{rd:04b}{rs1:04b}01{imm_val:016b}"
            elif modifier=='h':
                return f"{opcode}1{rd:04b}{rs1:04b}10{imm_val:016b}"
            else:
                return f"{opcode}1{rd:04b}{rs1:04b}00{imm_val:016b}"

    if instr in ["nop", "ret", "hlt"]:
        if len(parts) > 1:
            return f"Error: Unexpected operands for '{instr}' in line: {line}"
        return f"{opcode}".ljust(32, '0')

    if instr in ["call", "b", "beq", "bgt"]:
        if len(parts) < 2:
            return f"Error: Missing offset for branch instruction '{instr}' in line: {line}"
        elif len(parts) > 2:
            return f"Error: Unexpected operands for '{instr}' in line: {line}"
        # Handle labels in branch instructions
        if parts[1] in labels_dict:
            offset = int(labels_dict[parts[1]] - address)
            if offset < 0:
                offset = (1 << 27) + offset
            return f"{opcode}{offset:027b}"
        else:
            try:
                offset = int(parts[1])
                return f"{opcode}{offset:27b}"
            except ValueError:
                return f"Error: Label '{parts[1]}' not found for branch instruction"

    if instr == "cmp":
        if len(parts) < 3:
            return f"Error: Missing operands for '{instr}' in line: {line}"
        elif len(parts) > 3:
            return f"Error: Unexpected operands for '{instr}' in line: {line}"
        
        if parts[1] not in registers:
            return f"Error: Invalid register(s) in '{instr}' in line: {line}"
        
        rd = registers[parts[1]]
        if parts[2] in registers:
            rs = registers[parts[2]]
            return f"{opcode}00000{rd:04b}{rs:04b}".ljust(32, '0')
        else:
            try:
                imm_val = int(parts[2])
                if imm_val < 0:
                    imm_val = (1 << 16) + imm_val
            except ValueError:
                return f"Error: Invalid immediate value '{parts[2]}' for '{instr}' in line: {line}"
            if modifier=='u':
                return f"{opcode}10000{rd:04b}01{imm_val:016b}"
            elif modifier=='h':
                return f"{opcode}10000{rd:04b}10{imm_val:016b}"
            
            return f"{opcode}10000{rd:04b}00{imm_val:016b}"


    if instr in ["not", "mov"]:
        if len(parts) < 3:
            return f"Error: Missing operands for '{instr}' in line: {line}"
        elif len(parts) > 3:
            return f"Error: Unexpected operands for '{instr}' in line: {line}"
        
        if parts[1] not in registers:
            return f"Error: Invalid register(s) in '{instr}' in line: {line}"
        
        rd = registers[parts[1]]
        if parts[2] in registers:
            rs = registers[parts[2]]
            return f"{opcode}0{rd:04b}0000{rs:04b}".ljust(32, '0')
        else:
            try:
                imm_val = int(parts[2])
                if imm_val < 0:
                    imm_val = (1 << 16) + imm_val
            except ValueError:
                return f"Error: Invalid immediate value '{parts[2]}' for '{instr}' in line: {line}"
            if modifier=='u':
                return f"{opcode}1{rd:04b}000001{imm_val:016b}"
            elif modifier=='h':
                return f"{opcode}1{rd:04b}000010{imm_val:016b}"
            
            return f"{opcode}1{rd:04b}000000{imm_val:016b}"

    if instr in ["ld", "st"]:
       
        if len(parts) < 3:
            return f"Error: Missing operands for '{instr}' in line: {line}"
        elif len(parts) > 4:
            return f"Error: Unexpected operands for '{instr}' in line: {line}"
        if parts[1] not in registers:
            return f"Error: Invalid register(s) in '{instr}' in line: {line}"

        rd = registers[parts[1]]
        rs2 = parts[2]
        if rs2.startswith("["):
            a = rs2.find("[")
            
            temp = rs2[a+1:]
            
            if temp not in registers:
                return f"Error: Invalid register(s) in '{instr}' in line: {line}"
            rss1 = registers[temp]

            rs3=parts[3]
            b=rs3.find("]")
            temp2=rs3[:b]
            if temp2 in registers:
                return f"{opcode}0{rd:04b}{rss1:04b}{registers[temp2]:04b}".ljust(32, '0')
            else:
                imm_val = int(temp2)
                if imm_val < 0:
                    imm_val = (1 << 4) + imm_val
                return f"{opcode}1{rd:04b}{rss1:04b}{imm_val:04b}".ljust(32, '0')    
        else:
            a = rs2.find("[")
            b = rs2.find("]")
            rss1 = rs2[:a]
            
            if rs2[a+1:b] not in registers:
                return f"Error: Invalid register(s) in '{instr}' in line: {line}"
            rss2 = registers[rs2[a+1:b]]
            
            if rss1 in registers:
                return f"{opcode}0{rd:04b}{rss2:04b}{registers[rss1]:04b}".ljust(32, '0')
            else:
                imm_val = int(rss1)
                if imm_val < 0:
                    imm_val = (1 << 4) + imm_val
                return f"{opcode}1{rd:04b}{rss2:04b}{imm_val:04b}".ljust(32, '0')
    return f"Error: Unknown instruction '{instr}' in line: {line}"  # Ensure error return

def assemble_from_string(asm_code):
    labels_dict = {}
    lines = asm_code.splitlines()
    
    # First pass: Identify labels and their addresses
    address = 0
    for line in lines:
        if not line.strip():
            continue  # Skip empty lines
        
        # Check if the line contains a label
        if ":" in line:
            a = line.find(":")
            temp_label = line[:a].strip()  # Extract label without spaces
            labels_dict[temp_label] = address  # Store label and address
        
        address += 1  # Increment address for each instruction

    # Second pass: Assemble instructions
    result = []
    address = 0
    has_error = False
    
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue  # Skip empty lines
        
        binary_code = parse_instruction(line, address, labels_dict)
        if binary_code is None:
            continue  # Skip lines that only contain a label
        
        if binary_code.startswith("Error"):  # Error handling
            result.append(f"Error in line {line_number}: {line.strip()} → {binary_code}")
            has_error = True
        else:
            result.append(binary_code)
            address += 1  # Increment address for each instruction
    
    return result, has_error

# Input method tabs
tab1, tab2 = st.tabs(["Enter Assembly Code", "Upload ASM File"])

with tab1:
    default_code = """Example:
    mov r1, 10
    mov r2, 20
    add r3, r1, r2
    hlt"""
    
    asm_code = st.text_area("", 
                           placeholder=default_code, 
                           height=300)
    
    if st.button("Convert to Binary", key="convert_text"):
        if asm_code:
            binary_lines, has_error = assemble_from_string(asm_code)
            if has_error:
                st.markdown("<div class='error-message'>Errors found during assembly:</div>", unsafe_allow_html=True)
                for line in binary_lines:
                    st.markdown(f"<div class='error-message'>{line}</div>", unsafe_allow_html=True)
            else:
                binary_content = '\n'.join(binary_lines)
                
                # Create temporary file for download
                with tempfile.NamedTemporaryFile(delete=False, suffix='.bin', mode='w') as tmp_file:
                    tmp_file.write(binary_content)
                    tmp_path = tmp_file.name
                
                with open(tmp_path, 'rb') as f:
                    binary_data = f.read()
                
                st.download_button(
                    label="Download Binary File",
                    data=binary_data,
                    file_name="output.bin",
                    mime="application/octet-stream"
                )
                
                st.success("Assembly successful! Click the button above to download the binary file.")
                st.code(binary_content, language="text")
        else:
            st.warning("Please enter some assembly code.")

with tab2:
    uploaded_file = st.file_uploader("Upload an ASM file", type=["asm", "txt"])
    
    if uploaded_file is not None:
        asm_code = uploaded_file.getvalue().decode("utf-8")
        st.text_area("File Content", asm_code, height=300)
        
        if st.button("Convert to Binary", key="convert_file"):
            binary_lines, has_error = assemble_from_string(asm_code)
            if has_error:
                st.markdown("<div class='error-message'>Errors found during assembly:</div>", unsafe_allow_html=True)
                for line in binary_lines:
                    st.markdown(f"<div class='error-message'>{line}</div>", unsafe_allow_html=True)
            else:
                binary_content = '\n'.join(binary_lines)
                
                # Create temporary file for download
                with tempfile.NamedTemporaryFile(delete=False, suffix='.bin', mode='w') as tmp_file:
                    tmp_file.write(binary_content)
                    tmp_path = tmp_file.name
                
                with open(tmp_path, 'rb') as f:
                    binary_data = f.read()
                
                st.download_button(
                    label="Download Binary File",
                    data=binary_data,
                    file_name="output.bin",
                    mime="application/octet-stream"
                )
                
                st.success("Assembly successful! Click the button above to download the binary file.")
                st.code(binary_content, language="text")
               
