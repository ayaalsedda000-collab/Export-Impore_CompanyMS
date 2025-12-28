import streamlit as st
import pandas as pd
import hashlib
import secrets
import time
import importlib
from datetime import datetime, date
from database_postgres import Database
from data_manager import DataManager
import os
from PIL import Image
from functools import lru_cache

# Configure page with performance optimizations
st.set_page_config(
    page_title="EIMS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Language translations dictionary
TRANSLATIONS = {
    'en': {
        'title': 'EIMS',
        'login': '🔐 Login',
        'signup': '📝 Sign Up',
        'dashboard': '🏠 Dashboard',
        'view': '📋 View Data',
        'add': '➕ Add Data',
        'edit': '✏️ Edit Data',
        'delete': '🗑️ Delete Data',
        'analytics': '📊 Analytics & Charts',
        'export': '📥 Export Data',
        'request_leave': '📝 Request Leave',
        'manage_leaves': '🔧 Manage Leave Requests',
        'manage_users': '👥 Manage Users',
        'logout': '🚪 Logout',
        'select_page': 'Select Page:',
        'project_info': 'Information',
        'graduation_project': 'Software Engineering\nCompany Data Management System',
        'email': 'Email',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'role': 'Role',
        'create_account': 'Create Account',
        'login_button': 'Login',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'leave_type': 'Leave Type',
        'reason': 'Reason for leave',
        'attachment': 'Optional attachment (medical note, etc.)',
        'submit': 'Submit Request',
        'my_requests': 'My Leave Requests',
        'from': 'From',
        'to': 'To',
        'type': 'Type',
        'manager_response': 'Manager response',
        'status': 'Status',
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'language': '🌐 Language',
        'no_requests': 'You have no leave requests.',
        'set_status': 'Set status:',
        'response_user': 'Response to user:',
        'save': 'Save',
        'user': 'User',
        'employee': 'Employee',
        'client': 'Client',
        'manager': 'Manager',
        'shipments': '📊 Shipments',
        'add_shipment': '➕ Add Shipment',
        'my_shipments': '📦 My Shipments',
        'track_shipment': '🗺️ Track Shipment',
        'manage_shipments': '📋 Manage Shipments',
        'shipment_analytics': '📊 Shipment Analytics',
        'import': 'Import',
        'export': 'Export',
        'shipment_number': 'Shipment Number',
        'origin': 'Origin Country',
        'destination': 'Destination Country',
        'departure_date': 'Departure Date',
        'expected_arrival': 'Expected Arrival',
        'actual_arrival': 'Actual Arrival',
        'shipment_status': 'Shipment Status',
        'cargo_items': 'Cargo Items',
        'add_cargo': 'Add Cargo Item',
        'tracking': 'Tracking',
        'documents': 'Documents',
        'total_weight': 'Total Weight (kg)',
        'total_value': 'Total Value',
        'customs_cleared': 'Customs Cleared',
        'in_transit': 'In Transit',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled',
        'item_name': 'Item Name',
        'quantity': 'Quantity',
        'weight': 'Weight (kg)',
        'value': 'Value',
        'description': 'Description',
        'location': 'Location',
        'update_tracking': 'Update Tracking',
        'upload_document': 'Upload Document',
        'cargo_requests': '📝 Cargo Requests',
        'request_cargo_change': 'Request Cargo Change',
        'manage_cargo_requests': 'Manage Cargo Requests',
        'request_type': 'Request Type',
        'modify': 'Modify',
        'remove': 'Remove',
        'request_reason': 'Reason for Request',
        'my_cargo_requests': 'My Cargo Requests',
        'approve': 'Approve',
        'reject': 'Reject',
        'request_status': 'Request Status',
        'client_name': 'Client Name',
        'edit_shipment': '✏️ Edit Shipment',
        'delete_shipment': '🗑️ Delete Shipment',
        'messages': '💬 Messages',
        'send_message': 'Send Message',
        'message_subject': 'Subject',
        'message_content': 'Message',
        'to': 'To',
        'from': 'From',
        'date': 'Date',
        'reply': 'Reply',
    },
    'tr': {
        'title': 'EIMS',
        'login': '🔐 Giriş Yap',
        'signup': '📝 Kaydol',
        'dashboard': '🏠 Gösterge Paneli',
        'view': '📋 Verileri Görüntüle',
        'add': '➕ Veri Ekle',
        'edit': '✏️ Verileri Düzenle',
        'delete': '🗑️ Verileri Sil',
        'analytics': '📊 Analitikler ve Grafikler',
        'export': '📥 Verileri Dışa Aktar',
        'request_leave': '📝 İzin Talep Et',
        'manage_leaves': '🔧 İzin Taleplerini Yönet',
        'manage_users': '👥 Kullanıcıları Yönet',
        'logout': '🚪 Çıkış Yap',
        'select_page': 'Sayfa Seç:',
        'project_info': 'Proje Bilgileri',
        'graduation_project': 'Mezuniyet Projesi - Yazılım Mühendisliği\nŞirket Veri Yönetim Sistemi',
        'email': 'E-posta',
        'password': 'Şifre',
        'confirm_password': 'Şifreyi Onayla',
        'role': 'Rol',
        'create_account': 'Hesap Oluştur',
        'login_button': 'Giriş Yap',
        'start_date': 'Başlama Tarihi',
        'end_date': 'Bitiş Tarihi',
        'leave_type': 'İzin Türü',
        'reason': 'İzin Nedeni',
        'attachment': 'İsteğe Bağlı Ek (tıbbi not, vb.)',
        'submit': 'Talebi Gönder',
        'my_requests': 'Benim İzin Taleplerimin',
        'from': 'Başlama',
        'to': 'Bitiş',
        'type': 'Tür',
        'manager_response': 'Yönetici Yanıtı',
        'status': 'Durum',
        'pending': 'Beklemede',
        'approved': 'Onaylandı',
        'rejected': 'Reddedildi',
        'language': '🌐 Dil',
        'no_requests': 'İzin talebiniz yok.',
        'set_status': 'Durumu Ayarla:',
        'response_user': 'Kullanıcıya Yanıt:',
        'save': 'Kaydet',
        'user': 'Kullanıcı',
        'employee': 'Çalışan',
        'client': 'Müşteri',
        'admin': 'Yönetici',
        'shipments': '🚢 Gönderiler',
        'add_shipment': '➕ Gönderi Ekle',
        'my_shipments': '📦 Gönderilerim',
        'track_shipment': '🗺️ Gönderi Takibi',
        'manage_shipments': '📋 Gönderileri Yönet',
        'shipment_analytics': '📊 Gönderi Analizleri',
        'import': 'İthalat',
        'export': 'İhracat',
        'shipment_number': 'Gönderi Numarası',
        'origin': 'Çıkış Ülkesi',
        'destination': 'Varış Ülkesi',
        'departure_date': 'Kalkış Tarihi',
        'expected_arrival': 'Beklenen Varış',
        'actual_arrival': 'Gerçek Varış',
        'shipment_status': 'Gönderi Durumu',
        'cargo_items': 'Kargo Kalemleri',
        'add_cargo': 'Kargo Kalemi Ekle',
        'tracking': 'Takip',
        'documents': 'Belgeler',
        'total_weight': 'Toplam Ağırlık (kg)',
        'total_value': 'Toplam Değer',
        'customs_cleared': 'Gümrük Geçişi',
        'in_transit': 'Yolda',
        'delivered': 'Teslim Edildi',
        'cancelled': 'İptal Edildi',
        'item_name': 'Ürün Adı',
        'quantity': 'Miktar',
        'weight': 'Ağırlık (kg)',
        'value': 'Değer',
        'description': 'Açıklama',
        'location': 'Konum',
        'update_tracking': 'Takip Güncelle',
        'upload_document': 'Belge Yükle',
        'cargo_requests': '📝 Kargo Talepleri',
        'request_cargo_change': 'Kargo Değişikliği Talep Et',
        'manage_cargo_requests': 'Kargo Taleplerini Yönet',
        'request_type': 'Talep Türü',
        'modify': 'Düzenle',
        'remove': 'Kaldır',
        'request_reason': 'Talep Nedeni',
        'my_cargo_requests': 'Kargo Taleplerim',
        'approve': 'Onayla',
        'reject': 'Reddet',
        'request_status': 'Talep Durumu',
        'client_name': 'Müşteri Adı',
        'edit_shipment': '✏️ Gönderiyi Düzenle',
        'delete_shipment': '🗑️ Gönderiyi Sil',
    }
}

# Configure page icon
logo_icon = "assets/logo.png"
if os.path.exists(logo_icon):
    page_icon = Image.open(logo_icon)
else:
    page_icon = ""

st.set_page_config(
    page_title="EIMS",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove caching to ensure fresh data
def init_database():
    return Database()

def init_data_manager():
    return DataManager()

db = init_database()
data_manager = init_data_manager()

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'
# Initialize theme in session state ('light' or 'dark')
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

def t(key: str) -> str:
    """Get translation for a key in the current language."""
    lang = st.session_state.get('language', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def apply_theme():
    """Inject CSS for light or dark theme based on session state."""
    theme = st.session_state.get('theme', 'light')
    if theme == 'dark':
        css = """
        <style>
        /* page background */
        .stApp, .reportview-container, .main, body { background-color: #0b1220; color: #e6eef8; }
        /* cards and panels */
        .card { background: #0f1724 !important; border-color: #1f2937 !important; color: #e6eef8 !important; }
        .metric-card { background-color: #0f1724 !important; color: #e6eef8 !important; }
        .stMarkdown, .stText, .stHeader, h1, h2, h3, h4, h5 { color: #e6eef8 !important; }
        .stButton>button { background-color:#111827; color:#e6eef8; }
        .status-badge { color: #fff; }
        </style>
        """
    else:
        css = """
        <style>
        .stApp, .reportview-container, .main, body { background-color: #ffffff; color: #111827; }
        .card { background: #ffffff !important; border-color: #e6e9ef !important; color: #111827 !important; }
        .metric-card { background-color: #f0f2f6 !important; color: #111827 !important; }
        .stButton>button { background-color: #f3f4f6; color: #111827; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

def page_matches(page_label: str, page_key: str) -> bool:
    """Check if a page label matches a page key in any language."""
    return page_label in [TRANSLATIONS['en'].get(page_key, ''), TRANSLATIONS['tr'].get(page_key, '')]

def get_page_key(page_label: str) -> str:
    """Get the key for a page label by checking all translations."""
    for key in ['login', 'signup', 'dashboard', 'view', 'add', 'edit', 'delete', 
                'analytics', 'export', 'request_leave', 'manage_leaves', 'manage_users',
                'cargo_requests', 'manage_cargo_requests']:
        if page_label in [TRANSLATIONS['en'].get(key, ''), TRANSLATIONS['tr'].get(key, '')]:
            return key
    return ''

# ensure users table exists (safe to call repeatedly)
try:
    db.init_users_table()
except Exception:
    pass

# ensure leave_requests table exists
try:
    db.init_leave_table()
except Exception:
    pass

# Initialize shipment-related tables
try:
    db.init_shipments_table()
    db.init_cargo_items_table()
    db.init_tracking_updates_table()
    db.init_documents_table()
    db.init_cargo_requests_table()
    db.init_messages_table()
except Exception as e:
    print(f"Error initializing shipment tables: {e}")

def _generate_salt():
    return secrets.token_hex(16)

def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

# Cache database queries for better performance with longer TTL
@st.cache_data(ttl=300, show_spinner=False, max_entries=20)
def get_cached_records():
    """Cache employee records for 5 minutes"""
    return db.get_all_records()

@st.cache_data(ttl=300, show_spinner=False, max_entries=20)
def get_cached_shipments():
    """Cache shipments for 5 minutes"""
    try:
        return db.get_all_shipments()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600, show_spinner=False, max_entries=10)
def get_cached_users():
    """Cache users for 10 minutes"""
    try:
        return db.get_all_users()
    except:
        return []

@st.cache_resource(show_spinner=False)
def get_db_connection():
    """Cache database connection"""
    return Database()

# Ensure specific manager email exists and has manager role
try:
    _admin_email = 'aya@gmail.com'
    existing = db.get_user_by_email(_admin_email)
    if existing:
        if existing.get('role') != 'manager':
            db.update_user_role(existing['id'], 'manager')
            print(f"Promoted {_admin_email} to manager")
    else:
        # create manager user with a generated password and save credentials to a file
        gen_salt = _generate_salt()
        gen_password = secrets.token_urlsafe(10)
        gen_hash = _hash_password(gen_password, gen_salt)
        created = db.create_user(_admin_email, gen_hash, gen_salt, role='manager')
        if created:
            cred_path = 'manager_credentials.txt'
            try:
                with open(cred_path, 'w', encoding='utf-8') as f:
                    f.write(f'email: {_admin_email}\npassword: {gen_password}\n')
                print(f"Created manager {_admin_email} and wrote credentials to {cred_path}")
            except Exception as e:
                print(f"Created manager {_admin_email} but failed to write credentials: {e}")
except Exception as _e:
    print(f"Error ensuring manager user: {_e}")

def _safe_rerun():
    """Rerun the Streamlit script in a way compatible with multiple Streamlit versions."""
    # Clear cache before rerun for fresh data
    try:
        get_cached_records.clear()
        get_cached_shipments.clear()
        get_cached_users.clear()
    except:
        pass
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.query_params = {"_rerun": int(time.time())}
        st.stop()

PAGES = {
    'login': '🔐 Login',
    'signup': '📝 Sign Up',
    'dashboard': '🏠 Dashboard',
    'view': '📋 View Data',
    'add': '➕ Add Data',
    'edit': '✏️ Edit Data',
    'delete': '🗑️ Delete Data',
    'analytics': '📊 Analytics & Charts',
    'export': '📥 Export Data',
    'request_leave': '📝 Request Leave',
    'manage_leaves': '🔧 Manage Requests',
    'manage_users': '👥 Manage employee'
}

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .card {
        background: #262730;
        border: 1px solid #262730;
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(16,24,40,0.04);
        margin-bottom: 12px;
        color: #e6eef8;
    }
    .status-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-weight: 600; color: #fff; font-size: 12px; }
    .status-pending { background: #f39c12; }
    .status-approved { background: #28a745; }
    .status-rejected { background: #dc3545; }
    .request-row { padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
    </style>
""", unsafe_allow_html=True)

# Display title
st.title("📊 EIMS")
st.markdown("---")

with st.sidebar:
    # Display logo in sidebar
    logo_png = "assets/logo.png"
    logo_svg = "assets/logo.svg"
    if os.path.exists(logo_png):
        st.image(logo_png, width=80, output_format="PNG")
    elif os.path.exists(logo_svg):
        with open(logo_svg, "r", encoding="utf-8") as f:
            st.markdown(f'''<div style="text-align: center; margin: 10px 0; transform: scale(0.8);">{f.read()}</div>''', unsafe_allow_html=True)
    else:
        st.header("EIMS")
    # build options depending on auth/role (exact mapping requested)
    # Generate page labels dynamically based on current language
    guest_pages = [t('login'), t('signup')]
    # employees can manage shipments and cargo
    employee_pages = [
        t('manage_shipments'), t('add_shipment'), t('edit_shipment'), t('delete_shipment'),
        t('track_shipment'), t('shipment_analytics'), t('manage_cargo_requests'), t('request_leave'), t('messages')
    ]
    # clients can only view and track their own shipments
    client_pages = [t('my_shipments'), t('track_shipment'), t('cargo_requests'), t('messages')]
    admin_pages = [
        t('dashboard'), t('view'), t('add'), t('edit'), t('delete'),
        t('analytics'), t('manage_leaves'), t('manage_users'),
        t('shipment_analytics')
    ]

    page_options = guest_pages
    try:
        if 'user' in st.session_state and st.session_state['user']:
            role = st.session_state['user'].get('role', 'employee')
            if role == 'manager':
                page_options = admin_pages
            elif role == 'employee':
                page_options = employee_pages
            elif role == 'client':
                page_options = client_pages
            else:
                page_options = employee_pages
    except Exception:
        page_options = guest_pages

    # default to first option unless query param 'page' requests a different one
    default_index = 0
    try:
        qp = st.query_params
        if qp and 'page' in qp:
            requested = qp['page'][0] if isinstance(qp['page'], (list, tuple)) and qp['page'] else qp['page']
            # Try to match requested page key/label to one in page_options
            target_label = None
            # Try as a key first
            if requested == 'login':
                target_label = t('login')
            elif requested == 'signup':
                target_label = t('signup')
            elif requested == 'dashboard':
                target_label = t('dashboard')
            elif requested == 'request_leave':
                target_label = t('request_leave')
            elif requested == 'manage_leaves':
                target_label = t('manage_leaves')
            elif requested == 'manage_users':
                target_label = t('manage_users')
            elif requested == 'manage_shipments':
                target_label = t('manage_shipments')
            elif requested == 'add_shipment':
                target_label = t('add_shipment')
            elif requested == 'my_shipments':
                target_label = t('my_shipments')
            elif requested == 'track_shipment':
                target_label = t('track_shipment')
            elif requested == 'cargo_requests':
                target_label = t('cargo_requests')
            elif requested == 'manage_cargo_requests':
                target_label = t('manage_cargo_requests')
            # Otherwise try as a direct label
            elif requested in page_options:
                target_label = requested

            if target_label and target_label in page_options:
                default_index = page_options.index(target_label)
    except Exception:
        # if any issue reading query params, just fall back to default
        default_index = 0

    page = st.radio(
        t('select_page'),
        page_options,
        index=default_index,
        label_visibility="collapsed"
    )
    
    # Fix page to match current language if it was from a previous language
    page_key = get_page_key(page)
    if page_key:
        page = t(page_key)
    
    st.markdown("---")
    
    # Language toggle button
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        if st.button("🇺🇸 English" if st.session_state['language'] == 'tr' else "US English", width='stretch'):
            st.session_state['language'] = 'en'
    with col_lang2:
        if st.button("🇹🇷 Türkçe" if st.session_state['language'] == 'en' else "🇹🇷 Türkçe", width='stretch'):
            st.session_state['language'] = 'tr'
    
    st.markdown("---")
    
    # Logout button for logged-in users
    if 'user' in st.session_state and st.session_state['user']:
        if st.button(t('logout'), width='stretch'):
            st.session_state['user'] = None
            st.query_params = {"page": "login"}
            _safe_rerun()
    
    st.markdown("---")
    st.markdown(f"### {t('project_info')}")
    st.info(t('graduation_project'))

### Authentication handling: Login / Sign Up pages and access control ###
if page_matches(page, 'login'):
    st.header(t('login'))
    with st.form("login_form"):
        email = st.text_input(t('email'), placeholder="name@role.com")
        password = st.text_input(t('password'), type="password")
        submitted = st.form_submit_button(t('login_button'))
        if submitted:
            if not email or not password:
                st.error("Please provide email and password")
            else:
                user = db.get_user_by_email(email)
                if not user:
                    st.error("No account found with that email. Please sign up.")
                else:
                    hash_val = _hash_password(password, user['salt'])
                    if hash_val == user['password_hash']:
                        # include role so UI can branch by permissions
                        user_role = user.get('role', 'employee')
                        st.session_state['user'] = {'id': user['id'], 'email': user['email'], 'role': user_role}
                        # redirect based on role
                        try:
                            if user_role == 'manager':
                                st.query_params = {"page": "dashboard"}
                            elif user_role == 'employee':
                                st.query_params = {"page": "manage_shipments"}
                            elif user_role == 'client':
                                st.query_params = {"page": "my_shipments"}
                            else:
                                st.query_params = {"page": "request_leave"}
                        except Exception:
                            pass
                        _safe_rerun()
                    else:
                        st.error("Incorrect password")

elif page_matches(page, 'signup'):
    # Check if user has selected account type
    if 'signup_type' not in st.session_state:
        # Show account type selection page
        st.markdown("<h1 style='text-align: center; color: #1E88E5; margin-bottom: 10px;'>🎯 Create New Account</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; font-size: 18px; margin-bottom: 40px;'>Choose the type of account you want to register</p>", unsafe_allow_html=True)
        
        # Add spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_space1, col_main, col_space2 = st.columns([0.8, 2.4, 0.8])
        
        with col_main:
            col_btn1, col_space, col_btn2 = st.columns([1, 0.15, 1])
            
            with col_btn1:
                # Employee button as large card
                employee_clicked = st.button(
                    label="👨‍💼\n\nEmployee Account",
                    key="btn_employee",
                    use_container_width=True,
                    help="Register as an employee with complete access"
                )
                if employee_clicked:
                    st.session_state['signup_type'] = 'employee'
                    st.rerun()
                
                # Custom CSS for employee button - square and larger
                st.markdown("""
                    <style>
                    button[kind="secondary"]:has(div:first-child:contains("👨‍💼")) {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                        border: none !important;
                        padding: 80px 50px !important;
                        min-height: 420px !important;
                        aspect-ratio: 1 / 1 !important;
                        border-radius: 25px !important;
                        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.5) !important;
                        transition: all 0.3s ease !important;
                        color: white !important;
                        font-size: 36px !important;
                        font-weight: bold !important;
                        line-height: 1.8 !important;
                    }
                    button[kind="secondary"]:has(div:first-child:contains("👨‍💼")):hover {
                        transform: translateY(-10px) scale(1.02) !important;
                        box-shadow: 0 18px 50px rgba(102, 126, 234, 0.8) !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
            
            with col_btn2:
                # Client button as large card
                client_clicked = st.button(
                    label="👤\n\nClient Account",
                    key="btn_client",
                    use_container_width=True,
                    help="Register as a client with basic access"
                )
                if client_clicked:
                    st.session_state['signup_type'] = 'client'
                    st.rerun()
                
                # Custom CSS for client button - square and larger
                st.markdown("""
                    <style>
                    button[kind="secondary"]:has(div:first-child:contains("👤")) {
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
                        border: none !important;
                        padding: 80px 50px !important;
                        min-height: 420px !important;
                        aspect-ratio: 1 / 1 !important;
                        border-radius: 25px !important;
                        box-shadow: 0 12px 30px rgba(240, 147, 251, 0.5) !important;
                        transition: all 0.3s ease !important;
                        color: white !important;
                        font-size: 36px !important;
                        font-weight: bold !important;
                        line-height: 1.8 !important;
                    }
                    button[kind="secondary"]:has(div:first-child:contains("👤")):hover {
                        transform: translateY(-10px) scale(1.02) !important;
                        box-shadow: 0 18px 50px rgba(240, 147, 251, 0.8) !important;
                    }
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
                        border: none !important;
                        padding: 60px 40px !important;
                        min-height: 350px !important;
                        border-radius: 20px !important;
                        box-shadow: 0 10px 25px rgba(240, 147, 251, 0.5) !important;
                        transition: all 0.3s ease !important;
                        color: white !important;
                        font-size: 32px !important;
                        font-weight: bold !important;
                        line-height: 1.8 !important;
                    }
                    button[kind="secondary"]:has(div:first-child:contains("👤")):hover {
                        transform: translateY(-8px) !important;
                        box-shadow: 0 15px 40px rgba(240, 147, 251, 0.7) !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        
        col_back1, col_back2, col_back3 = st.columns([1, 1, 1])
        with col_back2:
            if st.button("← Back to Login", use_container_width=True, key="back_to_login"):
                st.query_params = {"page": "login"}
                st.rerun()
    
    else:
        # Show registration form based on selected type
        role_choice = st.session_state['signup_type']
        
        # Back button on top left
        if st.button("⬅ Change", key="change_type", help="Change account type"):
            del st.session_state['signup_type']
            st.rerun()
        
        # Centered title
        icon = "👨‍💼" if role_choice == "employee" else "👤"
        account_type = "Employee" if role_choice == "employee" else "Client"
        st.markdown(f"<h2 style='text-align: center; color: #1E88E5; margin-top: 20px;'>{icon} {account_type} Registration</h2>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.form("signup_form"):
            st.markdown("#### 📝 Account Information")
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("📧 Email Address *", placeholder=f"name@{role_choice}.com", help=f"Must end with @{role_choice}.com")
                password = st.text_input("🔒 Password *", type="password", help="Create a strong password")
            
            with col2:
                confirm = st.text_input("🔑 Confirm Password *", type="password", help="Re-enter your password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 👤 Personal Information")
            
            col3, col4 = st.columns(2)
            
            with col3:
                employee_name = st.text_input("📛 Full Name *", placeholder="Enter your full name")
                phone = st.text_input("📱 Phone Number", placeholder="05xxxxxxxx")
                
            with col4:
                # Simplified form for clients
                if role_choice == "client":
                    hire_date = st.date_input("📅 Registration Date *", value=date.today())
                    status = st.selectbox("📊 Status *", ["Active", "Inactive", "On Leave"], index=0)
                    # Set employee-specific fields to None
                    department = None
                    position = None
                    salary = None
                else:
                    # Full form for employees
                    department = st.selectbox("🏢 Department *", ["IT", "HR", "Sales", "Marketing", "Finance", "Administration", "Customer Service", "Logistics"])
                    position = st.text_input("💼 Position *", placeholder="e.g., Software Engineer")
            
            # Show additional employee fields only if not client
            if role_choice == "employee":
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### 💼 Employment Details")
                col5, col6 = st.columns(2)
                with col5:
                    hire_date = st.date_input("📅 Hire Date *", value=date.today())
                with col6:
                    status = st.selectbox("📊 Employment Status *", ["Active", "Inactive", "On Leave"], index=0)
                
                # Salary is auto-set to 0 for new employees - manager can edit later
                salary = 0.0
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button(f"✅ Create {account_type} Account", use_container_width=True, type="primary")
            
            if submitted:
                if not email or not password:
                    st.error("⚠️ Please provide email and password")
                elif password != confirm:
                    st.error("⚠️ Passwords do not match")
                elif role_choice == "employee" and (not employee_name or not department or not position):
                    st.error("⚠️ Please fill all required fields (*)")
                elif role_choice == "client" and not employee_name:
                    st.error("⚠️ Please enter your full name")
                elif not email.endswith(f"@{role_choice}.com"):
                    st.error(f"❌ Email must be in format: name@{role_choice}.com")
                else:
                    existing = db.get_user_by_email(email)
                    if existing:
                        st.error("An account with this email already exists. ")
                    else:
                        try:
                            salt = _generate_salt()
                            password_hash = _hash_password(password, salt)
                            # Create user account in users table
                            ok = db.create_user(email, password_hash, salt, role=role_choice)
                            if ok:
                                # Add employee record to company_records with password
                                db.add_record(
                                    employee_name=employee_name,
                                    department=department,  # None for clients
                                    position=position,      # None for clients
                                    salary=salary,          # None for clients
                                    hire_date=str(hire_date),
                                    email=email,
                                    phone=phone if phone else "",
                                    status=status,
                                    password=password
                                )
                                user = db.get_user_by_email(email)
                                st.session_state['user'] = {'id': user['id'], 'email': user['email'], 'role': user.get('role', 'employee')}
                                # Clear signup type from session
                                if 'signup_type' in st.session_state:
                                    del st.session_state['signup_type']
                                _safe_rerun()
                            else:
                                st.error("Failed to create account. Try again.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

else:
    # For all other pages require login
    if 'user' not in st.session_state or not st.session_state['user']:
        st.warning("Please log in to access these pages.")
        if st.button("Go to Login"):
                st.query_params = {"page": "login"}
                _safe_rerun()
        st.stop()

if page == "🏠 Dashboard":
    st.header("Main Dashboard")
    
    # Use cached data for statistics
    df = get_cached_records()
    if not df.empty:
        stats = {
            'total_employees': len(df),
            'total_departments': df['department'].nunique(),
            'avg_salary': df['salary'].mean(),
            'active_employees': len(df[df['status'] == 'Active'])
        }
    else:
        stats = {'total_employees': 0, 'total_departments': 0, 'avg_salary': 0, 'active_employees': 0}
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Employees",
            value=stats['total_employees'],
            delta="employees"
        )
    
    with col2:
        st.metric(
            label="Departments",
            value=stats['total_departments'],
            delta="departments"
        )
    
    with col3:
        st.metric(
            label="Average Salary",
            value=f"{stats['avg_salary']:,.0f} $",
            delta="$"
        )
    
    with col4:
        st.metric(
            label="Active Employees",
            value=stats['active_employees'],
            delta="active"
        )
    
    st.markdown("---")
    
    st.subheader("Recent Records")
    df = get_cached_records()
    if not df.empty:
        st.dataframe(df.head(5), width='stretch')
    else:
        st.info("No data available")

elif page == "📋 View Data":
    st.header("View All Data")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search Data", placeholder="Search by name, department, position...")
    with col2:
        if st.button("🔑 Generate Passwords", type="primary", help="Generate passwords for employees who don't have one"):
            try:
                credentials = db.generate_employee_passwords()
                if credentials:
                    st.success(f"✅ Generated {len(credentials)} passwords!")
                    _safe_rerun()
                else:
                    st.info("All employees already have passwords!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if search_term:
        df = db.search_records(search_term)
        st.info(f"Found {len(df)} results")
    else:
        df = get_cached_records()
    
    if not df.empty:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            departments = ['All'] + list(df['department'].dropna().unique())
            selected_dept = st.selectbox("Filter by Department:", departments)
        
        with col_f2:
            statuses = ['All'] + list(df['status'].unique())
            selected_status = st.selectbox("Filter by Status:", statuses)
        
        with col_f3:
            # Add role filter
            if 'role' in df.columns:
                roles = ['All'] + [r for r in df['role'].unique() if pd.notna(r)]
                selected_role = st.selectbox("Filter by Role:", roles)
            else:
                selected_role = 'All'
        
        if selected_dept != 'All':
            df = df[df['department'] == selected_dept]
        
        if selected_status != 'All':
            df = df[df['status'] == selected_status]
        
        if selected_role != 'All' and 'role' in df.columns:
            df = df[df['role'] == selected_role]
        
        # Display different columns based on role filter
        if selected_role == 'client':
            # For clients, show only: id, name, email, phone, status, hire_date, password, created_at
            client_cols = ['id', 'employee_name', 'email', 'phone', 'status', 'hire_date']
            if 'password' in df.columns:
                client_cols.insert(3, 'password')
            if 'role' in df.columns:
                client_cols.insert(3, 'role')
            if 'created_at' in df.columns:
                client_cols.append('created_at')
            
            # Filter only existing columns
            display_cols = [col for col in client_cols if col in df.columns]
            df_display = df[display_cols]
        else:
            df_display = df
        
        # Use column_config for better performance
        st.dataframe(
            df_display, 
            use_container_width=True, 
            height=400,
            hide_index=True
        )
    else:
        st.warning("No data to display")

elif page == "➕ Add Data":
    st.header("Add New Record")
    
    # User account settings OUTSIDE form to allow dynamic updates
    st.subheader("Account Settings")
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        create_account = st.checkbox("Create login account for this employee", value=True)
    with col_acc2:
        if create_account:
            account_role = st.selectbox("Account Role", ["employee", "client", "manager"], index=0)
            auto_password = st.checkbox("Auto-generate password", value=True)
            if not auto_password:
                user_password = st.text_input("Password", type="password", placeholder="Enter password")
        else:
            account_role = "employee"
            auto_password = True
    
    st.markdown("---")
    
    # Check if adding a client
    is_client = create_account and account_role == "client"
    
    # Now the form with dynamic content
    with st.form("add_form"):
        st.subheader("Personal Information")
        
        if is_client:
            # Simplified form for clients (no department, position, salary)
            col1, col2 = st.columns(2)
            
            with col1:
                employee_name = st.text_input("Client Name *", placeholder="Enter full name")
                email = st.text_input("Email *", placeholder="client@client.com")
                hire_date = st.date_input("Registration Date *", value=date.today())
            
            with col2:
                phone = st.text_input("Phone", placeholder="05xxxxxxxx")
                status = st.selectbox("Status *", ["Active", "Inactive", "On Leave"])
            
            # Set employee fields to None for clients
            department = None
            position = None
            salary = None
        else:
            # Full form for employees
            col1, col2 = st.columns(2)
            
            with col1:
                employee_name = st.text_input("Employee Name *", placeholder="Enter full name")
                department = st.selectbox("Department *", ["IT", "HR", "Sales", "Marketing", "Finance", "Administration", "Customer Service", "Logistics"])
                position = st.text_input("Position *", placeholder="Enter job title")
                salary = st.number_input("Salary ($) *", min_value=0.0, step=100.0, format="%.2f")
            
            with col2:
                hire_date = st.date_input("Hire Date *", value=date.today())
                email = st.text_input("Email *", placeholder="example@company.com")
                phone = st.text_input("Phone", placeholder="05xxxxxxxx")
                status = st.selectbox("Status *", ["Active", "Inactive", "On Leave"], index=0)
        
        submitted = st.form_submit_button("➕ Add Record", width='stretch')
        
        if submitted:
            # Validate based on role
            if is_client:
                # For clients, only name and email are required
                if not employee_name or not email:
                    st.error("⚠️ Please fill all required fields (*)")
                elif not email.endswith("@client.com"):
                    st.error("❌ Email must be in format: name@client.com")
                else:
                    proceed_with_add = True
            else:
                # For employees, all fields are required
                if not employee_name or not department or not position or salary <= 0 or not email:
                    st.error("⚠️ Please fill all required fields (*)")
                elif create_account and not email.endswith(f"@{account_role}.com"):
                    st.error(f"❌ Email must be in format: name@{account_role}.com")
                else:
                    proceed_with_add = True
            
            if 'proceed_with_add' in locals() and proceed_with_add:
                    try:
                        # Set password to '123' for employee record
                        employee_password = '123'
                        
                        # Add record to company_records
                        db.add_record(
                            employee_name=employee_name,
                            department=department,  # None for clients
                            position=position,      # None for clients
                            salary=salary,          # None for clients
                            hire_date=str(hire_date),
                            email=email,
                            phone=phone,
                            status=status,
                            password=employee_password
                        )
                        
                        # Create user account if requested
                        if create_account:
                            # Check if user already exists
                            existing_user = db.get_user_by_email(email)
                            if not existing_user:
                                # Generate or use provided password
                                if auto_password:
                                    generated_password = secrets.token_urlsafe(10)
                                    password_to_use = generated_password
                                else:
                                    password_to_use = user_password if 'user_password' in locals() and user_password else secrets.token_urlsafe(10)
                                
                                # Create user account
                                salt = _generate_salt()
                                password_hash = _hash_password(password_to_use, salt)
                                user_created = db.create_user(email, password_hash, salt, role=account_role)
                                
                                if user_created:
                                    if auto_password:
                                        # Save credentials to file
                                        cred_path = 'employee_credentials.txt'
                                        try:
                                            with open(cred_path, 'a', encoding='utf-8') as f:
                                                f.write(f'\n--- New Employee Account ---\n')
                                                f.write(f'Name: {employee_name}\n')
                                                f.write(f'Email: {email}\n')
                                                f.write(f'Password: {password_to_use}\n')
                                                f.write(f'Role: {account_role}\n')
                                                f.write(f'Created: {datetime.now()}\n')
                                            st.info(f"📧 Login credentials saved to {cred_path}")
                                        except Exception:
                                            st.warning(f"Account created. Email: {email}, Password: {password_to_use}")
                                    st.success("✅ Record added and user account created successfully!")
                                else:
                                    st.warning("✅ Record added but failed to create user account (email might already exist)")
                            else:
                                st.success("✅ Record added! User account already exists for this email.")
                        else:
                            st.success("✅ Record added successfully!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.error("⚠️ Please fill all required fields (*)")

elif page == "✏️ Edit Data":
    st.header("Edit Existing Record")
    
    df = get_cached_records()
    
    if not df.empty:
        # Add role filter
        col_filter1, col_filter2 = st.columns([1, 3])
        with col_filter1:
            role_filter = st.selectbox("Filter by Role:", ["All", "manager", "employee", "client"], index=0)
        
        # Filter records based on role
        if role_filter != "All":
            df_filtered = df[df['role'] == role_filter]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            st.warning(f"No records found for role: {role_filter}")
        else:
            # Different display for record options based on role
            if role_filter == 'client':
                record_options = [f"{row['id']} - {row['employee_name']} ({row.get('email', 'N/A')})" for _, row in df_filtered.iterrows()]
            else:
                record_options = [f"{row['id']} - {row['employee_name']} ({row['department']})" for _, row in df_filtered.iterrows()]
            
            selected_record = st.selectbox("Select record to edit:", record_options)
        
            if selected_record:
                record_id = int(selected_record.split(' - ')[0])
                record = df_filtered[df_filtered['id'] == record_id].iloc[0]
            
                # Check if user is a client
                is_client = (role_filter == 'client') or (pd.notna(record.get('role')) and record.get('role') == 'client')
            
                st.markdown("---")
            
                if is_client:
                    # Simplified form for clients
                    st.info("👤 **Editing Client Record** - Clients have a simplified profile")
                    with st.form("edit_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            employee_name = st.text_input("Client Name *", value=record['employee_name'])
                            email = st.text_input("Email *", value=record['email'] if pd.notna(record['email']) else "")
                            hire_date = st.date_input("Registration Date *", value=pd.to_datetime(record['hire_date']).date())
                        
                        with col2:
                            phone = st.text_input("Phone", value=record['phone'] if pd.notna(record['phone']) else "")
                            status = st.selectbox("Status *", ["Active", "Inactive"], index=["Active", "Inactive"].index(record['status']) if record['status'] in ["Active", "Inactive"] else 0)
                            password = st.text_input("Password", value=record.get('password', '123'), help="Client password")
                        
                        # Set client-specific values
                        department = None
                        position = None
                        salary = None
                        
                        submitted = st.form_submit_button("💾 Save Client Info", width='stretch')
                else:
                    # Full form for employees/managers
                    with st.form("edit_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            employee_name = st.text_input("Employee Name *", value=record['employee_name'])
                            department = st.selectbox("Department *", ["IT", "HR", "Sales", "Marketing", "Finance", "Administration", "Customer Service"], index=["IT", "HR", "Sales", "Marketing", "Finance", "Administration", "Customer Service"].index(record['department']) if record['department'] in ["IT", "HR", "Sales", "Marketing", "Finance", "Administration", "Customer Service"] else 0)
                            position = st.text_input("Position *", value=record['position'])
                            salary = st.number_input("Salary ($) *", value=float(record['salary']) if pd.notna(record.get('salary')) else 0.0, min_value=0.0, step=100.0, format="%.2f")
                        
                        with col2:
                            hire_date = st.date_input("Hire Date *", value=pd.to_datetime(record['hire_date']).date())
                            email = st.text_input("Email", value=record['email'] if pd.notna(record['email']) else "")
                            phone = st.text_input("Phone", value=record['phone'] if pd.notna(record['phone']) else "")
                            status = st.selectbox("Status *", ["Active", "Inactive", "On Leave"], index=["Active", "Inactive", "On Leave"].index(record['status']) if record['status'] in ["Active", "Inactive", "On Leave"] else 0)
                            password = st.text_input("Password", value=record.get('password', '123'), help="Employee password for records")
                        
                        submitted = st.form_submit_button("💾 Save Changes", width='stretch')
                
                if submitted:
                    try:
                        db.update_record(
                            record_id=record_id,
                            employee_name=employee_name,
                            department=department,
                            position=position,
                            salary=salary,
                            hire_date=str(hire_date),
                            email=email,
                            phone=phone,
                            status=status,
                            password=password
                        )
                        st.success("✅ Record updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        st.warning("No records to edit")

elif page == "🗑️ Delete Data":
    st.header("Delete Record")
    
    df = get_cached_records()
    
    if not df.empty:
        # Add role filter
        col_filter1, col_filter2 = st.columns([1, 3])
        with col_filter1:
            role_filter = st.selectbox("Filter by Role:", ["All", "manager", "employee", "client"], index=0)
        
        # Filter records based on role
        if role_filter != "All":
            df_filtered = df[df['role'] == role_filter]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            st.warning(f"No records found for role: {role_filter}")
        else:
            # Different display for record options based on role
            if role_filter == 'client':
                record_options = [f"{row['id']} - {row['employee_name']} ({row.get('email', 'N/A')})" for _, row in df_filtered.iterrows()]
            else:
                record_options = [f"{row['id']} - {row['employee_name']} ({row['department']})" for _, row in df_filtered.iterrows()]
            
            selected_record = st.selectbox("Select record to delete:", record_options)
        
            if selected_record:
                record_id = int(selected_record.split(' - ')[0])
                record = df_filtered[df_filtered['id'] == record_id].iloc[0]
                
                # Check if user is a client
                is_client = (role_filter == 'client') or (pd.notna(record.get('role')) and record.get('role') == 'client')
                
                st.markdown("---")
                st.subheader("Record Information:")
            
                if is_client:
                    # Simplified view for clients
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Client Name:** {record['employee_name']}")
                        st.write(f"**Email:** {record.get('email', 'N/A')}")
                        st.write(f"**Phone:** {record.get('phone', 'N/A')}")
                    with col2:
                        st.write(f"**Registration Date:** {record['hire_date']}")
                        st.write(f"**Status:** {record['status']}")
                        st.write(f"**Password:** {record.get('password', 'N/A')}")
                else:
                    # Full view for employees/managers
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {record['employee_name']}")
                        st.write(f"**Department:** {record.get('department', 'N/A')}")
                        st.write(f"**Position:** {record.get('position', 'N/A')}")
                        st.write(f"**Password:** {record.get('password', 'N/A')}")
                    with col2:
                        st.write(f"**Salary:** {record.get('salary', 0):,.0f} $")
                        st.write(f"**Hire Date:** {record['hire_date']}")
                        st.write(f"**Status:** {record['status']}")
            
                st.markdown("---")
                st.warning("⚠️ Warning: This action cannot be undone!")
            
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🗑️ Confirm Delete", width='stretch', type="primary"):
                        try:
                            db.delete_record(record_id)
                            st.success("✅ Record deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            with col2:
                if st.button("❌ Cancel", width='stretch'):
                    st.info("Delete operation cancelled")
    else:
        st.warning("No records to delete")

elif page_matches(page, 'analytics'):
    df = get_cached_records()
    
    if not df.empty:
        tab1, tab2, tab3 = st.tabs(["📊 Distribution", "💰 Salaries", "📈 Trends"])
        
        with tab1:
            st.subheader("Employee Distribution by Department")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Employee Status")
                fig3 = data_manager.create_status_pie_chart(df)
                st.plotly_chart(fig3, use_container_width=True)
            with col2:
                st.subheader("Common Positions")
                fig4 = data_manager.create_position_chart(df)
                st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("No data available for charts")

elif page_matches(page, 'request_leave'):
    st.header(t('request_leave'))
    user = st.session_state.get('user')
    if not user:
        st.error("Please log in to submit a leave request.")
        st.stop()

    # Request card
    with st.container():
        st.markdown("<div style='background: #262730; border: 1px solid #262730; padding: 16px; border-radius: 8px; margin-bottom: 16px;'><h3 style='margin: 0 0 12px 0; color: #e6eef8;'>Submit Leave Request</h3></div>", unsafe_allow_html=True)
        with st.form("request_leave_form"):
            c1, c2 = st.columns([1, 2])
            with c1:
                start_date = st.date_input(t('start_date'), value=date.today())
                end_date = st.date_input(t('end_date'), value=date.today())
                leave_type = st.selectbox(t('leave_type'), ["Other", "Paid", "Unpaid", "Sick"], index=0)
            with c2:
                reason = st.text_area(t('reason'), height=130, placeholder="Provide a short reason for your leave...")
                attachment_file = st.file_uploader(t('attachment'))
            submitted = st.form_submit_button(t('submit'), width='stretch')
            if submitted:
                if start_date > end_date:
                    st.error("End date must be the same or after start date.")
                else:
                    try:
                        # handle optional attachment save
                        attachment_name = ''
                        if attachment_file is not None:
                            try:
                                os.makedirs('uploads', exist_ok=True)
                                safe_name = f"user{user['id']}_{int(time.time())}_{attachment_file.name}"
                                save_path = os.path.join('uploads', safe_name)
                                with open(save_path, 'wb') as out:
                                    out.write(attachment_file.getbuffer())
                                attachment_name = safe_name
                            except Exception as e:
                                st.warning(f"Could not save attachment: {e}")

                        db.create_leave_request(user['id'], str(start_date), str(end_date), reason, leave_type, attachment_name)
                        st.success("Leave request submitted successfully.")
                        _safe_rerun()
                    except Exception as e:
                        st.error(f"Failed to submit request: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

    # My requests
    st.markdown("---")
    st.subheader(t('my_requests'))
    try:
        df = db.get_leave_requests_by_user(user['id'])
        if df.empty:
            st.info(t('no_requests'))
        else:
            for _, r in df.iterrows():
                status = (r.get('status') or 'Pending').lower()
                badge_class = 'status-pending'
                status_display = r.get('status', 'Pending')
                if status == 'approved':
                    badge_class = 'status-approved'
                    status_display = t('approved')
                elif status == 'rejected':
                    badge_class = 'status-rejected'
                    status_display = t('rejected')
                elif status == 'pending':
                    status_display = t('pending')

                st.markdown("<div class='card request-row'>", unsafe_allow_html=True)
                col_left, col_right = st.columns([3,1])
                with col_left:
                    st.markdown(f"<span style='color: #e6eef8;'>**{t('from')}:** {r.get('start_date')}  &nbsp;&nbsp; **{t('to')}:** {r.get('end_date')}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #e6eef8;'>**{t('type')}:** {r.get('leave_type', 'Other')}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #e6eef8;'>**{t('reason')}:** {r.get('reason')}</span>", unsafe_allow_html=True)
                    # show attachment if present
                    attachment = (r.get('attachment') or '').strip()
                    if attachment:
                        filepath = os.path.join('uploads', attachment)
                        if os.path.exists(filepath):
                            try:
                                with open(filepath, 'rb') as f:
                                    st.download_button(label=f"Download attachment: {attachment}", data=f, file_name=attachment)
                            except Exception:
                                st.markdown(f"Attachment: {attachment}")
                        else:
                            st.markdown(f"Attachment: {attachment}")
                    resp = r.get('admin_response')
                    if resp:
                        st.markdown(f"<span style='color: #e6eef8;'>**Manager response:** {resp}</span>", unsafe_allow_html=True)
                with col_right:
                    st.markdown(f"<span class='status-badge {badge_class}'>{status_display}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load your requests: {str(e)}")

elif page_matches(page, 'manage_leaves'):
    st.header(t('manage_leaves'))
    user = st.session_state.get('user')
    if not user or user.get('role') != 'manager':
        st.error("You must be a manager to manage leave requests.")
        st.stop()

    try:
        df = db.get_all_leave_requests()
        if df.empty:
            st.info("No leave requests found.")
        else:
            for _, row in df.iterrows():
                rid = int(row['id'])
                with st.expander(f"Request {rid} — {row.get('user_email', '')}"):
                    st.write(f"{t('from')}: {row.get('start_date')}  {t('to')}: {row.get('end_date')}")
                    st.write(f"{t('type')}: {row.get('leave_type', 'Other')}")
                    st.write(f"{t('reason')}: {row.get('reason')}")
                    # show attachment if present
                    att = (row.get('attachment') or '').strip()
                    if att:
                        att_path = os.path.join('uploads', att)
                        if os.path.exists(att_path):
                            try:
                                with open(att_path, 'rb') as af:
                                    st.download_button(label=f"Download attachment: {att}", data=af, file_name=att)
                            except Exception:
                                st.write(f"Attachment: {att}")
                        else:
                            st.write(f"Attachment: {att}")
                    st.write(f"{t('status')}: {row.get('status')}")
                    st.write(f"User: {row.get('user_email')}")
                    with st.form(f"manage_{rid}"):
                        status_list = ["Pending", "Approved", "Rejected"]
                        new_status = st.selectbox(t('set_status'), status_list, index=status_list.index(row.get('status', 'Pending')) if row.get('status') in status_list else 0)
                        response = st.text_area(t('response_user'), value=row.get('admin_response', ''))
                        submitted = st.form_submit_button(t('save'))
                        if submitted:
                            try:
                                db.update_leave_request_status(rid, new_status, response)
                                st.success("Request updated.")
                                _safe_rerun()
                            except Exception as e:
                                st.error(f"Failed to update: {str(e)}")
    except Exception as e:
        st.error(f"Error loading requests: {str(e)}")

elif page_matches(page, 'manage_users'):
    st.header(t('manage_users'))
    user = st.session_state.get('user')
    if not user or user.get('role') != 'manager':
        st.error("You must be a manager to manage users.")
        st.stop()

    try:
        # Get all records from company_records (same as View Data)
        df = get_cached_records()
        
        if df.empty:
            st.info("No users found.")
        else:
            # Display the full data table
            st.dataframe(df, use_container_width=True, height=400)
            
            st.markdown("---")
            st.subheader("Change User Role")
            
            # Get list of users with email
            users_with_email = df[df['email'].notna()]['email'].tolist()
            
            if not users_with_email:
                st.warning("No users with email addresses found.")
            else:
                cols = st.columns(3)
                with cols[0]:
                    selected_user = st.selectbox("Select user:", users_with_email)
                with cols[1]:
                    new_role = st.selectbox("New role:", ["employee", "client", "manager"])
                with cols[2]:
                    if st.button("Update Role"):
                        try:
                            # Get user from users table by email
                            existing_user = db.get_user_by_email(selected_user)
                            if existing_user:
                                db.update_user_role(existing_user['id'], new_role)
                                st.success("User role updated.")
                                _safe_rerun()
                            else:
                                st.error("User not found in users table. Please create login account first.")
                        except Exception as e:
                            st.error(f"Failed to update role: {str(e)}")
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")

# Shipment Management Pages
elif page_matches(page, 'manage_shipments'):
    st.header(t('manage_shipments'))
    user = st.session_state.get('user')
    if not user or user.get('role') not in ['manager', 'employee']:
        st.error("You must be a manager or employee to manage shipments.")
        st.stop()

    try:
        # Fetch data from database with caching
        df = get_cached_shipments()
        
        if df.empty:
            st.info("No shipments found. Add a new shipment to get started.")
        else:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                shipment_types = ['All'] + list(df['type'].unique())
                selected_type = st.selectbox("Filter by Type:", shipment_types)
            with col2:
                statuses = ['All'] + list(df['status'].unique())
                selected_status = st.selectbox("Filter by Status:", statuses)
            with col3:
                search_term = st.text_input("🔍 Search", placeholder="Shipment number, client...")
            
            # Apply filters
            filtered_df = df.copy()
            if selected_type != 'All':
                filtered_df = filtered_df[filtered_df['type'] == selected_type]
            if selected_status != 'All':
                filtered_df = filtered_df[filtered_df['status'] == selected_status]
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['shipment_number'].str.contains(search_term, case=False, na=False) |
                    filtered_df['client_email'].str.contains(search_term, case=False, na=False)
                ]
            
            st.dataframe(filtered_df, width='stretch')
            
            # Shipment details and management
            st.markdown("---")
            st.subheader("Shipment Details & Management")
            
            if not filtered_df.empty:
                shipment_nums = filtered_df['shipment_number'].tolist()
                selected_shipment = st.selectbox("Select Shipment:", shipment_nums)
                
                # Get fresh data from database for selected shipment
                fresh_df = db.get_all_shipments()
                ship_data = fresh_df[fresh_df['shipment_number'] == selected_shipment].iloc[0]
                
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Details", "📦 Cargo Items", "🗺️ Tracking", "📄 Documents"])
                
                with tab1:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**{t('shipment_number')}:** {ship_data['shipment_number']}")
                        st.write(f"**Type:** {ship_data['type']}")
                        st.write(f"**{t('origin')}:** {ship_data['origin_country']}")
                        st.write(f"**{t('destination')}:** {ship_data['destination_country']}")
                        st.write(f"**Client:** {ship_data['client_email']}")
                    with col_b:
                        st.write(f"**{t('departure_date')}:** {ship_data['departure_date']}")
                        st.write(f"**{t('expected_arrival')}:** {ship_data['expected_arrival']}")
                        st.write(f"**{t('actual_arrival')}:** {ship_data.get('actual_arrival', 'N/A')}")
                        st.write(f"**{t('total_weight')}:** {ship_data['total_weight']} kg")
                        st.write(f"**{t('total_value')}:** {ship_data['currency']} {ship_data['total_value']:,.2f}")
                    
                    st.markdown("---")
                    st.subheader("Update Status")
                    with st.form("update_status_form"):
                        status_options = ["Pending", "In Transit", "Customs", "Delivered", "Cancelled"]
                        new_status = st.selectbox(t('shipment_status'), status_options, 
                                                index=status_options.index(ship_data['status']) if ship_data['status'] in status_options else 0)
                        actual_arrival_date = st.date_input(t('actual_arrival'), value=None)
                        customs_check = st.checkbox(t('customs_cleared'), value=bool(ship_data.get('customs_cleared', 0)))
                        
                        if st.form_submit_button("Update Status"):
                            try:
                                # Update shipment status
                                db.update_shipment_status(ship_data['id'], new_status, 
                                                        str(actual_arrival_date) if actual_arrival_date else None)
                                # Update customs status
                                db.update_customs_status(ship_data['id'], customs_check)
                                
                                st.success("✅ Status updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                
                with tab2:
                    st.subheader(t('cargo_items'))
                    cargo_df = db.get_cargo_items_by_shipment(ship_data['id'])
                    if not cargo_df.empty:
                        st.dataframe(cargo_df, width='stretch')
                        
                        st.markdown("---")
                        st.markdown("### 🔧 Manage Cargo Items")
                        # Edit and Delete cargo items
                        col_edit, col_delete = st.columns(2)
                        
                        with col_edit:
                            st.markdown("#### ✏️ Edit Cargo Item")
                            item_to_edit = st.selectbox("Select item to edit:", 
                                [(f"{row['id']} - {row['item_name']}", row['id']) for _, row in cargo_df.iterrows()],
                                format_func=lambda x: x[0], key="edit_cargo_select")
                            
                            if item_to_edit:
                                selected_id = item_to_edit[1]
                                selected_item = cargo_df[cargo_df['id'] == selected_id].iloc[0]
                                
                                with st.form("edit_cargo_form"):
                                    edit_item_name = st.text_input("Item Name", value=selected_item['item_name'])
                                    col_e1, col_e2 = st.columns(2)
                                    with col_e1:
                                        edit_quantity = st.number_input("Quantity", min_value=1, value=int(selected_item['quantity']))
                                        edit_weight = st.number_input("Weight (kg)", min_value=0.0, value=float(selected_item['weight']))
                                    with col_e2:
                                        edit_unit = st.selectbox("Unit", ["pcs", "kg", "ton", "box", "container"],
                                            index=["pcs", "kg", "ton", "box", "container"].index(selected_item['unit']) 
                                            if selected_item['unit'] in ["pcs", "kg", "ton", "box", "container"] else 0)
                                        edit_value = st.number_input("Value", min_value=0.0, value=float(selected_item['value']))
                                    edit_description = st.text_area("Description", value=selected_item.get('description', ''))
                                    edit_hs_code = st.text_input("HS Code", value=selected_item.get('hs_code', ''))
                                    
                                    if st.form_submit_button("💾 Save Changes", width='stretch'):
                                        try:
                                            db.update_cargo_item(
                                                item_id=selected_id,
                                                item_name=edit_item_name,
                                                quantity=edit_quantity,
                                                weight=edit_weight,
                                                unit=edit_unit,
                                                value=edit_value,
                                                description=edit_description,
                                                hs_code=edit_hs_code
                                            )
                                            st.success("✅ Cargo item updated successfully!")
                                            _safe_rerun()
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                        
                        with col_delete:
                            st.markdown("#### 🗑️ Delete Cargo Item")
                            item_to_delete = st.selectbox("Select item to delete:", 
                                [(f"{row['id']} - {row['item_name']}", row['id']) for _, row in cargo_df.iterrows()],
                                format_func=lambda x: x[0], key="delete_cargo_select")
                            
                            if item_to_delete:
                                delete_id = item_to_delete[1]
                                delete_item = cargo_df[cargo_df['id'] == delete_id].iloc[0]
                                
                                st.markdown("**Item Details:**")
                                st.write(f"📦 **Item:** {delete_item['item_name']}")
                                st.write(f"📊 **Quantity:** {delete_item['quantity']} {delete_item['unit']}")
                                st.write(f"⚖️ **Weight:** {delete_item['weight']} kg")
                                st.write(f"💰 **Value:** ${delete_item['value']:,.2f}")
                                
                                st.warning("⚠️ This action cannot be undone!")
                                
                                if st.button("🗑️ Confirm Delete", type="primary", width='stretch'):
                                    try:
                                        db.delete_cargo_item(delete_id)
                                        st.success("✅ Item deleted successfully!")
                                        _safe_rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
                    else:
                        st.info("No cargo items found.")
                    
                    st.markdown("---")
                    st.subheader(f"➕ {t('add_cargo')}")
                    with st.form("add_cargo_form"):
                        c1, c2 = st.columns(2)
                        with c1:
                            item_name = st.text_input(t('item_name') + " *")
                            quantity = st.number_input(t('quantity') + " *", min_value=1, value=1)
                            weight = st.number_input(t('weight') + " *", min_value=0.0, value=0.0)
                        with c2:
                            unit = st.selectbox("Unit *", ["pcs", "kg", "ton", "box", "container"])
                            value = st.number_input(t('value') + " *", min_value=0.0, value=0.0)
                            description = st.text_area(t('description'))
                        hs_code = st.text_input("HS Code (Optional)")
                        
                        if st.form_submit_button(f"➕ {t('add_cargo')}", width='stretch'):
                            if item_name:
                                try:
                                    db.add_cargo_item(
                                        int(ship_data['id']), 
                                        item_name, 
                                        description, 
                                        int(quantity), 
                                        unit, 
                                        float(weight), 
                                        float(value), 
                                        hs_code
                                    )
                                    st.success("✅ Cargo item added successfully!")
                                    _safe_rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                            else:
                                st.error("⚠️ Please enter item name")
                
                with tab3:
                    st.subheader(t('tracking'))
                    tracking_df = db.get_tracking_updates(ship_data['id'])
                    if not tracking_df.empty:
                        for _, row in tracking_df.iterrows():
                            status_class = row['status'].lower().replace(' ', '-')
                            notes_html = f"<div style='color: #b8bcc4; margin-top: 5px;'>📝 {row['notes']}</div>" if row.get('notes') else ''
                            updated_by = row.get('updated_by_email', 'System')
                            
                            st.markdown(f"""
                            <div style='background: #262730; border: 1px solid #262730; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                                <div style='color: #e6eef8;'><strong>📅 {row['update_date']}</strong> - 📍 {row['location']}</div>
                                <div style='margin: 8px 0;'><span class='status-badge status-{status_class}'>{row['status']}</span></div>
                                {notes_html}
                                👤 Updated by: {updated_by}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No tracking updates yet.")
                    
                    st.markdown("---")
                    st.subheader(t('update_tracking'))
                    with st.form("add_tracking_form"):
                        location = st.text_input(t('location') + " *", placeholder="e.g., Port of Jeddah")
                        track_status = st.selectbox("Status *", ["Departed", "In Transit", "Arrived at Port", "Customs", "Out for Delivery", "Delivered"])
                        track_date = st.date_input("Update Date *", value=date.today())
                        track_notes = st.text_area("Notes", placeholder="Optional notes about this update...")
                        
                        if st.form_submit_button("📍 Add Update", width='stretch'):
                            if location:
                                try:
                                    db.add_tracking_update(ship_data['id'], location, track_status, 
                                                          track_notes, str(track_date), user['id'])
                                    st.success("✅ Tracking update added successfully!")
                                    _safe_rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                            else:
                                st.error("Please enter location")
                
                with tab4:
                    st.subheader(t('documents'))
                    docs_df = db.get_shipment_documents(ship_data['id'])
                    if not docs_df.empty:
                        for _, doc in docs_df.iterrows():
                            st.markdown(f"""
                            <div class='card'>
                                <strong>{doc['document_type']}</strong><br>
                                File: {doc['file_path']}<br>
                                Uploaded by: {doc.get('uploaded_by_email', 'Unknown')}<br>
                                Date: {doc['created_at']}<br>
                                {f"Notes: {doc['notes']}" if doc['notes'] else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No documents uploaded yet.")
                    
                    st.markdown("---")
                    st.subheader(t('upload_document'))
                    with st.form("upload_doc_form"):
                        doc_type = st.selectbox("Document Type", 
                            ["Invoice", "Bill of Lading", "Customs Declaration", "Certificate of Origin", "Packing List", "Other"])
                        uploaded_file = st.file_uploader("Choose file")
                        doc_notes = st.text_area("Notes")
                        
                        if st.form_submit_button("Upload"):
                            if uploaded_file:
                                try:
                                    # Save file
                                    os.makedirs("shipment_documents", exist_ok=True)
                                    file_path = os.path.join("shipment_documents", 
                                                            f"{ship_data['shipment_number']}_{uploaded_file.name}")
                                    with open(file_path, "wb") as f:
                                        f.write(uploaded_file.getbuffer())
                                    
                                    db.add_shipment_document(ship_data['id'], doc_type, file_path, user['id'], doc_notes)
                                    st.success("Document uploaded!")
                                    _safe_rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.error("Please select a file")
    except Exception as e:
        st.error(f"Error loading shipments: {str(e)}")

elif page_matches(page, 'add_shipment'):
    st.header(t('add_shipment'))
    user = st.session_state.get('user')
    if not user or user.get('role') not in ['manager', 'employee']:
        st.error("You must be a manager or employee to add shipments.")
        st.stop()

    with st.form("add_shipment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            shipment_number = st.text_input(t('shipment_number') + " *", placeholder="SH-2025-001")
            shipment_type = st.selectbox("Type *", ["Import", "Export"])
            
            # Country dropdown list (alphabetically sorted)
            countries = [
                "Algeria", "Argentina", "Australia", "Austria", "Bahrain", "Belgium", "Brazil",
                "Canada", "China", "Denmark", "Egypt", "France", "Germany", "India", "Iraq",
                "Italy", "Japan", "Jordan", "Kuwait", "Lebanon", "Libya", "Mexico", "Morocco",
                "Netherlands", "Norway", "Oman", "Palestine", "Poland", "Qatar", "Russia",
                "Saudi Arabia", "South Korea", "Spain", "Sudan", "Sweden", "Switzerland", "Syria",
                "Tunisia", "Turkey", "UAE", "United Kingdom", "United States", "Yemen"
            ]
            
            origin_country = st.selectbox(t('origin') + " *", countries)
            destination_country = st.selectbox(t('destination') + " *", countries)
            departure_date = st.date_input(t('departure_date') + " *", value=date.today())
        
        with col2:
            # Get all clients for selection
            try:
                users_df = db.get_all_users()
                clients = users_df[users_df['role'] == 'client']
                if clients.empty:
                    st.warning("⚠️ No clients found. Please create a user with 'client' role first.")
                    client_options = []
                else:
                    client_options = clients['email'].tolist()
            except Exception as e:
                st.error(f"Error loading users: {str(e)}")
                client_options = []
            
            if client_options:
                client_email = st.selectbox("Client *", client_options)
            else:
                st.error("Please create at least one client user before adding shipments.")
                client_email = None
            
            expected_arrival = st.date_input(t('expected_arrival') + " *")
            total_weight = st.number_input(t('total_weight') + " *", min_value=0.0, value=0.0)
            total_value = st.number_input(t('total_value') + " *", min_value=0.0, value=0.0)
            currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "TRY"])
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("➕ Add Shipment", width='stretch')
        
        if submitted:
            if not client_options:
                st.error("❌ Cannot add shipment: No clients available. Please create a client user first.")
            elif shipment_number and origin_country and destination_country and client_email:
                try:
                    # Get client ID
                    client_data = users_df[users_df['email'] == client_email].iloc[0]
                    client_id = int(client_data['id'])
                    
                    st.write(f"Debug: Creating shipment for client_id={client_id}")  # Debug
                    
                    shipment_id = db.create_shipment(
                        shipment_number=shipment_number,
                        client_id=client_id,
                        shipment_type=shipment_type,
                        origin_country=origin_country,
                        destination_country=destination_country,
                        departure_date=str(departure_date),
                        expected_arrival=str(expected_arrival),
                        total_weight=total_weight,
                        total_value=total_value,
                        currency=currency,
                        notes=notes
                    )
                    
                    st.write(f"Debug: Shipment ID returned: {shipment_id}")  # Debug
                    
                    if shipment_id:
                        st.success(f"✅ Shipment {shipment_number} created successfully with ID: {shipment_id}")
                        _safe_rerun()
                    else:
                        st.error("❌ Failed to create shipment. The shipment number might already exist.")
                except Exception as e:
                    st.error(f"❌ Error creating shipment: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                st.error("⚠️ Please fill all required fields (*)")

elif page_matches(page, 'my_shipments'):
    st.header(t('my_shipments'))
    user = st.session_state.get('user')
    if not user or user.get('role') != 'client':
        st.error("This page is only for clients.")
        st.stop()

    try:
        df = db.get_shipments_by_client(user['id'])
        if df.empty:
            st.info("You have no shipments yet.")
        else:
            st.dataframe(df, width='stretch')
            
            st.markdown("---")
            st.subheader("Shipment Details")
            
            shipment_nums = df['shipment_number'].tolist()
            selected_shipment = st.selectbox("Select Your Shipment:", shipment_nums)
            
            ship_data = df[df['shipment_number'] == selected_shipment].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(t('shipment_status'), ship_data['status'])
                st.write(f"**{t('origin')}:** {ship_data['origin_country']}")
                st.write(f"**{t('destination')}:** {ship_data['destination_country']}")
                st.write(f"**Type:** {ship_data['type']}")
            with col2:
                st.metric(t('total_value'), f"{ship_data['currency']} {ship_data['total_value']:,.2f}")
                st.write(f"**{t('departure_date')}:** {ship_data['departure_date']}")
                st.write(f"**{t('expected_arrival')}:** {ship_data['expected_arrival']}")
                st.write(f"**{t('customs_cleared')}:** {'Yes' if ship_data.get('customs_cleared') else 'No'}")
            
            # Show cargo items
            st.markdown("---")
            st.subheader(t('cargo_items'))
            cargo_df = db.get_cargo_items_by_shipment(ship_data['id'])
            if not cargo_df.empty:
                st.dataframe(cargo_df[['item_name', 'quantity', 'unit', 'weight', 'value']], width='stretch')
            else:
                st.info("No cargo items listed.")
            
            # Show tracking
            st.markdown("---")
            st.subheader(t('tracking'))
            tracking_df = db.get_tracking_updates(ship_data['id'])
            if not tracking_df.empty:
                for _, row in tracking_df.iterrows():
                    st.markdown(f"""
                    <div class='card'>
                        <strong>{row['update_date']}</strong> - {row['location']}<br>
                        <span class='status-badge status-{row['status'].lower().replace(' ', '-')}'>{row['status']}</span><br>
                        {row['notes'] if row['notes'] else ''}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No tracking updates yet.")
    except Exception as e:
        st.error(f"Error loading your shipments: {str(e)}")

elif page_matches(page, 'track_shipment'):
    st.header(t('track_shipment'))
    
    shipment_number = st.text_input("Enter Shipment Number:", placeholder="SH-2025-001")
    
    if st.button("🔍 Track"):
        if shipment_number:
            try:
                df = get_cached_shipments()
                ship_data = df[df['shipment_number'] == shipment_number]
                
                if ship_data.empty:
                    st.error("Shipment not found.")
                else:
                    ship = ship_data.iloc[0]
                    
                    # Check if user is client and can only view their own shipments
                    user = st.session_state.get('user')
                    if user and user.get('role') == 'client' and ship['client_id'] != user['id']:
                        st.error("You can only track your own shipments.")
                        st.stop()
                    
                    st.success(f"Shipment Found: {shipment_number}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Status", ship['status'])
                    with col2:
                        st.metric("Origin", ship['origin_country'])
                    with col3:
                        st.metric("Destination", ship['destination_country'])
                    
                    st.markdown("---")
                    st.subheader("Tracking History")
                    
                    tracking_df = db.get_tracking_updates(ship['id'])
                    if not tracking_df.empty:
                        for _, row in tracking_df.iterrows():
                            st.markdown(f"""
                            <div class='card'>
                                <strong>📍 {row['location']}</strong><br>
                                <span class='status-badge status-{row['status'].lower().replace(' ', '-')}'>{row['status']}</span><br>
                                Date: {row['update_date']}<br>
                                {row['notes'] if row['notes'] else ''}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No tracking updates available yet.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a shipment number.")

elif page_matches(page, 'shipment_analytics'):
    st.header(t('shipment_analytics'))
    user = st.session_state.get('user')
    if not user or user.get('role') not in ['manager', 'employee']:
        st.error("You must be a manager or employee to view analytics.")
        st.stop()

    try:
        stats = db.get_shipment_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Shipments", stats['total_shipments'])
        with col2:
            st.metric("Imports", stats['total_imports'])
        with col3:
            st.metric("Exports", stats['total_exports'])
        with col4:
            st.metric("In Transit", stats['in_transit'])
        
        st.metric("Total Value", f"${stats['total_value']:,.2f}")
        
        # Charts
        df = db.get_all_shipments()
        if not df.empty:
            st.markdown("---")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("Shipments by Type")
                type_counts = df['type'].value_counts()
                st.bar_chart(type_counts)
            
            with col_b:
                st.subheader("Shipments by Status")
                status_counts = df['status'].value_counts()
                st.bar_chart(status_counts)
            
            st.markdown("---")
            st.subheader("Recent Shipments")
            st.dataframe(df.head(10), width='stretch')
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

elif page_matches(page, 'cargo_requests'):
    st.header(t('cargo_requests'))
    user = st.session_state.get('user')
    if not user or user.get('role') != 'client':
        st.error("This page is only for clients.")
        st.stop()

    try:
        st.subheader(t('request_cargo_change'))
        
        # Get all cargo items from database
        conn = db.get_connection()
        cargo_df = pd.read_sql_query('SELECT * FROM cargo_items', conn)
        conn.close()
        
        if not cargo_df.empty:
            with st.form("cargo_request_form"):
                # Select cargo item directly (no shipment selection needed)
                cargo_options = [(f"{row['item_name']} - {row['quantity']} {row['unit']}", row['id']) 
                               for _, row in cargo_df.iterrows()]
                selected_cargo = st.selectbox("Select Cargo Item:", cargo_options, format_func=lambda x: x[0])
                
                # Request type
                request_type = st.selectbox(t('request_type'), [t('modify'), t('remove')])
                
                # Reason
                reason = st.text_area(t('request_reason'), placeholder="Please explain why you need this change...")
                
                submitted = st.form_submit_button(t('submit'))
                
                if submitted:
                    if reason:
                        try:
                            cargo_id = selected_cargo[1]
                            db.create_cargo_request(cargo_id, user['id'], request_type, reason)
                            st.success("✅ Request submitted successfully!")
                            _safe_rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    else:
                        st.error("Please provide a reason for your request.")
        else:
            st.info("No cargo items available for requests.")
        
        # Show client's requests
        st.markdown("---")
        st.subheader(t('my_cargo_requests'))
        requests_df = db.get_cargo_requests_by_client(user['id'])
        
        if requests_df.empty:
            st.info("You have no cargo requests.")
        else:
            for _, req in requests_df.iterrows():
                status = req.get('status', 'Pending')
                badge_class = 'status-pending'
                if status == 'Approved':
                    badge_class = 'status-approved'
                elif status == 'Rejected':
                    badge_class = 'status-rejected'
                
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Shipment:** {req.get('shipment_number', 'N/A')}")
                    st.write(f"**Item:** {req.get('item_name', 'N/A')}")
                    st.write(f"**Request Type:** {req.get('request_type', 'N/A')}")
                    st.write(f"**Reason:** {req.get('reason', 'N/A')}")
                    if req.get('employee_response'):
                        st.write(f"**Employee Response:** {req.get('employee_response')}")
                    st.write(f"**Date:** {req.get('created_at', 'N/A')}")
                with col2:
                    st.markdown(f"<span class='status-badge {badge_class}'>{status}</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")

elif page_matches(page, 'manage_cargo_requests'):
    st.header(t('manage_cargo_requests'))
    user = st.session_state.get('user')
    if not user or user.get('role') not in ['manager', 'employee']:
        st.error("You must be a manager or employee to manage cargo requests.")
        st.stop()

    try:
        requests_df = db.get_all_cargo_requests()
        
        if requests_df.empty:
            st.info("No cargo requests found.")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox("Filter by Status:", ["All", "Pending", "Approved", "Rejected"])
            with col2:
                type_filter = st.selectbox("Filter by Type:", ["All", t('modify'), t('remove')])
            
            # Apply filters
            filtered_df = requests_df.copy()
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            if type_filter != "All":
                filtered_df = filtered_df[filtered_df['request_type'] == type_filter]
            
            st.markdown("---")
            
            if filtered_df.empty:
                st.info("No requests match the selected filters.")
            else:
                for _, req in filtered_df.iterrows():
                    request_id = int(req['id'])
                    
                    with st.expander(f"Request #{request_id} - {req.get('client_email', 'Unknown')} - {req.get('status', 'Pending')}"):
                        col_info, col_action = st.columns([2, 1])
                        
                        with col_info:
                            st.write(f"**Client:** {req.get('client_email', 'Unknown')}")
                            st.write(f"**Shipment:** {req.get('shipment_number', 'N/A')}")
                            st.write(f"**Cargo Item:** {req.get('item_name', 'N/A')}")
                            st.write(f"**Request Type:** {req.get('request_type', 'N/A')}")
                            st.write(f"**Reason:** {req.get('reason', 'N/A')}")
                            st.write(f"**Date:** {req.get('created_at', 'N/A')}")
                            st.write(f"**Current Status:** {req.get('status', 'Pending')}")
                        
                        with col_action:
                            if req.get('status') == 'Pending':
                                with st.form(f"manage_request_{request_id}"):
                                    new_status = st.selectbox("Action:", ["Pending", "Approved", "Rejected"], 
                                                            key=f"status_{request_id}")
                                    response = st.text_area("Response to client:", key=f"response_{request_id}")
                                    
                                    if st.form_submit_button(t('save')):
                                        try:
                                            db.update_cargo_request_status(request_id, new_status, response)
                                            
                                            # If approved and request is to remove, delete the cargo item
                                            if new_status == "Approved" and req.get('request_type') == t('remove'):
                                                db.delete_cargo_item(req['cargo_item_id'])
                                            
                                            st.success("Request updated successfully!")
                                            _safe_rerun()
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                            else:
                                st.info(f"Status: {req.get('status')}")
                                if req.get('employee_response'):
                                    st.write(f"**Response:** {req.get('employee_response')}")
    except Exception as e:
        st.error(f"Error loading requests: {str(e)}")

elif page_matches(page, 'edit_shipment'):
    st.header(t('edit_shipment'))
    user = st.session_state.get('user')
    if not user or user.get('role') not in ['manager', 'employee']:
        st.error("Only managers and employees can edit shipments.")
        st.stop()

    # Clear any session state cache
    if 'last_edited_shipment' not in st.session_state:
        st.session_state.last_edited_shipment = None

    try:
        # Get fresh data
        df = db.get_all_shipments()
        
        if df.empty:
            st.info("No shipments found.")
        else:
            # Select shipment to edit
            shipment_nums = df['shipment_number'].tolist()
            selected_shipment = st.selectbox("Select Shipment to Edit:", shipment_nums)
            
            # Always get fresh data for selected shipment
            fresh_df = db.get_all_shipments()
            ship_data = fresh_df[fresh_df['shipment_number'] == selected_shipment].iloc[0]
            
            st.markdown("---")
            st.subheader(f"Edit Shipment: {selected_shipment}")
            
            # Show current values
            with st.expander("Current Values", expanded=False):
                st.write(f"Type: {ship_data['type']}")
                st.write(f"Origin: {ship_data['origin_country']}")
                st.write(f"Destination: {ship_data['destination_country']}")
                st.write(f"Weight: {ship_data['total_weight']} kg")
                st.write(f"Value: {ship_data['currency']} {ship_data['total_value']}")
            
            with st.form("edit_shipment_form", clear_on_submit=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    shipment_type = st.selectbox(t('type'), ["Import", "Export"], 
                                                index=0 if ship_data['type'] == 'Import' else 1)
                    origin = st.text_input(t('origin'), value=ship_data['origin_country'])
                    destination = st.text_input(t('destination'), value=ship_data['destination_country'])
                    departure = st.date_input(t('departure_date'), 
                                             value=pd.to_datetime(ship_data['departure_date']).date())
                
                with col2:
                    expected = st.date_input(t('expected_arrival'), 
                                            value=pd.to_datetime(ship_data['expected_arrival']).date())
                    weight = st.number_input(t('total_weight'), value=float(ship_data['total_weight']), min_value=0.0)
                    value_amount = st.number_input(t('total_value'), value=float(ship_data['total_value']), min_value=0.0)
                    currency = st.selectbox("Currency", ["USD", "EUR", "TRY"], 
                                           index=["USD", "EUR", "TRY"].index(ship_data['currency']))
        
                submitted = st.form_submit_button("💾 Save Changes")
                
                if submitted:
                    try:
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        
                        # Execute update
                        cursor.execute('''
                            UPDATE shipments 
                            SET type=%s, origin_country=%s, destination_country=%s,
                                departure_date=%s, expected_arrival=%s, total_weight=%s, 
                                total_value=%s, currency=%s, updated_at=CURRENT_TIMESTAMP
                            WHERE id=%s
                        ''', (shipment_type, origin, destination, str(departure), str(expected),
                              weight, value_amount, currency, int(ship_data['id'])))
                        
                        conn.commit()
                        conn.close()
                        
                        # Store in session state
                        st.session_state.last_edited_shipment = selected_shipment
                        
                        st.success(f"✅ Shipment {selected_shipment} updated successfully!")
                        st.info("Please refresh the page to see changes in the table.")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

elif page_matches(page, 'delete_shipment'):
    st.header(t('delete_shipment'))
    user = st.session_state.get('user')
    if not user or user.get('role') not in ['manager', 'employee']:
        st.error("Only managers and employees can delete shipments.")
        st.stop()

    try:
        df = db.get_all_shipments()
        
        if df.empty:
            st.info("No shipments found.")
        else:
            # Select shipment to delete
            shipment_nums = df['shipment_number'].tolist()
            selected_shipment = st.selectbox("Select Shipment to Delete:", shipment_nums)
            
            ship_data = df[df['shipment_number'] == selected_shipment].iloc[0]
            
            st.markdown("---")
            st.warning(f"⚠️ You are about to delete shipment: **{selected_shipment}**")
            
            # Show shipment details
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {ship_data['type']}")
                st.write(f"**Origin:** {ship_data['origin_country']}")
                st.write(f"**Destination:** {ship_data['destination_country']}")
            with col2:
                st.write(f"**Status:** {ship_data['status']}")
                st.write(f"**Client:** {ship_data['client_email']}")
                st.write(f"**Departure:** {ship_data['departure_date']}")
            
            st.markdown("---")
            
            confirm = st.checkbox("I confirm I want to delete this shipment")
            
            if st.button("🗑️ Delete Shipment", type="primary", disabled=not confirm):
                try:
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM shipments WHERE id=%s', (int(ship_data['id']),))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Shipment {selected_shipment} deleted successfully!")
                    _safe_rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting shipment: {str(e)}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

elif page == "💬 Messages":
    st.header("💬 Messages")
    st.markdown("### Communication between Clients and Employees")
    
    try:
        current_user = st.session_state['user']
        user_id = current_user['id']
        user_role = current_user.get('role', 'client')
        
        # Create tabs for Inbox and Send Message
        tab1, tab2 = st.tabs(["📥 Inbox", "✉️ Send Message"])
        
        with tab1:
            # Display messages
            st.markdown("#### Your Messages")
            
            messages_df = db.get_user_messages(user_id)
            
            if len(messages_df) == 0:
                st.info("📭 No messages yet.")
            else:
                # Show unread count
                unread_count = db.get_unread_count(user_id)
                if unread_count > 0:
                    st.warning(f"📬 You have {unread_count} unread message(s)")
                
                for idx, msg in messages_df.iterrows():
                    # Determine if this is sent or received
                    is_received = msg['to_user_id'] == user_id
                    
                    # Create expandable message
                    with st.expander(
                        f"{'📬' if is_received and msg['is_read'] == 0 else '📭'} "
                        f"{'From' if is_received else 'To'}: {msg['from_email'] if is_received else msg['to_email']} - "
                        f"{msg['subject']} ({msg['created_at']})"
                    ):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Subject:** {msg['subject']}")
                            st.markdown(f"**From:** {msg['from_email']}")
                            st.markdown(f"**To:** {msg['to_email']}")
                            if msg['shipment_number']:
                                st.markdown(f"**Shipment:** {msg['shipment_number']}")
                            st.markdown(f"**Date:** {msg['created_at']}")
                            st.markdown("---")
                            st.markdown(f"**Message:**")
                            st.write(msg['content'])
                        
                        with col2:
                            if is_received and msg['is_read'] == 0:
                                if st.button("✓ Mark as Read", key=f"read_{msg['id']}"):
                                    db.mark_message_read(msg['id'])
                                    st.rerun()
                            
                            # Reply button
                            if st.button("↩️ Reply", key=f"reply_{msg['id']}"):
                                st.session_state['reply_to'] = {
                                    'email': msg['from_email'] if is_received else msg['to_email'],
                                    'subject': f"Re: {msg['subject']}",
                                    'shipment_id': msg.get('shipment_id')
                                }
                                st.rerun()
        
        with tab2:
            st.markdown("#### Send New Message")
            
            # Get list of users to send to
            if user_role == 'client':
                # Clients can send to employees
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, email FROM users WHERE role IN ('employee', 'manager')")
                users = cursor.fetchall()
                conn.close()
            else:
                # Employees can send to clients
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, email FROM users WHERE role='client'")
                users = cursor.fetchall()
                conn.close()
            
            if len(users) == 0:
                st.warning("No users available to send messages to.")
            else:
                with st.form("send_message_form"):
                    # Check if replying
                    if 'reply_to' in st.session_state:
                        reply_data = st.session_state['reply_to']
                        to_email = st.text_input("To:", value=reply_data['email'], disabled=True)
                        # Find user ID from email
                        to_user = next((u for u in users if u[1] == reply_data['email']), None)
                        to_user_id = to_user[0] if to_user else users[0][0]
                        subject = st.text_input("Subject:", value=reply_data['subject'])
                        
                        # Clear reply state after form
                        del st.session_state['reply_to']
                    else:
                        user_emails = [u[1] for u in users]
                        to_email = st.selectbox("To:", user_emails)
                        to_user_id = next((u[0] for u in users if u[1] == to_email), users[0][0])
                        subject = st.text_input("Subject:")
                    
                    # Optional: Select shipment
                    if user_role == 'client':
                        client_shipments = db.get_shipments_by_client(user_id)
                        if len(client_shipments) > 0:
                            shipment_options = ["None"] + client_shipments['shipment_number'].tolist()
                            selected_shipment = st.selectbox("Related Shipment (optional):", shipment_options)
                            shipment_id = None
                            if selected_shipment != "None":
                                shipment_id = client_shipments[client_shipments['shipment_number'] == selected_shipment]['id'].iloc[0]
                        else:
                            shipment_id = None
                    else:
                        shipment_id = None
                    
                    content = st.text_area("Message:", height=200)
                    
                    submit = st.form_submit_button("📤 Send Message")
                    
                    if submit:
                        if not subject or not content:
                            st.error("Please fill in subject and message content.")
                        else:
                            if db.send_message(user_id, to_user_id, subject, content, shipment_id):
                                st.success("✅ Message sent successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Error sending message.")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>EIMS | Company Data Management System</p>
    </div>
    """,
    unsafe_allow_html=True
)

