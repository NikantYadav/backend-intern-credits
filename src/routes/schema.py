from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from database import get_db, engine
import logging

router = APIRouter(prefix="/api/schema", tags=["schema"])
logger = logging.getLogger(__name__)

# Pydantic models for schema operations
class ColumnDefinition(BaseModel):
    name: str
    type: str  # e.g., "VARCHAR(255)", "INT", "DATETIME"
    nullable: bool = True
    default: Optional[str] = None

class TableDefinition(BaseModel):
    table_name: str
    columns: List[ColumnDefinition]

class AddColumnRequest(BaseModel):
    table_name: str
    column: ColumnDefinition

@router.get("/tables")
async def list_tables(db: AsyncSession = Depends(get_db)):
    """List all tables in the database"""
    try:
        result = await db.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result.fetchall()]
        return {"tables": tables}
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables/{table_name}/columns")
async def describe_table(table_name: str, db: AsyncSession = Depends(get_db)):
    """Get column information for a specific table"""
    try:
        result = await db.execute(text(f"DESCRIBE {table_name}"))
        columns = []
        for row in result.fetchall():
            columns.append({
                "field": row[0],
                "type": row[1],
                "null": row[2],
                "key": row[3],
                "default": row[4],
                "extra": row[5]
            })
        return {"table": table_name, "columns": columns}
    except Exception as e:
        logger.error(f"Error describing table {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tables")
async def create_table(table_def: TableDefinition, db: AsyncSession = Depends(get_db)):
    """Create a new table dynamically"""
    try:
        # Build CREATE TABLE statement
        columns_sql = []
        for col in table_def.columns:
            col_sql = f"`{col.name}` {col.type}"
            if not col.nullable:
                col_sql += " NOT NULL"
            if col.default:
                col_sql += f" DEFAULT {col.default}"
            columns_sql.append(col_sql)
        
        create_sql = f"""
        CREATE TABLE `{table_def.table_name}` (
            {', '.join(columns_sql)}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        await db.execute(text(create_sql))
        await db.commit()
        
        logger.info(f"Created table: {table_def.table_name}")
        return {"message": f"Table '{table_def.table_name}' created successfully"}
        
    except Exception as e:
        logger.error(f"Error creating table {table_def.table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/columns")
async def add_column(request: AddColumnRequest, db: AsyncSession = Depends(get_db)):
    """Add a new column to an existing table"""
    try:
        col = request.column
        col_sql = f"`{col.name}` {col.type}"
        if not col.nullable:
            col_sql += " NOT NULL"
        if col.default:
            col_sql += f" DEFAULT {col.default}"
        
        alter_sql = f"ALTER TABLE `{request.table_name}` ADD COLUMN {col_sql}"
        
        await db.execute(text(alter_sql))
        await db.commit()
        
        logger.info(f"Added column {col.name} to table {request.table_name}")
        return {"message": f"Column '{col.name}' added to table '{request.table_name}' successfully"}
        
    except Exception as e:
        logger.error(f"Error adding column to {request.table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/columns/{table_name}/{column_name}")
async def drop_column(table_name: str, column_name: str, db: AsyncSession = Depends(get_db)):
    """Drop a column from a table"""
    try:
        drop_sql = f"ALTER TABLE `{table_name}` DROP COLUMN `{column_name}`"
        
        await db.execute(text(drop_sql))
        await db.commit()
        
        logger.info(f"Dropped column {column_name} from table {table_name}")
        return {"message": f"Column '{column_name}' dropped from table '{table_name}' successfully"}
        
    except Exception as e:
        logger.error(f"Error dropping column {column_name} from {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tables/{table_name}")
async def drop_table(table_name: str, db: AsyncSession = Depends(get_db)):
    """Drop a table"""
    try:
        drop_sql = f"DROP TABLE `{table_name}`"
        
        await db.execute(text(drop_sql))
        await db.commit()
        
        logger.info(f"Dropped table {table_name}")
        return {"message": f"Table '{table_name}' dropped successfully"}
        
    except Exception as e:
        logger.error(f"Error dropping table {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reflect")
async def reflect_schema():
    """Reflect current database schema and return structure"""
    try:
        async with engine.begin() as conn:
            # Get table names
            result = await conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            schema = {}
            for table_name in tables:
                # Get column info for each table
                result = await conn.execute(text(f"DESCRIBE {table_name}"))
                columns = []
                for row in result.fetchall():
                    columns.append({
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "key": row[3],
                        "default": row[4],
                        "extra": row[5]
                    })
                schema[table_name] = columns
            
            return {"schema": schema}
            
    except Exception as e:
        logger.error(f"Error reflecting schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))