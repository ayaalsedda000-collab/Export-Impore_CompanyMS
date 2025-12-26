import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import pandas as pd
from datetime import datetime
import streamlit as st
import os
from sqlalchemy import create_engine

class Database:
    _connection_pool = None
    _engine = None
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL", "")
        if not self.db_url:
            st.error("Database URL not configured. Please add DATABASE_URL to secrets.")
            st.stop()
        
        if Database._engine is None:
            Database._engine = create_engine(
                self.db_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600
            )
        
        if Database._connection_pool is None:
            try:
                Database._connection_pool = pool.SimpleConnectionPool(
                    minconn=2,
                    maxconn=10,
                    dsn=self.db_url
                )
            except Exception as e:
                st.error(f"Failed to create connection pool: {e}")
                st.stop()
        
        self.init_database()
    
    def get_connection(self):
        try:
            conn = Database._connection_pool.getconn()
            return conn
        except Exception:
            return psycopg2.connect(self.db_url)
    
    def return_connection(self, conn):
        try:
            Database._connection_pool.putconn(conn)
        except Exception:
            conn.close()
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_records (
                id SERIAL PRIMARY KEY,
                employee_name TEXT NOT NULL,
                department TEXT NOT NULL,
                position TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', sample_data)
        
        conn.commit()
        self.return_connection(conn)

    def init_users_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def create_user(self, email, password_hash, salt, role='user'):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, salt, role)
                VALUES (%s, %s, %s, %s)
            ''', (email, password_hash, salt, role))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def get_user_by_email(self, email):
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('SELECT id, email, password_hash, salt, role, created_at FROM users WHERE email=%s', (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def init_leave_table(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leave_requests (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                reason TEXT,
                leave_type TEXT DEFAULT 'Other',
                attachment TEXT DEFAULT '',
                status TEXT DEFAULT 'Pending',
                admin_response TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def create_leave_request(self, user_id, start_date, end_date, reason, leave_type='Other', attachment=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leave_requests (user_id, start_date, end_date, reason, leave_type, attachment)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, start_date, end_date, reason, leave_type, attachment))
        conn.commit()
        conn.close()

    def get_leave_requests_by_user(self, user_id):
        return pd.read_sql_query(
            'SELECT * FROM leave_requests WHERE user_id=%(user_id)s ORDER BY id DESC',
            Database._engine,
            params={'user_id': user_id}
        )

    def get_all_leave_requests(self):
        return pd.read_sql_query(
            'SELECT lr.id, lr.user_id, u.email as user_email, lr.start_date, lr.end_date, lr.reason, lr.leave_type, lr.attachment, lr.status, lr.admin_response, lr.created_at FROM leave_requests lr JOIN users u ON lr.user_id=u.id ORDER BY lr.id DESC',
            Database._engine
        )

    def update_leave_request_status(self, request_id, status, admin_response=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if admin_response is None:
            cursor.execute('UPDATE leave_requests SET status=%s WHERE id=%s', (status, request_id))
        else:
            cursor.execute('UPDATE leave_requests SET status=%s, admin_response=%s WHERE id=%s', (status, admin_response, request_id))
        conn.commit()
        conn.close()

    def get_all_users(self):
        return pd.read_sql_query(
            'SELECT id, email, role, created_at FROM users ORDER BY id DESC',
            Database._engine
        )

    def update_user_role(self, user_id, role):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET role=%s WHERE id=%s', (role, user_id))
        conn.commit()
        conn.close()
    
    def get_all_records(self):
        return pd.read_sql_query(
            "SELECT * FROM company_records ORDER BY id DESC",
            Database._engine
        )
    
    def add_record(self, employee_name, department, position, salary, hire_date, email, phone, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO company_records (employee_name, department, position, salary, hire_date, email, phone, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (employee_name, department, position, salary, hire_date, email, phone, status))
        conn.commit()
        conn.close()
    
    def update_record(self, record_id, employee_name, department, position, salary, hire_date, email, phone, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE company_records 
            SET employee_name=%s, department=%s, position=%s, salary=%s, hire_date=%s, email=%s, phone=%s, status=%s
            WHERE id=%s
        ''', (employee_name, department, position, salary, hire_date, email, phone, status, record_id))
        conn.commit()
        conn.close()
    
    def delete_record(self, record_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM company_records WHERE id=%s", (record_id,))
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
        query = """
            SELECT * FROM company_records 
            WHERE employee_name ILIKE %(pattern)s 
            OR department ILIKE %(pattern)s
            OR position ILIKE %(pattern)s
            OR email ILIKE %(pattern)s
            ORDER BY id DESC
        """
        search_pattern = f'%{search_term}%'
        return pd.read_sql_query(
            query,
            Database._engine,
            params={'pattern': search_pattern}
        )
    
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
                id SERIAL PRIMARY KEY,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                id SERIAL PRIMARY KEY,
                shipment_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                description TEXT,
                quantity INTEGER NOT NULL,
                unit TEXT DEFAULT 'pcs',
                weight REAL,
                value REAL,
                hs_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                id SERIAL PRIMARY KEY,
                shipment_id INTEGER NOT NULL,
                location TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                update_date TEXT NOT NULL,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                id SERIAL PRIMARY KEY,
                shipment_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_by INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                id SERIAL PRIMARY KEY,
                cargo_item_id INTEGER NOT NULL,
                client_id INTEGER NOT NULL,
                request_type TEXT NOT NULL,
                reason TEXT,
                status TEXT DEFAULT 'Pending',
                employee_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (shipment_number, client_id, shipment_type, origin_country, destination_country, 
                  departure_date, expected_arrival, total_weight, total_value, currency, notes))
            shipment_id = cursor.fetchone()[0]
            conn.commit()
            return shipment_id
        except Exception as e:
            print(f"Error creating shipment: {e}")
            return None
        finally:
            conn.close()

    def get_all_shipments(self):
        return pd.read_sql_query('''
            SELECT s.*, u.email as client_email 
            FROM shipments s 
            LEFT JOIN users u ON s.client_id = u.id 
            ORDER BY s.id DESC
        ''', Database._engine)

    def get_shipments_by_client(self, client_id):
        return pd.read_sql_query('''
            SELECT * FROM shipments WHERE client_id=%(client_id)s ORDER BY id DESC
        ''', Database._engine, params={'client_id': client_id})

    def update_shipment_status(self, shipment_id, status, actual_arrival=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if actual_arrival:
            cursor.execute('''
                UPDATE shipments SET status=%s, actual_arrival=%s, updated_at=CURRENT_TIMESTAMP 
                WHERE id=%s
            ''', (status, actual_arrival, int(shipment_id)))
        else:
            cursor.execute('''
                UPDATE shipments SET status=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s
            ''', (status, int(shipment_id)))
        conn.commit()
        conn.close()

    def update_customs_status(self, shipment_id, cleared):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE shipments SET customs_cleared=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s
        ''', (1 if cleared else 0, int(shipment_id)))
        conn.commit()
        conn.close()

    def add_cargo_item(self, shipment_id, item_name, description, quantity, unit, weight, value, hs_code=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cargo_items (shipment_id, item_name, description, quantity, unit, weight, value, hs_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (shipment_id, item_name, description, quantity, unit, weight, value, hs_code))
        conn.commit()
        conn.close()

    def get_cargo_items_by_shipment(self, shipment_id):
        return pd.read_sql_query(
            'SELECT * FROM cargo_items WHERE shipment_id=%(shipment_id)s',
            Database._engine,
            params={'shipment_id': int(shipment_id)}
        )

    def delete_cargo_item(self, item_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cargo_items WHERE id=%s", (item_id,))
        conn.commit()
        conn.close()

    def update_cargo_item(self, item_id, item_name, quantity, weight, unit, value, description='', hs_code=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cargo_items 
            SET item_name=%s, description=%s, quantity=%s, unit=%s, weight=%s, value=%s, hs_code=%s
            WHERE id=%s
        ''', (item_name, description, quantity, unit, weight, value, hs_code, item_id))
        conn.commit()
        conn.close()

    def add_tracking_update(self, shipment_id, location, status, notes, update_date, created_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tracking_updates (shipment_id, location, status, notes, update_date, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (shipment_id, location, status, notes, update_date, created_by))
        conn.commit()
        conn.close()

    def get_tracking_updates(self, shipment_id):
        return pd.read_sql_query('''
            SELECT t.*, u.email as updated_by_email 
            FROM tracking_updates t 
            LEFT JOIN users u ON t.created_by = u.id 
            WHERE t.shipment_id=%(shipment_id)s 
            ORDER BY t.update_date DESC, t.id DESC
        ''', Database._engine, params={'shipment_id': int(shipment_id)})

    def add_shipment_document(self, shipment_id, document_type, file_path, uploaded_by, notes=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shipment_documents (shipment_id, document_type, file_path, uploaded_by, notes)
            VALUES (%s, %s, %s, %s, %s)
        ''', (shipment_id, document_type, file_path, uploaded_by, notes))
        conn.commit()
        conn.close()

    def get_shipment_documents(self, shipment_id):
        return pd.read_sql_query('''
            SELECT d.*, u.email as uploaded_by_email 
            FROM shipment_documents d 
            LEFT JOIN users u ON d.uploaded_by = u.id 
            WHERE d.shipment_id=%(shipment_id)s 
            ORDER BY d.id DESC
        ''', Database._engine, params={'shipment_id': int(shipment_id)})

    def create_cargo_request(self, cargo_item_id, client_id, request_type, reason=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cargo_requests (cargo_item_id, client_id, request_type, reason)
            VALUES (%s, %s, %s, %s)
        ''', (cargo_item_id, client_id, request_type, reason))
        conn.commit()
        conn.close()

    def get_cargo_requests_by_client(self, client_id):
        return pd.read_sql_query('''
            SELECT cr.*, ci.item_name, ci.shipment_id, s.shipment_number
            FROM cargo_requests cr
            LEFT JOIN cargo_items ci ON cr.cargo_item_id = ci.id
            LEFT JOIN shipments s ON ci.shipment_id = s.id
            WHERE cr.client_id=%(client_id)s
            ORDER BY cr.id DESC
        ''', Database._engine, params={'client_id': client_id})

    def get_all_cargo_requests(self):
        return pd.read_sql_query('''
            SELECT cr.*, ci.item_name, ci.shipment_id, s.shipment_number, u.email as client_email
            FROM cargo_requests cr
            LEFT JOIN cargo_items ci ON cr.cargo_item_id = ci.id
            LEFT JOIN shipments s ON ci.shipment_id = s.id
            LEFT JOIN users u ON cr.client_id = u.id
            ORDER BY cr.id DESC
        ''', Database._engine)

    def update_cargo_request_status(self, request_id, status, employee_response=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cargo_requests 
            SET status=%s, employee_response=%s, updated_at=CURRENT_TIMESTAMP
            WHERE id=%s
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
