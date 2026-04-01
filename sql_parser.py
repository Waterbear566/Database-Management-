"""
SQL Parser and Executor
Supports basic SQL commands for student database
"""

import re
from datetime import datetime


class SQLParser:
    """Parse and execute SQL-like commands"""
    
    def __init__(self, database):
        self.db = database
        self.command_history = []
    
    def parse_and_execute(self, sql_command):
        """Parse SQL command and execute it"""
        sql_command = sql_command.strip()
        
        if not sql_command:
            return False, "Empty command", None
        
        # Add to history
        self.command_history.append({
            'command': sql_command,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Convert to uppercase for parsing
        cmd_upper = sql_command.upper()
        
        try:
            # SELECT queries
            if cmd_upper.startswith('SELECT'):
                return self._execute_select(sql_command)
            
            # INSERT queries
            elif cmd_upper.startswith('INSERT'):
                return self._execute_insert(sql_command)
            
            # DELETE queries
            elif cmd_upper.startswith('DELETE'):
                return self._execute_delete(sql_command)
            
            # UPDATE queries
            elif cmd_upper.startswith('UPDATE'):
                return self._execute_update(sql_command)
            
            # SHOW queries
            elif cmd_upper.startswith('SHOW'):
                return self._execute_show(sql_command)
            
            # DESCRIBE queries
            elif cmd_upper.startswith('DESCRIBE') or cmd_upper.startswith('DESC'):
                return self._execute_describe(sql_command)
            
            # HELP command
            elif cmd_upper.startswith('HELP'):
                return self._execute_help(sql_command)
            
            # CLEAR command
            elif cmd_upper.startswith('CLEAR'):
                self.db.clear_database()
                return True, "Database cleared successfully", None
            
            else:
                return False, f"Unknown command: {sql_command.split()[0]}", None
        
        except Exception as e:
            return False, f"Error executing command: {str(e)}", None
    
    def _execute_select(self, sql):
        """Execute SELECT query"""
        # SELECT * FROM students
        # SELECT * FROM students WHERE ma_sv = 'SV001'
        # SELECT ma_sv, ho_ten FROM students
        
        match = re.match(
            r'SELECT\s+(.+?)\s+FROM\s+students(?:\s+WHERE\s+(.+))?',
            sql,
            re.IGNORECASE
        )
        
        if not match:
            return False, "Invalid SELECT syntax", None
        
        columns = match.group(1).strip()
        where_clause = match.group(2)
        
        # Get all students
        students = self.db.get_all_students()
        
        if not students:
            return True, "No records found", []
        
        # Apply WHERE clause
        if where_clause:
            students = self._filter_students(students, where_clause)
        
        # Select columns
        if columns == '*':
            result = [s.to_dict() for s in students]
        else:
            col_names = [c.strip() for c in columns.split(',')]
            result = []
            for s in students:
                row = {}
                s_dict = s.to_dict()
                for col in col_names:
                    if col in s_dict:
                        row[col] = s_dict[col]
                result.append(row)
        
        return True, f"Retrieved {len(result)} row(s)", result
    
    def _execute_insert(self, sql):
        """Execute INSERT query"""
        # INSERT INTO students VALUES ('SV001', 'Name', 'Nam', '2003-01-01', 'CNTT01', 8.5)
        # INSERT INTO students (ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb) 
        #        VALUES ('SV001', 'Name', 'Nam', '2003-01-01', 'CNTT01', 8.5)
        
        # Simple VALUES pattern
        match = re.match(
            r'INSERT\s+INTO\s+students\s+VALUES\s*\((.+)\)',
            sql,
            re.IGNORECASE
        )
        
        if match:
            values_str = match.group(1)
            values = self._parse_values(values_str)
            
            if len(values) != 6:
                return False, "INSERT requires 6 values (ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb)", None
            
            ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb = values
            
            try:
                diem_tb = float(diem_tb)
            except ValueError:
                return False, "diem_tb must be a number", None
            
            success, message = self.db.add_student(ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb)
            return success, message, None
        
        return False, "Invalid INSERT syntax", None
    
    def _execute_delete(self, sql):
        """Execute DELETE query"""
        # DELETE FROM students WHERE ma_sv = 'SV001'
        
        match = re.match(
            r'DELETE\s+FROM\s+students\s+WHERE\s+ma_sv\s*=\s*[\'"](.+?)[\'"]',
            sql,
            re.IGNORECASE
        )
        
        if match:
            ma_sv = match.group(1)
            success, message = self.db.delete_student(ma_sv)
            return success, message, None
        
        return False, "Invalid DELETE syntax. Use: DELETE FROM students WHERE ma_sv = 'XXX'", None
    
    def _execute_update(self, sql):
        """Execute UPDATE query"""
        # UPDATE students SET diem_tb = 9.0 WHERE ma_sv = 'SV001'
        
        match = re.match(
            r'UPDATE\s+students\s+SET\s+(.+?)\s+WHERE\s+ma_sv\s*=\s*[\'"](.+?)[\'"]',
            sql,
            re.IGNORECASE
        )
        
        if match:
            set_clause = match.group(1)
            ma_sv = match.group(2)
            
            # Find student
            student = self.db.search_by_ma_sv(ma_sv)
            if not student:
                return False, f"Student {ma_sv} not found", None
            
            # Parse SET clause
            updates = {}
            for pair in set_clause.split(','):
                key, value = pair.split('=')
                key = key.strip()
                value = value.strip().strip('"\'')
                updates[key] = value
            
            # Update student
            for key, value in updates.items():
                if hasattr(student, key):
                    if key == 'diem_tb':
                        value = float(value)
                    setattr(student, key, value)
            
            return True, f"Updated student {ma_sv}", None
        
        return False, "Invalid UPDATE syntax", None
    
    def _execute_show(self, sql):
        """Execute SHOW command"""
        cmd_upper = sql.upper()
        
        if 'TABLES' in cmd_upper:
            return True, "Tables in database", [{'table': 'students'}]
        
        elif 'INDEX' in cmd_upper or 'INDEXES' in cmd_upper:
            indexes = [
                {'index_name': 'idx_ma_sv', 'column': 'ma_sv', 'type': 'B-Tree'},
                {'index_name': 'idx_ho_ten', 'column': 'ho_ten', 'type': 'B-Tree'}
            ]
            return True, "Indexes on students table", indexes
        
        elif 'STATS' in cmd_upper or 'STATISTICS' in cmd_upper:
            stats = self.db.get_statistics()
            result = [
                {'metric': 'Active Students', 'value': stats['active_students']},
                {'metric': 'Total Records', 'value': stats['total_records']},
                {'metric': 'Deleted Records', 'value': stats['deleted_records']},
                {'metric': 'Total Operations', 'value': stats['operations']}
            ]
            return True, "Database statistics", result
        
        return False, "Invalid SHOW syntax", None
    
    def _execute_describe(self, sql):
        """Execute DESCRIBE command"""
        schema = [
            {'Field': 'ma_sv', 'Type': 'VARCHAR(10)', 'Null': 'NO', 'Key': 'PRI'},
            {'Field': 'ho_ten', 'Type': 'VARCHAR(100)', 'Null': 'NO', 'Key': 'MUL'},
            {'Field': 'gioi_tinh', 'Type': 'VARCHAR(10)', 'Null': 'YES', 'Key': ''},
            {'Field': 'ngay_sinh', 'Type': 'DATE', 'Null': 'YES', 'Key': ''},
            {'Field': 'lop', 'Type': 'VARCHAR(20)', 'Null': 'YES', 'Key': ''},
            {'Field': 'diem_tb', 'Type': 'FLOAT', 'Null': 'YES', 'Key': ''}
        ]
        return True, "Table structure: students", schema
    
    def _execute_help(self, sql):
        """Show help information"""
        help_text = """
Available SQL Commands:

SELECT:
  SELECT * FROM students
  SELECT ma_sv, ho_ten FROM students
  SELECT * FROM students WHERE ma_sv = 'SV001'
  SELECT * FROM students WHERE ho_ten LIKE '%Nguyen%'

INSERT:
  INSERT INTO students VALUES ('SV001', 'Name', 'Nam', '2003-01-01', 'CNTT01', 8.5)

UPDATE:
  UPDATE students SET diem_tb = 9.0 WHERE ma_sv = 'SV001'
  UPDATE students SET ho_ten = 'New Name', diem_tb = 9.5 WHERE ma_sv = 'SV001'

DELETE:
  DELETE FROM students WHERE ma_sv = 'SV001'

SHOW:
  SHOW TABLES
  SHOW INDEXES
  SHOW STATS

DESCRIBE:
  DESCRIBE students
  DESC students

OTHER:
  CLEAR - Clear all database
  HELP - Show this help
"""
        return True, help_text, None
    
    def _filter_students(self, students, where_clause):
        """Filter students based on WHERE clause"""
        # Simple WHERE parsing
        # ma_sv = 'SV001'
        # ho_ten LIKE '%Nguyen%'
        
        filtered = []
        
        for student in students:
            s_dict = student.to_dict()
            
            # Equal condition
            if '=' in where_clause and 'LIKE' not in where_clause.upper():
                parts = where_clause.split('=')
                field = parts[0].strip()
                value = parts[1].strip().strip('"\'')
                
                if field in s_dict and str(s_dict[field]) == value:
                    filtered.append(student)
            
            # LIKE condition
            elif 'LIKE' in where_clause.upper():
                match = re.match(r'(\w+)\s+LIKE\s+[\'"](.+?)[\'"]', where_clause, re.IGNORECASE)
                if match:
                    field = match.group(1)
                    pattern = match.group(2).replace('%', '.*')
                    
                    if field in s_dict and re.search(pattern, str(s_dict[field]), re.IGNORECASE):
                        filtered.append(student)
        
        return filtered
    
    def _parse_values(self, values_str):
        """Parse VALUES string into list"""
        # Handle quoted strings
        values = []
        current = ''
        in_quotes = False
        quote_char = None
        
        for char in values_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ',' and not in_quotes:
                values.append(current.strip().strip('"\''))
                current = ''
            else:
                current += char
        
        if current:
            values.append(current.strip().strip('"\''))
        
        return values
    
    def get_command_history(self):
        """Get command history"""
        return self.command_history[-50:]  # Last 50 commands
