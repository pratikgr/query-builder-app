"""
Service for converting query builder JSON to SQL
"""
from typing import Dict, Any, List, Tuple
from sqlalchemy import and_, or_, not_, select
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
        
        # Handle IN / NOT IN with optional subquery
        try:
            if operator in ("in", "notIn"):
                # subquery may be provided in rule['subquery'] or as the value
                sub = None
                if isinstance(rule.get("subquery"), dict):
                    sub = rule.get("subquery")
                elif isinstance(value, dict) and "query" in value and "table_name" in value:
                    sub = value

                if sub:
                    sub_query_group = sub.get("query")
                    sub_table = sub.get("table_name")
                    sub_select_field = sub.get("select_field") or sub.get("selectField")
                    sub_select_fields = sub.get("select_fields") or sub.get("selectFields") or []

                    sub_model = cls.TABLE_MODELS.get(sub_table)
                    if not sub_model:
                        raise ValueError(f"Subquery table '{sub_table}' not found")

                    sub_conditions = cls.build_query_conditions(sub_model, sub_query_group) if sub_query_group else None

                    # Always use the primary key (first column/id) for IN comparison
                    pk_col = list(sub_model.__table__.columns)[0]
                    
                    stmt = select(pk_col)
                    if sub_conditions is not None:
                        stmt = stmt.where(sub_conditions)
                    subselect = stmt.scalar_subquery()

                    if operator == "in":
                        return field.in_(subselect)
                    else:
                        return ~field.in_(subselect)

                # otherwise fall back to list/string handling
                return operator_func(field, value)

            # default apply
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
    def extract_subquery_info(cls, query_group: Dict[str, Any]):
        """Extract subquery metadata from query rules"""
        rules = query_group.get("rules", [])
        subqueries = []
        
        for rule in rules:
            if "rules" in rule:
                # Nested group
                subqueries.extend(cls.extract_subquery_info(rule))
            else:
                # Single rule
                operator = rule.get("operator")
                value = rule.get("value")
                
                if operator in ("in", "notIn"):
                    sub = None
                    if isinstance(rule.get("subquery"), dict):
                        sub = rule.get("subquery")
                    elif isinstance(value, dict) and "query" in value and "table_name" in value:
                        sub = value
                    
                    if sub:
                        select_fields = sub.get("select_fields") or sub.get("selectFields") or []
                        if len(select_fields) > 1:  # Multiple fields = use JOIN
                            subqueries.append({
                                "field": rule.get("field"),
                                "table": sub.get("table_name"),
                                "select_fields": select_fields,
                                "conditions": sub.get("query"),
                            })
        
        return subqueries

    @classmethod
    def execute_query(cls, db: Session, query_group: Dict[str, Any], table_name: str, limit: int = 100) -> Tuple[List[Dict], str]:
        """Execute query and return results"""
        # Get the model
        model = cls.TABLE_MODELS.get(table_name)
        if not model:
            raise ValueError(f"Table '{table_name}' not found")
        
        # Check for subqueries with multiple fields that need JOINs
        subquery_info = cls.extract_subquery_info(query_group)
        
        if subquery_info:
            # Use JOIN-based approach for multiple fields
            return cls.execute_query_with_joins(db, model, query_group, subquery_info, limit)
        else:
            # Standard IN-based approach
            query = db.query(model)
            
            # Build conditions
            conditions = cls.build_query_conditions(model, query_group)
            
            if conditions is not None:
                query = query.filter(conditions)
            
            # Apply limit
            query = query.limit(limit)
            
            # Get SQL string
            sql_query = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
            
            # Execute and get results
            results = query.all()
            
            # Convert to dictionaries
            data = []
            for row in results:
                row_dict = {}
                for column in row.__table__.columns:
                    value = getattr(row, column.name)
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[column.name] = value
                data.append(row_dict)
            
            return data, sql_query
    
    @classmethod
    def execute_query_with_joins(cls, db: Session, main_model, query_group: Dict[str, Any], subquery_info: List[Dict], limit: int = 100) -> Tuple[List[Dict], str]:
        """Execute query with JOINs for subqueries with multiple fields"""
        from sqlalchemy import select
        
        # Build SELECT columns list
        main_cols = list(main_model.__table__.columns)
        select_cols = list(main_cols)
        
        # Build joins and collect joined columns
        from_clause = main_model
        joined_models_dict = {}
        
        for sub_info in subquery_info:
            sub_table_name = sub_info["table"]
            sub_model = cls.TABLE_MODELS.get(sub_table_name)
            if not sub_model:
                continue
            
            # Add selected fields from subquery to select list
            for field_name in sub_info.get("select_fields", []):
                if hasattr(sub_model, field_name):
                    select_cols.append(getattr(sub_model, field_name))
            
            # Track for joining
            joined_models_dict[sub_table_name] = (sub_model, sub_info)
        
        # Build SQL statement with explicit joins
        stmt = select(*select_cols)
        
        # Add joins
        for sub_table_name, (sub_model, sub_info) in joined_models_dict.items():
            from sqlalchemy import and_
            # Join on the foreign key
            main_fk_field = sub_info["field"]
            if hasattr(main_model, main_fk_field):
                # Get the PK of the subquery table (assume first column)
                sub_pk = list(sub_model.__table__.columns)[0]
                stmt = stmt.join(
                    sub_model,
                    getattr(main_model, main_fk_field) == sub_pk
                )
        
        # Build and apply conditions
        conditions = cls.build_query_conditions(main_model, query_group)
        if conditions is not None:
            stmt = stmt.where(conditions)
        
        # Apply limit
        stmt = stmt.limit(limit)
        
        # Get SQL string
        sql_query = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        
        # Execute
        result = db.execute(stmt)
        rows = result.fetchall()
        
        # Convert to dictionaries
        data = []
        for row in rows:
            row_dict = {}
            col_idx = 0
            
            # Main model columns
            for column in main_cols:
                if col_idx < len(row):
                    row_dict[column.name] = row[col_idx]
                    col_idx += 1
            
            # Joined model columns
            for sub_table_name, (sub_model, sub_info) in joined_models_dict.items():
                for field_name in sub_info.get("select_fields", []):
                    if hasattr(sub_model, field_name) and col_idx < len(row):
                        value = row[col_idx]
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        row_dict[f"{sub_table_name}.{field_name}"] = value
                        col_idx += 1
            
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
