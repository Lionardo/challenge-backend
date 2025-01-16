from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Supabase app!"}

@router.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "message": "Item retrieved successfully."}

@router.post("/items/")
async def create_item(item: dict):
    return {"item": item, "message": "Item created successfully."}