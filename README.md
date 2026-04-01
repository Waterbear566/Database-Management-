# 🎓 Student Database Management Studio v2.0

**Hệ quản trị cơ sở dữ liệu chuyên nghiệp với giao diện giống SQL Server Management Studio**

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🌟 Tính năng nổi bật

### 1. **Giao diện chuyên nghiệp**
- Thiết kế theo phong cách SQL Server Management Studio
- Dark theme chuyên nghiệp
- Multi-panel layout với Object Explorer, Query Editor, Results Panel

### 2. **SQL Query Editor**
- Editor với syntax highlighting
- Line numbers
- Execute queries với F5
- Save/Load SQL scripts
- Query templates (SELECT, INSERT, UPDATE, DELETE)

### 3. **Hỗ trợ SQL Commands**
```sql
SELECT * FROM students;
SELECT * FROM students WHERE ma_sv = 'SV001';
SELECT * FROM students WHERE ho_ten LIKE '%Nguyen%';

INSERT INTO students VALUES ('SV001', 'Name', 'Nam', '2003-01-01', 'CNTT01', 8.5);

UPDATE students SET diem_tb = 9.0 WHERE ma_sv = 'SV001';

DELETE FROM students WHERE ma_sv = 'SV001';

SHOW TABLES;
SHOW INDEXES;
SHOW STATS;

DESCRIBE students;
```

### 4. **Excel-like Data Grid**
- Xem và chỉnh sửa dữ liệu trực quan
- Add/Delete rows
- Sort by columns
- Search and filter

### 5. **B-Tree Index Visualization**
- Hiển thị cấu trúc cây B-Tree bằng đồ họa
- Text representation
- 2 indexes: ma_sv (Primary) và ho_ten (Secondary)
- Real-time updates

### 6. **File Operations**
- New/Open/Save Database
- Import/Export JSON
- Browse file system
- Auto-save support

### 7. **Command Terminal**
- Execute SQL commands
- View results in real-time
- Command history
- Messages panel

### 8. **SQL Guide Tab**
- Complete SQL command reference
- Examples and syntax
- Tips and best practices
- Integrated help system

## 📸 Screenshots

### Main Interface
```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  Query  View  Help                                │
├──────────┬──────────────────────────────────────────────────┤
│          │ 📝 SQL Query │ 📊 Data View │ 🌳 Index │ 📖 Guide│
│ Object   ├──────────────────────────────────────────────────┤
│ Explorer │                                                   │
│          │  SQL Query Editor                                 │
│ 🗄 DB    │  ──────────────────────────────────────────      │
│  ├ Tables│  SELECT * FROM students;                         │
│  │ └ 📊 │                                                   │
│  └ Index │                                                   │
│    ├ 🌳  │                                                   │
│    └ 🌳  │                                                   │
│          ├──────────────────────────────────────────────────┤
│ Status:  │ 📋 Results │ 💬 Messages │ 📜 History          │
│ Ready    │                                                   │
│ Records: │  Query results displayed here...                 │
│ 5        │                                                   │
└──────────┴──────────────────────────────────────────────────┘
```

## 🚀 Cài đặt và Sử dụng

### Yêu cầu hệ thống
- Python 3.7 hoặc cao hơn
- Tkinter (built-in với Python)

### Cài đặt
```bash
# Clone repository
git clone https://github.com/yourusername/student-db-studio.git
cd student-db-studio

# Chạy ứng dụng
python main.py
```

### Quick Start Guide

#### 1. Chạy SQL Query
```sql
-- Viết query trong SQL Editor
SELECT * FROM students WHERE diem_tb > 8.0;

-- Nhấn F5 hoặc click "Execute" button
```

#### 2. Thêm sinh viên qua GUI
- Switch sang tab "Data View"
- Click "Add Row"
- Điền thông tin
- Click "Add Student"

#### 3. Xem B-Tree Index
- Switch sang tab "Index View"
- Chọn index (ma_sv hoặc ho_ten)
- Xem visualization

