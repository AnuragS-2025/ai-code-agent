import os

def read_codebase(folder="codebase"):
    context = ""

    for filename in os.listdir(folder):

        path = os.path.join(folder, filename)

        if os.path.isfile(path):

            with open(path, "r", encoding="utf-8") as f:

                context += f"\n\nFILE: {filename}\n"
                context += f.read()

    return context