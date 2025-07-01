import subprocess
import os
from optimizacion import optimize_code 
import sys

# Carpeta de entrada
input_dir = "inputs"

# Archivos fuente
#source_files = [
#    "main.cpp", "parser.cpp", "scanner.cpp", "token.cpp",
#    "visitor.cpp", "exp.cpp"
#]
source_files=['*.cpp']

if not source_files:
    print("No se encontraron archivos .cpp")
    sys.exit(1)

# Compilar
print("Compilando...")
compile_cmd = ["g++"] + source_files
result = subprocess.run(compile_cmd)

if result.returncode != 0:
    print("Error de compilación.")
    exit(1)

print("Compilación exitosa.\n")

for i in range(1, 15):
    
    input_file = os.path.join(input_dir, f"input{i}.txt")


    if not os.path.exists(input_file):
        print(f"{input_dir} no existe. Se omite.")
        continue
    input_file_optimized= os.path.join(input_dir, f"input{i}_optimized.txt")
    optimize_code(input_file,input_file_optimized)

    print(f"\nEjecutando con {input_file}")
    subprocess.run(["./a.exe", input_file])