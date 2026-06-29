import os


def replace_code_block(
    filename: str,
    old_block: str,
    new_block: str,
) -> bool:
    """
    Replace an existing code block with a new one.

    Returns:
        True  -> Replacement successful
        False -> Old block not found
    """

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()

    # --------------------------------------
    # Normalize blocks
    # --------------------------------------

    old_block = old_block.rstrip("\n")
    new_block = new_block.rstrip("\n")

    # Ensure replacement ends with a newline
    new_block += "\n"

    if old_block not in content:

        print("\n❌ Original block not found.\n")

        return False

    # --------------------------------------
    # Replace first occurrence
    # --------------------------------------

    updated_content = content.replace(
        old_block,
        new_block,
        1
    )

    with open(filename, "w", encoding="utf-8") as file:
        file.write(updated_content)

    return True


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    test_file = "app.py"

    old_block = """        try:
            collection.delete(ids=[filename])
        except:
            pass"""

    new_block = """        try:
            collection.delete(ids=[filename])
        except Exception:
            pass"""

    success = replace_code_block(
        test_file,
        old_block,
        new_block,
    )

    print("=" * 60)

    if success:
        print("✔ Code block replaced successfully.")
    else:
        print("❌ Code block not found.")

    print("=" * 60)