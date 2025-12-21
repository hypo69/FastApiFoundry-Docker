# -*- coding: utf-8 -*-
from fastapi import APIRouter

router = APIRouter()

@router.get("/rag/search")
async def rag_search():
    return {"results": []}