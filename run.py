from app import create_app

app = create_app()

@app.get("/")
def index():
    return {"hello": "world"}

if __name__ == "__main__":
    app.run(debug=True)