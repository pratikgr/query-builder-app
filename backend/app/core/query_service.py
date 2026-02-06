"""
Service for converting query builder JSON to SQL
"""
from typing import Dict, Any, List, Tuple
from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import Session
from app.db.models import User, Product, Order, OrderItem


class QueryService:
    """Service to handle query building and execution"""
    
    # Mapping of table names to models
    TABLE_MODELS = {
        "users": User,
        "products": Product,
        "orders": Order,
        "order_items": OrderItem,
    }
    
    # Operator mapping
    OPERATORS = {
        "=": lambda field, value: field == value,
        "!=": lambda field, value: field != value,
        "<": lambda field, value: field < value,
        "<=": lambda field, value: field <= value,
        ">": lambda field, value: field > value,
        ">=": lambda field, value: field >= value,
        "contains": lambda field, value: field.contains(value),
        "beginsWith": lambda field, value: field.like(f"{value}%"),
        "endsWith": lambda field, value: field.like(f"%{value}"),
        "doesNotContain": lambda field, value: ~field.contains(value),
        "doesNotBeginWith": lambda field, value: ~field.like(f"{value}%"),
        "doesNotEndWith": lambda field, value: ~field.like(f"%{value}"),
        "null": lambda field, value: field.is_(None),
        "notNull": lambda field, value: field.isnot(None),
        "in": lambda field, value: field.in_(value.split(",") if isinstance(value, str) else value),
        "notIn": lambda field, value: ~field.in_(value.split(",") if isinstance(value, str) else value),
        "between": lambda field, value: field.between(*value) if isinstance(value, (list, tuple)) else None,
    }
    
    @classmethod
    def build_filter(cls, model, rule: Dict[str, Any]):
        """Build a single filter condition"""
        field_name = rule.get("field")
        operator = rule.get("operator")
        value = rule.get("value")
        
        if not field_name or not operator:
            return None
        
        # Get the field from the model
        if not hasattr(model, field_name):
            raise ValueError(f"Field '{field_name}' not found in model")
        
        field = getattr(model, field_name)
        
        # Get operator function
        operator_func = cls.OPERATORS.get(operator)
        if not operator_func:
            raise ValueError(f"Operator '{operator}' not supported")
        
        # Handle special cases
        if operator in ["null", "notNull"]:
            return operator_func(field, None)
        
        if value is None and operator not in ["null", "notNull"]:
            return None
        
        # Apply the operator
        try:
            return operator_func(field, value)
        except Exception as e:
            raise ValueError(f"Error applying operator '{operator}': {str(e)}")
    
    @classmethod
    def build_query_conditions(cls, model, query_group: Dict[str, Any]):
        """Recursively build query conditions from query group"""
        combinator = query_group.get("combinator", "and")
        rules = query_group.get("rules", [])
        not_flag = query_group.get("not", False)
        
        conditions = []
        
        for rule in rules:
            if "rules" in rule:
                # It's a nested group
                nested_condition = cls.build_query_conditions(model, rule)
                if nested_condition is not None:
                    conditions.append(nested_condition)
            else:
                # It's a single rule
                condition = cls.build_filter(model, rule)
                if condition is not None:
                    conditions.append(condition)
        
        if not conditions:
            return None
        
        # Combine conditions
        if combinator.lower() == "and":
            combined = and_(*conditions)
        else:  # or
            combined = or_(*conditions)
        
        # Apply NOT if specified
        if not_flag:
            combined = not_(combined)
        
        return combined
    
    @classmethod
    def execute_query(cls, db: Session, query_group: Dict[str, Any], table_name: str, limit: int = 100) -> Tuple[List[Dict], str]:
        """Execute query and return results"""
        # Get the model
        model = cls.TABLE_MODELS.get(table_name)
        if not model:
            raise ValueError(f"Table '{table_name}' not found")
        
        # Build the query
        query = db.query(model)
        
        # Build conditions
        conditions = cls.build_query_conditions(model, query_group)
        
        if conditions is not None:
            query = query.filter(conditions)
        
        # Apply limit
        query = query.limit(limit)
        
        # Get SQL string (for display)
        sql_query = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
        
        # Execute and get results
        results = query.all()
        
        # Convert to dictionaries
        data = []
        for row in results:
            row_dict = {}
            for column in row.__table__.columns:
                value = getattr(row, column.name)
                # Convert datetime to string
                if hasattr(value, 'isoformat'):
                    value = value.isoformat()
                row_dict[column.name] = value
            data.append(row_dict)
        
        return data, sql_query
    
    @classmethod
    def query_to_sql(cls, query_group: Dict[str, Any], table_name: str) -> str:
        """Convert query to SQL string (without executing)"""
        model = cls.TABLE_MODELS.get(table_name)
        if not model:
            raise ValueError(f"Table '{table_name}' not found")
        
        from sqlalchemy import select
        
        # Build the select statement
        stmt = select(model)
        
        # Build conditions
        conditions = cls.build_query_conditions(model, query_group)
        
        if conditions is not None:
            stmt = stmt.where(conditions)
        
        # Compile to SQL
        sql_query = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        
        return sql_query
