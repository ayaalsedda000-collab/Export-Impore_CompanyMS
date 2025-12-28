import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st

class Database:
    def __init__(self, db_name="company_data.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name TEXT NOT NULL,
                department TEXT NOT NULL,
                position TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM company_records")
        if cursor.fetchone()[0] == 0:
            sample_data = [
                ('Ahmed Mohammed', 'IT', 'Software Developer', 5000, '2023-01-15', 'ahmed@company.com', '0501234567', 'Active'),
                ('Fatima Ali', 'HR', 'HR Manager', 6000, '2022-06-10', 'fatima@company.com', '0507654321', 'Active'),
                ('Mohammed Khalid', 'Sales', 'Sales Representative', 4500, '2023-03-20', 'mohammed@company.com', '0509876543', 'Active'),
                ('Sara Ahmed', 'Marketing', 'Marketing Specialist', 4800, '2023-02-01', 'sara@company.com', '0502345678', 'Active'),
                ('Abdullah Youssef', 'Finance', 'Accountant', 5200, '2022-09-15', 'abdullah@company.com', '0508765432', 'Active'),
            ]
            cursor.executemany('''
                INSERT INTO company_records (employee_name, department, position, salary, hire_date, email, phone, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_data)
        
        conn.commit()
        conn.close()

    def init_users_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in cursor.fetchall()]
        if 'role' not in cols:
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            except Exception:
                pass
        conn.commit()
        conn.close()

    def create_user(self, email, password_hash, salt, role='user'):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, salt, role)
                VALUES (?, ?, ?, ?)
            ''', (email, password_hash, salt, role))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, password_hash, salt, role, created_at FROM users WHERE email=?', (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0],
                'email': row[1],
                'password_hash': row[2],
                'salt': row[3],
                'role': row[4],
                'created_at': row[5]
            }
        return None

    def init_leave_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                reason TEXT,
                leave_type TEXT DEFAULT 'Other',
                attachment TEXT DEFAULT '',
                status TEXT DEFAULT 'Pending',
                admin_response TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        cursor.execute("PRAGMA table_info(leave_requests)")
        cols = [r[1] for r in cursor.fetchall()]
        if 'leave_type' not in cols:
            try:
                cursor.execute("ALTER TABLE leave_requests ADD COLUMN leave_type TEXT DEFAULT 'Other'")
                conn.commit()
            except Exception:
                pass
        if 'attachment' not in cols:
            try:
                cursor.execute("ALTER TABLE leave_requests ADD COLUMN attachment TEXT DEFAULT ''")
                conn.commit()
            except Exception:
                pass
        if 'admin_response' not in cols:
            try:
                cursor.execute("ALTER TABLE leave_requests ADD COLUMN admin_response TEXT DEFAULT ''")
                conn.commit()
            except Exception:
                pass
        conn.close()

    def create_leave_request(self, user_id, start_date, end_date, reason, leave_type='Other', attachment=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leave_requests (user_id, start_date, end_date, reason, leave_type, attachment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, start_date, end_date, reason, leave_type, attachment))
        conn.commit()
        conn.close()

    def get_leave_requests_by_user(self, user_id):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM leave_requests WHERE user_id=? ORDER BY id DESC', conn, params=(user_id,))
        conn.close()
        return df

    def get_all_leave_requests(self):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT lr.id, lr.user_id, u.email as user_email, lr.start_date, lr.end_date, lr.reason, lr.leave_type, lr.attachment, lr.status, lr.admin_response, lr.created_at FROM leave_requests lr JOIN users u ON lr.user_id=u.id ORDER BY lr.id DESC', conn)
        conn.close()
        return df

    def update_leave_request_status(self, request_id, status, admin_response=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if admin_response is None:
            cursor.execute('UPDATE leave_requests SET status=? WHERE id=?', (status, request_id))
        else:
            cursor.execute('UPDATE leave_requests SET status=?, admin_response=? WHERE id=?', (status, admin_response, request_id))
        conn.commit()
        conn.close()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        return conn

    def get_all_users(self):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT id, email, role, created_at FROM users ORDER BY id DESC', conn)
        conn.close()
        return df

    def update_user_role(self, user_id, role):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET role=? WHERE id=?', (role, user_id))
        conn.commit()
        conn.close()
    
    def get_all_records(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM company_records ORDER BY id DESC", conn)
        conn.close()
        return df
    
    def add_record(self, employee_name, department, position, salary, hire_date, email, phone, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO company_records (employee_name, department, position, salary, hire_date, email, phone, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (employee_name, department, position, salary, hire_date, email, phone, status))
        conn.commit()
        conn.close()
    
    def update_record(self, record_id, employee_name, department, position, salary, hire_date, email, phone, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE company_records 
            SET employee_name=?, department=?, position=?, salary=?, hire_date=?, email=?, phone=?, status=?
            WHERE id=?
        ''', (employee_name, department, position, salary, hire_date, email, phone, status, record_id))
        conn.commit()
        conn.close()
    
    def delete_record(self, record_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM company_records WHERE id=?", (record_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return False
            return True
            
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False
        finally:
            conn.close()
    
    def search_records(self, search_term):
        conn = self.get_connection()
        query = f"""
            SELECT * FROM company_records 
            WHERE employee_name LIKE '%{search_term}%' 
            OR department LIKE '%{search_term}%'
            OR position LIKE '%{search_term}%'
            OR email LIKE '%{search_term}%'
            ORDER BY id DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM company_records")
        total_employees = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT department) FROM company_records")
        total_departments = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(salary) FROM company_records")
        avg_salary = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM company_records WHERE status='Active'")
        active_employees = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_employees': total_employees,
            'total_departments': total_departments,
            'avg_salary': round(avg_salary, 2),
            'active_employees': active_employees
        }

    def init_shipments_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_number TEXT UNIQUE NOT NULL,
                client_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                origin_country TEXT,
                destination_country TEXT,
                departure_date TEXT,
                expected_arrival TEXT,
                actual_arrival TEXT,
                status TEXT DEFAULT 'Pending',
                total_weight REAL,
                total_value REAL,
                currency TEXT DEFAULT 'USD',
                customs_cleared INTEGER DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def init_cargo_items_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cargo_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                unit TEXT DEFAULT 'pcs',
                weight REAL,
                value REAL,
                hs_code TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(shipment_id) REFERENCES shipments(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()

    def init_tracking_updates_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                update_date TEXT NOT NULL,
                created_by INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(shipment_id) REFERENCES shipments(id) ON DELETE CASCADE,
                FOREIGN KEY(created_by) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def init_documents_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shipment_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_by INTEGER,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(shipment_id) REFERENCES shipments(id) ON DELETE CASCADE,
                FOREIGN KEY(uploaded_by) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def init_cargo_requests_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cargo_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cargo_item_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                request_type TEXT NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'Pending',
                employee_response TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(cargo_item_id) REFERENCES cargo_items(id) ON DELETE CASCADE,
                FOREIGN KEY(client_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def create_shipment(self, shipment_number, client_id, shipment_type, origin_country, 
                       destination_country, departure_date, expected_arrival, total_weight, 
                       total_value, currency='USD', notes=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO shipments (shipment_number, client_id, type, origin_country, 
                                     destination_country, departure_date, expected_arrival, 
                                     total_weight, total_value, currency, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (shipment_number, client_id, shipment_type, origin_country, destination_country, 
                  departure_date, expected_arrival, total_weight, total_value, currency, notes))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating shipment: {e}")
            return None
        finally:
            conn.close()

    def get_all_shipments(self):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT s.*, u.email as client_email 
            FROM shipments s 
            LEFT JOIN users u ON s.client_id = u.id 
            ORDER BY s.id DESC
        ''', conn)
        conn.close()
        return df

    def get_shipments_by_client(self, client_id):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM shipments WHERE client_id=? ORDER BY id DESC
        ''', conn, params=(client_id,))
        conn.close()
        return df

    def update_shipment_status(self, shipment_id, status, actual_arrival=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if actual_arrival:
            cursor.execute('''
                UPDATE shipments SET status=?, actual_arrival=?, updated_at=CURRENT_TIMESTAMP 
                WHERE id=?
            ''', (status, actual_arrival, shipment_id))
        else:
            cursor.execute('''
                UPDATE shipments SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
            ''', (status, shipment_id))
        conn.commit()
        conn.close()

    def update_customs_status(self, shipment_id, cleared):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE shipments SET customs_cleared=?, updated_at=CURRENT_TIMESTAMP WHERE id=?
        ''', (1 if cleared else 0, shipment_id))
        conn.commit()
        conn.close()

    def add_cargo_item(self, shipment_id, item_name, description, quantity, unit, weight, value, hs_code=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cargo_items (shipment_id, item_name, description, quantity, unit, weight, value, hs_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (shipment_id, item_name, description, quantity, unit, weight, value, hs_code))
        conn.commit()
        conn.close()

    def get_cargo_items_by_shipment(self, shipment_id):
        conn = self.get_connection()
        df = pd.read_sql_query('SELECT * FROM cargo_items WHERE shipment_id=?', conn, params=(shipment_id,))
        conn.close()
        return df

    def delete_cargo_item(self, item_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cargo_items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()

    def update_cargo_item(self, item_id, item_name, quantity, weight, unit, value, description='', hs_code=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cargo_items 
            SET item_name=?, description=?, quantity=?, unit=?, weight=?, value=?, hs_code=?
            WHERE id=?
        ''', (item_name, description, quantity, unit, weight, value, hs_code, item_id))
        conn.commit()
        conn.close()

    def add_tracking_update(self, shipment_id, location, status, notes, update_date, created_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tracking_updates (shipment_id, location, status, notes, update_date, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (shipment_id, location, status, notes, update_date, created_by))
        conn.commit()
        conn.close()

    def get_tracking_updates(self, shipment_id):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT t.*, u.email as updated_by_email 
            FROM tracking_updates t 
            LEFT JOIN users u ON t.created_by = u.id 
            WHERE t.shipment_id=? 
            ORDER BY t.update_date DESC, t.id DESC
        ''', conn, params=(shipment_id,))
        conn.close()
        return df

    def add_shipment_document(self, shipment_id, document_type, file_path, uploaded_by, notes=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shipment_documents (shipment_id, document_type, file_path, uploaded_by, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (shipment_id, document_type, file_path, uploaded_by, notes))
        conn.commit()
        conn.close()

    def get_shipment_documents(self, shipment_id):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT d.*, u.email as uploaded_by_email 
            FROM shipment_documents d 
            LEFT JOIN users u ON d.uploaded_by = u.id 
            WHERE d.shipment_id=? 
            ORDER BY d.id DESC
        ''', conn, params=(shipment_id,))
        conn.close()
        return df

    def create_cargo_request(self, cargo_item_id, client_id, request_type, reason=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cargo_requests (cargo_item_id, client_id, request_type, reason)
            VALUES (?, ?, ?, ?)
        ''', (cargo_item_id, client_id, request_type, reason))
        conn.commit()
        conn.close()

    def get_cargo_requests_by_client(self, client_id):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT cr.*, ci.item_name, ci.shipment_id, s.shipment_number
            FROM cargo_requests cr
            LEFT JOIN cargo_items ci ON cr.cargo_item_id = ci.id
            LEFT JOIN shipments s ON ci.shipment_id = s.id
            WHERE cr.client_id=?
            ORDER BY cr.id DESC
        ''', conn, params=(client_id,))
        conn.close()
        return df

    def get_all_cargo_requests(self):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT cr.*, ci.item_name, ci.shipment_id, s.shipment_number, u.email as client_email
            FROM cargo_requests cr
            LEFT JOIN cargo_items ci ON cr.cargo_item_id = ci.id
            LEFT JOIN shipments s ON ci.shipment_id = s.id
            LEFT JOIN users u ON cr.client_id = u.id
            ORDER BY cr.id DESC
        ''', conn)
        conn.close()
        return df

    def update_cargo_request_status(self, request_id, status, employee_response=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cargo_requests 
            SET status=?, employee_response=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (status, employee_response, request_id))
        conn.commit()
        conn.close()

    def get_shipment_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM shipments")
        total_shipments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shipments WHERE type='Import'")
        total_imports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shipments WHERE type='Export'")
        total_exports = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shipments WHERE status='In Transit'")
        in_transit = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_value) FROM shipments")
        total_value = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_shipments': total_shipments,
            'total_imports': total_imports,
            'total_exports': total_exports,
            'in_transit': in_transit,
            'total_value': round(total_value, 2)
        }