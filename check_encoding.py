with open('employees/urls.py', 'rb') as f:
    content = f.read()
    print(f"Total bytes: {len(content)}")
    for i, byte in enumerate(content):
        if byte > 127:
            print(f"Non-ASCII byte at offset {i}: {byte}")

print("Checking for hidden characters...")
import reprlib
print(reprlib.repr(content[:500]))
