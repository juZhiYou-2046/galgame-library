"""本地扫描 API 路由"""

import os
from pathlib import Path

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from app.services.scanner import ScannerService

router = APIRouter(prefix="/api/scan", tags=["扫描"])


class ScanRequest(BaseModel):
    directory: str
    max_depth: int = 3


class ScanResponse(BaseModel):
    directory: str
    files_found: int
    items: list[dict]


@router.post("", response_model=ScanResponse)
def scan_directory(data: ScanRequest):
    """扫描本地目录，查找游戏文件"""
    directory = Path(data.directory).resolve()

    if not directory.exists():
        raise HTTPException(status_code=400, detail="目录不存在")
    if not directory.is_dir():
        raise HTTPException(status_code=400, detail="路径不是目录")

    # 安全检查：不允许扫描系统目录
    forbidden_prefixes = ["/System", "/Library", "/etc", "/dev", "/proc", "/sys"]
    if any(str(directory).startswith(p) for p in forbidden_prefixes):
        raise HTTPException(status_code=403, detail="不允许扫描系统目录")

    items = ScannerService.scan_directory(str(directory), max_depth=data.max_depth)
    return ScanResponse(
        directory=str(directory),
        files_found=len(items),
        items=items,
    )