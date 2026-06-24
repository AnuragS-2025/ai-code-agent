def apply_health_endpoint():

    with open("codebase/app.py", "a", encoding="utf-8") as f:

        f.write(
            """

@app.get("/health")
def health():
    return {"status": "ok"}
"""
        )

    print("Endpoint added.")