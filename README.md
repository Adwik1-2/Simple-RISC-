# Assembly to Binary Converter

This project is an **Assembly to Binary Converter** that translates assembly code into its corresponding binary representation. It includes a **Streamlit-based GUI** for easy interaction, allowing users to write assembly code directly in the app, assemble it, and download the binary output.

---

## Features

- **Assembly Code Input**: Write or paste assembly code directly into the app.
- **Binary Output**: View the binary representation of the assembly code.
- **Error Handling**: Displays detailed error messages for invalid assembly instructions.
- **Download Binary**: Download the binary output as a `.bin` file.
- **Streamlit GUI**: A user-friendly web interface for easy interaction.

---

## How It Works

1. The user writes assembly code in the provided text area.
2. The app processes each line of assembly code using the `parse_instruction` function.
3. Valid assembly instructions are converted into binary.
4. Errors (if any) are displayed in the app.
5. The binary output is displayed and can be downloaded as a `.bin` file.

---

## Installation

To run this project locally, follow these steps:

### Prerequisites

- Python 3.x
- Streamlit

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/assembly-to-binary-converter.git
   cd assembly-to-binary-converter
2.Install the required dependencies:
pip install streamlit

3.Run the Streamlit app:
streamlit run app.py

## Supported Instructions
The following assembly instructions are supported:

Instruction	Description
add	Addition
sub	Subtraction
mul	Multiplication
div	Division
mod	Modulus
cmp	Compare
and	Bitwise AND
or	Bitwise OR
not	Bitwise NOT
mov	Move
lsl	Logical Shift Left
lsr	Logical Shift Right
asr	Arithmetic Shift Right
nop	No Operation
ld	Load
st	Store
beq	Branch if Equal
bgt	Branch if Greater Than
b	Unconditional Branch
call	Call Subroutine
ret	Return from Subroutine
hlt	Halt

