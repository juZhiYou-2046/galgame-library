"""导入导出 API 路由"""

import csv
import io
import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Game

router = APIRouter(prefix="/api/games", tags=["导入导出"])

# 导出字段定义
EXPORT_FIELDS = [
    "title", "original_title", "developer", "release_date",
    "tags", "description", "rating", "folder_path",
]


@router.get("/export")
def export_games(format: str = "json", db: Session = Depends(get_db)):
    """导出所有游戏数据"""
    games = db.query(Game).order_by(Game.id).all()

    if format == "csv":
        return _export_csv(games)
    elif format == "json":
        return _export_json(games)
    else:
        raise HTTPException(status_code=400, detail="不支持的导出格式，请使用 json 或 csv")


def _export_json(games: list[Game]) -> StreamingResponse:
    """导出 JSON 格式"""
    data = []
    for game in games:
        item = {field: getattr(game, field, "") for field in EXPORT_FIELDS}
        data.append(item)

    content = json.dumps(data, ensure_ascii=False, indent=2)
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=galgame_library.json"},
    )


def _export_csv(games: list[Game]) -> StreamingResponse:
    """导出 CSV 格式"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for game in games:
        row = {field: getattr(game, field, "") for field in EXPORT_FIELDS}
        writer.writerow(row)

    content = output.getvalue()
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=galgame_library.csv"},
    )


@router.post("/import")
async def import_games(
    file: UploadFile = File(...),
    conflict_strategy: str = Form(default="skip"),
    db: Session = Depends(get_db),
):
    """
    批量导入游戏数据。
    conflict_strategy: skip（跳过已存在的）或 update（覆盖更新）
    """
    if conflict_strategy not in ("skip", "update"):
        raise HTTPException(status_code=400, detail="冲突策略必须为 skip 或 update")

    content = await file.read()
    filename = file.filename or ""

    try:
        if filename.endswith(".csv") or file.content_type == "text/csv":
            records = _parse_csv(content)
        else:
            records = _parse_json(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    # 执行导入
    created = 0
    updated = 0
    skipped = 0
    errors = []

    for idx, record in enumerate(records):
        title = record.get("title", "").strip()
        if not title:
            errors.append(f"第 {idx + 1} 行: 标题为空")
            continue

        # 查找是否已存在同名游戏
        existing = db.query(Game).filter(Game.title == title).first()

        if existing:
            if conflict_strategy == "update":
                for field in EXPORT_FIELDS:
                    if field in record and field != "title":
                        value = record[field]
                        if field == "rating":
                            try:
                                value = float(value) if value != "" else 0.0
                            except (ValueError, TypeError):
                                value = 0.0
                        setattr(existing, field, value)
                updated += 1
            else:
                skipped += 1
        else:
            game_data = {}
            for field in EXPORT_FIELDS:
                value = record.get(field, "")
                # rating 字段需要数值类型
                if field == "rating":
                    try:
                        game_data[field] = float(value) if value != "" else 0.0
                    except (ValueError, TypeError):
                        game_data[field] = 0.0
                else:
                    game_data[field] = str(value) if value else ""
            game = Game(**game_data)
            db.add(game)
            created += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {str(e)}")

    return {
        "total": len(records),
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
    }


def _parse_json(content: bytes) -> list[dict]:
    """解析 JSON 导入文件"""
    text = content.decode("utf-8-sig")
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("JSON 文件必须包含一个数组")
    return data


def _parse_csv(content: bytes) -> list[dict]:
    """解析 CSV 导入文件"""
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    return [row for row in reader]