#### 4. Save/Load Database
- File → Save Database (Ctrl+S)
- File → Open Database (Ctrl+O)
- Export/Import JSON

## 📖 SQL Command Reference

### SELECT Queries
```sql
-- Lấy tất cả
SELECT * FROM students;

-- Lấy theo điều kiện
SELECT * FROM students WHERE ma_sv = 'SV001';

-- Search với LIKE
SELECT * FROM students WHERE ho_ten LIKE '%Nguyen%';

-- Lấy columns cụ thể
SELECT ma_sv, ho_ten, diem_tb FROM students;
```

### INSERT
```sql
INSERT INTO students VALUES ('SV001', 'Nguyen Van A', 'Nam', '2003-05-15', 'CNTT01', 8.5);
```

### UPDATE
```sql
UPDATE students SET diem_tb = 9.0 WHERE ma_sv = 'SV001';
UPDATE students SET ho_ten = 'New Name', diem_tb = 9.5 WHERE ma_sv = 'SV001';
```

### DELETE
```sql
DELETE FROM students WHERE ma_sv = 'SV001';
```

### SHOW Commands
```sql
SHOW TABLES;      -- Hiện danh sách tables
SHOW INDEXES;     -- Hiện danh sách indexes
SHOW STATS;       -- Hiện thống kê database
```

### Other
```sql
DESCRIBE students;  -- Xem cấu trúc table
HELP;              -- Hiện hướng dẫn
CLEAR;             -- Xóa tất cả dữ liệu
```

## 🏗 Kiến trúc Hệ thống

### Cấu trúc Files
```
student-db-studio/
├── main.py              # GUI chính (SSMS-style)
├── database.py          # Database management
├── btree.py            # B-Tree implementation
├── sql_parser.py       # SQL parser & executor
├── README.md           # Documentation
├── requirements.txt    # Dependencies
└── LICENSE             # License file
```

### Components

#### 1. SQL Parser (`sql_parser.py`)
- Parse SQL commands
- Execute queries
- Return results
- Command history

#### 2. Database Manager (`database.py`)
- Student CRUD operations
- B-Tree index management
- Statistics tracking

#### 3. B-Tree Engine (`btree.py`)
- Order 3 B-Tree (t=2)
- Insert/Delete/Search: O(log n)
- Auto-balancing

#### 4. GUI (`main.py`)
- Multi-panel layout
- SQL editor
- Data grid
- Index visualization

## 🎯 Use Cases

### 1. Học tập về Database
- Hiểu cách SQL commands hoạt động
- Quan sát B-Tree indexing real-time
- Thực hành queries

### 2. Demo và Presentation
- Minh họa database operations
- Visualize index structures
- Show performance benefits

### 3. Data Management
- Quản lý danh sách sinh viên
- Import/Export data
- Generate reports

## 🔬 Advanced Features

### B-Tree Indexing
- **Order**: 3 (t=2)
- **Max keys per node**: 3
- **Min keys per node**: 1 (except root)
- **Search complexity**: O(log n)
- **Auto-balancing**: Split và Merge tự động

### SQL Parser
- Support multiple queries (separated by ;)
- WHERE clause with = and LIKE
- Comments with --
- Error handling

### File Format (JSON)
```json
{
  "students": [
    {
      "ma_sv": "SV001",
      "ho_ten": "Nguyen Van A",
      "gioi_tinh": "Nam",
      "ngay_sinh": "2003-05-15",
      "lop": "CNTT01",
      "diem_tb": 8.5
    }
  ],
  "metadata": {
    "created": "2024-01-01T00:00:00",
    "records": 1
  }
}
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

MIT License - See LICENSE file

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Inspired by SQL Server Management Studio
- B-Tree algorithm from "Introduction to Algorithms" (CLRS)
- Thanks to all contributors

---

**Note**: Đây là project giáo dục, không dùng cho production.

For questions or support, please open an issue on GitHub.
