from fastapi import APIRouter
from app.schemas.query import FieldMetadata, TableMetadata, FieldsResponse
from typing import List

router = APIRouter()


@router.get("/fields", response_model=FieldsResponse)
async def get_fields():
    """Get all available fields for query builder"""
    
    # Define fields for each table
    tables = [
        TableMetadata(
            name="users",
            label="Users",
            fields=[
                FieldMetadata(
                    name="id",
                    label="ID",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">="]
                ),
                FieldMetadata(
                    name="first_name",
                    label="First Name",
                    type="text",
                    operators=["=", "!=", "contains", "beginsWith", "endsWith", "doesNotContain"]
                ),
                FieldMetadata(
                    name="last_name",
                    label="Last Name",
                    type="text",
                    operators=["=", "!=", "contains", "beginsWith", "endsWith", "doesNotContain"]
                ),
                FieldMetadata(
                    name="email",
                    label="Email",
                    type="text",
                    operators=["=", "!=", "contains", "beginsWith", "endsWith"]
                ),
                FieldMetadata(
                    name="age",
                    label="Age",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">=", "between"]
                ),
                FieldMetadata(
                    name="city",
                    label="City",
                    type="text",
                    operators=["=", "!=", "contains", "in", "notIn"]
                ),
                FieldMetadata(
                    name="country",
                    label="Country",
                    type="text",
                    operators=["=", "!=", "in", "notIn"]
                ),
                FieldMetadata(
                    name="is_active",
                    label="Is Active",
                    type="boolean",
                    valueEditorType="checkbox",
                    operators=["="],
                    defaultValue=True
                ),
            ]
        ),
        TableMetadata(
            name="products",
            label="Products",
            fields=[
                FieldMetadata(
                    name="id",
                    label="ID",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">="]
                ),
                FieldMetadata(
                    name="name",
                    label="Product Name",
                    type="text",
                    operators=["=", "!=", "contains", "beginsWith", "endsWith"]
                ),
                FieldMetadata(
                    name="category",
                    label="Category",
                    type="select",
                    values=["Electronics", "Furniture"],
                    operators=["=", "!=", "in", "notIn"]
                ),
                FieldMetadata(
                    name="price",
                    label="Price",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">=", "between"]
                ),
                FieldMetadata(
                    name="stock_quantity",
                    label="Stock Quantity",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">="]
                ),
                FieldMetadata(
                    name="is_available",
                    label="Is Available",
                    type="boolean",
                    valueEditorType="checkbox",
                    operators=["="],
                    defaultValue=True
                ),
            ]
        ),
        TableMetadata(
            name="orders",
            label="Orders",
            fields=[
                FieldMetadata(
                    name="id",
                    label="Order ID",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">="]
                ),
                FieldMetadata(
                    name="user_id",
                    label="User ID",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">="]
                ),
                FieldMetadata(
                    name="total_amount",
                    label="Total Amount",
                    type="number",
                    inputType="number",
                    operators=["=", "!=", "<", "<=", ">", ">=", "between"]
                ),
                FieldMetadata(
                    name="status",
                    label="Status",
                    type="select",
                    values=["pending", "completed", "shipped", "cancelled"],
                    operators=["=", "!=", "in", "notIn"]
                ),
            ]
        ),
    ]
    
    return FieldsResponse(tables=tables)


@router.get("/tables")
async def get_tables():
    """Get list of available tables"""
    return {
        "tables": [
            {"name": "users", "label": "Users"},
            {"name": "products", "label": "Products"},
            {"name": "orders", "label": "Orders"},
        ]
    }
