import os
def save_file(filename: str, code: str):

    folder = os.path.dirname(filename)

    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"Saved: {filename}")