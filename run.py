import uvicorn

if __name__ == "__main__":
    # You can also run this using `fastapi dev app/main.py` if using fastapi[standard]
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)