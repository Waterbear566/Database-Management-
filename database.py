"""
Student Database Management System
Core logic for managing students with B-Tree indexing
"""

from btree import BTree
from datetime import datetime


class Student:
    """Student record class"""
    def __init__(self, ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb):
        self.ma_sv = ma_sv
        self.ho_ten = ho_ten
        self.gioi_tinh = gioi_tinh
        self.ngay_sinh = ngay_sinh
        self.lop = lop
        self.diem_tb = diem_tb
    
    def to_dict(self):
        return {
            'ma_sv': self.ma_sv,
            'ho_ten': self.ho_ten,
            'gioi_tinh': self.gioi_tinh,
            'ngay_sinh': self.ngay_sinh,
            'lop': self.lop,
            'diem_tb': self.diem_tb
        }
    
    def __repr__(self):
        return f"Student({self.ma_sv}, {self.ho_ten})"


class StudentDatabase:
    """Main database class with B-Tree indexing"""
    
    def __init__(self):
        self.students = []  # Main data table (list of Student objects)
        self.index_ma_sv = BTree(t=2)  # B-Tree index on Mã SV (order 3)
        self.index_ho_ten = BTree(t=2)  # B-Tree index on Họ tên (order 3)
        self.operation_log = []  # Log of operations for display
    
    def add_student(self, ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb):
        """Add a new student to the database"""
        # Check if student ID already exists
        if self.index_ma_sv.search(ma_sv) is not None:
            return False, "Mã sinh viên đã tồn tại!"
        
        # Create student object
        student = Student(ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb)
        
        # Add to main table
        row_index = len(self.students)
        self.students.append(student)
        
        # Add to indexes
        self.index_ma_sv.insert(ma_sv, row_index)
        self.index_ho_ten.insert(ho_ten.lower(), row_index)  # Lowercase for case-insensitive search
        
        # Log operation
        self.operation_log.append({
            'operation': 'INSERT',
            'ma_sv': ma_sv,
            'ho_ten': ho_ten,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        return True, f"Đã thêm sinh viên {ho_ten} (Mã: {ma_sv})"
    
    def delete_student(self, ma_sv):
        """Delete a student by ID"""
        # Search for student
        row_index = self.index_ma_sv.search(ma_sv)
        
        if row_index is None:
            return False, "Không tìm thấy sinh viên!"
        
        # Get student info before deletion
        student = self.students[row_index]
        ho_ten = student.ho_ten
        
        # Mark as deleted in main table (logical deletion)
        self.students[row_index] = None
        
        # Delete from indexes
        self.index_ma_sv.delete(ma_sv)
        self.index_ho_ten.delete(ho_ten.lower())
        
        # Log operation
        self.operation_log.append({
            'operation': 'DELETE',
            'ma_sv': ma_sv,
            'ho_ten': ho_ten,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        return True, f"Đã xóa sinh viên {ho_ten} (Mã: {ma_sv})"
    
    def search_by_ma_sv(self, ma_sv):
        """Search student by ID using B-Tree index"""
        row_index = self.index_ma_sv.search(ma_sv)
        
        if row_index is None or self.students[row_index] is None:
            return None
        
        return self.students[row_index]
    
    def search_by_ho_ten(self, ho_ten):
        """Search students by name using B-Tree index"""
        # Exact match search
        row_index = self.index_ho_ten.search(ho_ten.lower())
        
        if row_index is not None and self.students[row_index] is not None:
            return [self.students[row_index]]
        
        # Partial match search (fallback to linear search)
        results = []
        for i, student in enumerate(self.students):
            if student is not None and ho_ten.lower() in student.ho_ten.lower():
                results.append(student)
        
        return results if results else None
    
    def get_all_students(self):
        """Get all active students"""
        return [s for s in self.students if s is not None]
    
    def get_index_structure_ma_sv(self):
        """Get B-Tree structure for Mã SV index"""
        return self.index_ma_sv.get_tree_structure()
    
    def get_index_structure_ho_ten(self):
        """Get B-Tree structure for Họ tên index"""
        return self.index_ho_ten.get_tree_structure()
    
    def get_statistics(self):
        """Get database statistics"""
        active_students = len(self.get_all_students())
        total_records = len(self.students)
        deleted_records = total_records - active_students
        
        return {
            'active_students': active_students,
            'total_records': total_records,
            'deleted_records': deleted_records,
            'operations': len(self.operation_log)
        }
    
    def clear_database(self):
        """Clear all data"""
        self.students = []
        self.index_ma_sv = BTree(t=2)
        self.index_ho_ten = BTree(t=2)
        self.operation_log = []
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        sample_students = [
            ("SV001", "Nguyễn Văn An", "Nam", "2003-05-15", "CNTT01", 8.5),
            ("SV002", "Trần Thị Bình", "Nữ", "2003-08-20", "CNTT01", 7.8),
            ("SV003", "Lê Hoàng Cường", "Nam", "2003-03-10", "CNTT02", 9.0),
            ("SV004", "Phạm Thị Dung", "Nữ", "2003-12-01", "CNTT02", 8.2),
            ("SV005", "Hoàng Văn Em", "Nam", "2003-07-25", "CNTT01", 7.5),
        ]
        
        for student_data in sample_students:
            self.add_student(*student_data)
        
        return True, f"Đã tải {len(sample_students)} sinh viên mẫu"
