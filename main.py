from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/vapi")
async def vapi(request: Request):
    data = await request.json()
    print(data)
    return {"success": True}

