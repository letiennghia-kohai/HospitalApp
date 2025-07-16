import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime
import re
from tkcalendar import DateEntry

class MedicalRecordsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Bệnh án")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Khởi tạo database
        self.init_database()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Load dữ liệu ban đầu
        self.load_patients()
        self.update_stats()
        
        # Biến lưu trữ thông tin bệnh nhân được chọn
        self.selected_patient_id = None
        self.selected_patient_name = None
    
    def init_database(self):
        """Khởi tạo database và tạo bảng"""
        self.conn = sqlite3.connect('patients.db')
        self.cursor = self.conn.cursor()
        
        # Tạo bảng bệnh nhân
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                birth_date TEXT,
                gender TEXT,
                phone TEXT,
                address TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tạo bảng bệnh án
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_date TEXT,
                diagnosis TEXT,
                symptoms TEXT,
                treatment TEXT,
                notes TEXT,
                doctor_id INTEGER,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        ''')
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS test_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                test_type_id INTEGER NOT NULL,
                result TEXT,
                test_date TEXT,
                notes TEXT,
                FOREIGN KEY (record_id) REFERENCES medical_records(id),
                FOREIGN KEY (test_type_id) REFERENCES test_types(id)
            )
        ''')
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS medicine_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')    
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                dosage TEXT,            -- liều dùng (ví dụ: "1 viên sáng + 1 viên tối")
                quantity INTEGER,       -- số lượng
                instructions TEXT,      -- hướng dẫn dùng
                FOREIGN KEY (record_id) REFERENCES medical_records(id),
                FOREIGN KEY (medicine_id) REFERENCES medicine_types(id)
            )
        ''')    
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')    
        self.conn.commit()
    
    def create_widgets(self):
        """Tạo giao diện chính"""
        # Tạo notebook (tab container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Quản lý bệnh nhân
        self.patient_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.patient_frame, text="Quản lý Bệnh nhân")
        self.create_patient_tab()
        
        # Tab 2: Quản lý bệnh án
        self.record_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.record_frame, text="Quản lý Bệnh án")
        self.create_record_tab()
        
        # Tab 3: Xem chi tiết bệnh án
        self.detail_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.detail_frame, text="Chi tiết Bệnh án")
        self.create_detail_tab()
        
        # Tab 5: Quản lý loại xét nghiệm
        self.test_type_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.test_type_frame, text="Quản lý Loại Xét nghiệm")
        self.create_test_type_tab()
        
        # Tab 6: Quản lý loại thuốc
        self.medicine_type_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.medicine_type_frame, text="Quản lý Loại Thuốc")
        self.create_medicine_type_tab()
        
        # Tab 4: Thống kê
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Thống kê")
        self.create_stats_tab()
    
    def create_patient_tab(self):
        """Tạo tab quản lý bệnh nhân"""
        # Frame chứa form nhập liệu
        form_frame = ttk.LabelFrame(self.patient_frame, text="Thông tin bệnh nhân", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # Tạo form nhập liệu
        ttk.Label(form_frame, text="Họ tên:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.patient_name = ttk.Entry(form_frame, width=30)
        self.patient_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Ngày sinh:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.patient_birth = DateEntry(form_frame, 
                                    width=12,
                                    background='darkblue',
                                    foreground='white', 
                                    borderwidth=2,
                                    date_pattern='dd/mm/yyyy')
        self.patient_birth.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Giới tính:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.patient_gender = ttk.Combobox(form_frame, values=['Nam', 'Nữ'], width=27)
        self.patient_gender.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Số điện thoại:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.patient_phone = ttk.Entry(form_frame, width=15)
        self.patient_phone.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Địa chỉ:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.patient_address = ttk.Entry(form_frame, width=70)
        self.patient_address.grid(row=2, column=1, columnspan=4, padx=5, pady=5, sticky='ew')
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=5, pady=10)
        
        ttk.Button(button_frame, text="Thêm BN", command=self.add_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_patient).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Làm mới", command=self.clear_patient_form).pack(side='left', padx=5)
        
        # Tìm kiếm
        search_frame = ttk.LabelFrame(self.patient_frame, text="Tìm kiếm", padding=10)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Họ và tên:").pack(side='left')
        self.search_patient = ttk.Entry(search_frame, width=30)
        self.search_patient.pack(side='left', padx=5)
        self.search_patient.bind('<KeyRelease>', self.search_patients)
        
        # Danh sách bệnh nhân
        list_frame = ttk.LabelFrame(self.patient_frame, text="Danh sách bệnh nhân", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview
        columns = ('ID', 'Họ tên', 'Ngày sinh', 'Giới tính', 'Số ĐT', 'Địa chỉ')
        self.patient_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Định nghĩa cột
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.patient_tree.yview)
        self.patient_tree.configure(yscrollcommand=scrollbar.set)
        
        self.patient_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind events
        self.patient_tree.bind('<Double-1>', self.on_patient_select_and_navigate)
        self.patient_tree.bind('<ButtonRelease-1>', self.on_patient_select)


    def on_patient_select_and_navigate(self, event):
        """Xử lý khi double click vào bệnh nhân - chuyển sang tab bệnh án"""
        selection = self.patient_tree.selection()
        if selection:
            item = self.patient_tree.item(selection[0])
            patient_data = item['values']
            
            if patient_data:
                patient_id = patient_data[0]
                patient_name = patient_data[1]
                
                # Lưu thông tin bệnh nhân được chọn
                self.selected_patient_id = patient_id
                self.selected_patient_name = patient_name
                
                # Chuyển sang tab bệnh án
                self.notebook.select(1)
                
                # Cập nhật thông tin bệnh nhân trong tab bệnh án
                self.update_medical_record_patient_info(patient_id, patient_name)
                
                # Set combobox
                self.record_patient_combo.set(f"{patient_id} - {patient_name}")
                
                # Load bệnh án của bệnh nhân này
                self.load_patient_medical_records(patient_id)
    def update_medical_record_patient_info(self, patient_id, patient_name):
        """Cập nhật thông tin bệnh nhân trong tab bệnh án"""
        if hasattr(self, 'current_patient_label'):
            self.current_patient_label.config(text=f"Bệnh nhân: {patient_name} (ID: {patient_id})")
        
        if hasattr(self, 'detail_patient_info'):
            # Lấy thông tin chi tiết bệnh nhân
            try:
                self.cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
                patient_info = self.cursor.fetchone()
                if patient_info:
                    info_text = f"Bệnh nhân: {patient_info[1]} | Ngày sinh: {patient_info[2]} | Giới tính: {patient_info[3]} | SĐT: {patient_info[4]} | Địa chỉ: {patient_info[5]}"
                    self.detail_patient_info.config(text=info_text)
            except Exception as e:
                print(f"Lỗi khi cập nhật thông tin bệnh nhân: {e}")

    # Hàm load bệnh án của bệnh nhân
    def load_patient_medical_records(self, patient_id):
        """Load danh sách bệnh án của bệnh nhân"""
        # Xóa dữ liệu cũ trong treeview bệnh án
        if hasattr(self, 'medical_record_tree'):
            for item in self.medical_record_tree.get_children():
                self.medical_record_tree.delete(item)
        
        # Load bệnh án từ database
        try:
            self.cursor.execute("""
                SELECT 
                    id, 
                    visit_date, 
                    diagnosis, 
                    symptoms, 
                    treatment, 
                    prescription, 
                    doctor_name, 
                    notes
                FROM 
                    medical_records
                WHERE 
                    patient_id = ?
                ORDER BY 
                    visit_date DESC
            """, (patient_id,))
            
            records = self.cursor.fetchall()
            
            # Thêm dữ liệu vào treeview
            for record in records:
                self.medical_record_tree.insert('', 'end', values=record)
                
        except Exception as e:
            print(f"Lỗi khi load bệnh án: {e}")

    # Hàm xử lý khi chọn bệnh nhân (để fill form)
    def on_patient_select(self, event):
        """Xử lý khi chọn bệnh nhân để fill form"""
        selection = self.patient_tree.selection()
        if selection:
            item = self.patient_tree.item(selection[0])
            patient_data = item['values']
            
            if patient_data:
                # Clear form trước
                self.clear_patient_form()
                
                # Fill dữ liệu vào form
                self.patient_name.insert(0, patient_data[1])
                
                # Chuyển đổi ngày sinh từ string sang datetime cho DateEntry
                try:
                    birth_date = datetime.strptime(patient_data[2], '%d/%m/%Y')
                    self.patient_birth.set_date(birth_date)
                except:
                    pass
                
                self.patient_gender.set(patient_data[3])
                self.patient_phone.insert(0, patient_data[4])
                self.patient_address.insert(0, patient_data[5])

    # Hàm clear form với DateEntry
    def clear_patient_form(self):
        """Xóa dữ liệu trong form"""
        self.patient_name.delete(0, 'end')
        self.patient_birth.set_date(datetime.now())  # Set về ngày hiện tại
        self.patient_gender.set('')
        self.patient_phone.delete(0, 'end')
        self.patient_address.delete(0, 'end')
    def create_record_tab(self):
        """Tạo tab quản lý bệnh án với bố cục hợp lý hơn"""
        # Frame chọn bệnh nhân
        patient_select_frame = ttk.LabelFrame(self.record_frame, text="Chọn bệnh nhân", padding=10)
        patient_select_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(patient_select_frame, text="Bệnh nhân:").pack(side='left')
        self.record_patient_combo = ttk.Combobox(patient_select_frame, width=50, state='readonly')
        self.record_patient_combo.pack(side='left', padx=5)
        self.record_patient_combo.bind('<<ComboboxSelected>>', self.on_patient_combo_select)
        
        ttk.Button(patient_select_frame, text="Tải lại DS", command=self.load_patient_combo).pack(side='left', padx=5)
        
        self.current_patient_label = ttk.Label(patient_select_frame, text="Chưa chọn bệnh nhân", 
                                             font=('Arial', 10, 'bold'), foreground='blue')
        self.current_patient_label.pack(side='left', padx=20)
        
        # Frame form bệnh án với Notebook
        record_form_frame = ttk.LabelFrame(self.record_frame, text="Thông tin bệnh án", padding=10)
        record_form_frame.pack(fill='x', padx=10, pady=5)
        
        # Tạo Notebook cho các tab con
        record_notebook = ttk.Notebook(record_form_frame)
        record_notebook.pack(fill='both', pady=5, expand=False)
        
        # Tab 1: Thông tin chính
        main_info_frame = ttk.Frame(record_notebook)
        record_notebook.add(main_info_frame, text="Thông tin chính")
        
        # Ngày khám và Bác sĩ
        ttk.Label(main_info_frame, text="Ngày khám:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.visit_date = DateEntry(main_info_frame, 
                                  width=12, background='darkblue', foreground='white', 
                                  borderwidth=2, date_pattern='dd/mm/yyyy')
        self.visit_date.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(main_info_frame, text="Bác sĩ:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.doctor_name = ttk.Entry(main_info_frame, width=30)
        self.doctor_name.grid(row=0, column=3, padx=5, pady=5)
        
        # Chẩn đoán
        ttk.Label(main_info_frame, text="Chẩn đoán:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.diagnosis = ttk.Entry(main_info_frame, width=60)
        self.diagnosis.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Triệu chứng
        ttk.Label(main_info_frame, text="Triệu chứng:").grid(row=2, column=0, sticky='nw', padx=5, pady=5)
        self.symptoms = scrolledtext.ScrolledText(main_info_frame, width=60, height=2)
        self.symptoms.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Điều trị
        ttk.Label(main_info_frame, text="Điều trị:").grid(row=3, column=0, sticky='nw', padx=5, pady=5)
        self.treatment = scrolledtext.ScrolledText(main_info_frame, width=60, height=2)
        self.treatment.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Ghi chú
        ttk.Label(main_info_frame, text="Ghi chú:").grid(row=4, column=0, sticky='nw', padx=5, pady=5)
        self.notes = scrolledtext.ScrolledText(main_info_frame, width=60, height=2)
        self.notes.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Tab 2: Kết quả xét nghiệm
        test_frame = ttk.Frame(record_notebook)
        record_notebook.add(test_frame, text="Kết quả xét nghiệm")
        
        # Form nhập xét nghiệm
        ttk.Label(test_frame, text="Loại xét nghiệm:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.test_type_combo = ttk.Combobox(test_frame, width=30, state='readonly')
        self.test_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(test_frame, text="Kết quả:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.test_result = ttk.Entry(test_frame, width=30)
        self.test_result.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(test_frame, text="Ghi chú:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.test_notes = ttk.Entry(test_frame, width=60)
        self.test_notes.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        test_button_frame = ttk.Frame(test_frame)
        test_button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        ttk.Button(test_button_frame, text="Thêm xét nghiệm", command=self.add_test_result).pack(side='left', padx=5)
        ttk.Button(test_button_frame, text="Xóa xét nghiệm", command=self.delete_test_result).pack(side='left', padx=5)
        
        # Treeview kết quả xét nghiệm
        test_columns = ('ID', 'Loại xét nghiệm', 'Kết quả', 'Ghi chú')
        self.test_tree = ttk.Treeview(test_frame, columns=test_columns, show='headings', height=4)
        for col in test_columns:
            self.test_tree.heading(col, text=col)
            self.test_tree.column(col, width=150)
        self.test_tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        self.test_tree.bind('<ButtonRelease-1>', self.on_test_select)
        
        # Tab 3: Đơn thuốc
        prescription_frame = ttk.Frame(record_notebook)
        record_notebook.add(prescription_frame, text="Đơn thuốc")
        
        # Form nhập đơn thuốc
        ttk.Label(prescription_frame, text="Loại thuốc:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.medicine_type_combo = ttk.Combobox(prescription_frame, width=30, state='readonly')
        self.medicine_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(prescription_frame, text="Liều lượng:").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.dosage = ttk.Entry(prescription_frame, width=20)
        self.dosage.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(prescription_frame, text="Số lượng:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.quantity = ttk.Entry(prescription_frame, width=10)
        self.quantity.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(prescription_frame, text="Hướng dẫn:").grid(row=1, column=2, sticky='w', padx=5, pady=5)
        self.instructions = ttk.Entry(prescription_frame, width=30)
        self.instructions.grid(row=1, column=3, padx=5, pady=5)
        
        prescription_button_frame = ttk.Frame(prescription_frame)
        prescription_button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        ttk.Button(prescription_button_frame, text="Thêm thuốc", command=self.add_prescription).pack(side='left', padx=5)
        ttk.Button(prescription_button_frame, text="Xóa thuốc", command=self.delete_prescription).pack(side='left', padx=5)
        
        # Treeview đơn thuốc
        prescription_columns = ('ID', 'Loại thuốc', 'Liều lượng', 'Số lượng', 'Hướng dẫn')
        self.prescription_tree = ttk.Treeview(prescription_frame, columns=prescription_columns, show='headings', height=4)
        for col in prescription_columns:
            self.prescription_tree.heading(col, text=col)
            self.prescription_tree.column(col, width=120)
        self.prescription_tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky='ew')
        self.prescription_tree.bind('<ButtonRelease-1>', self.on_prescription_select)
        
        # Buttons bệnh án
        record_button_frame = ttk.Frame(record_form_frame)
        record_button_frame.pack(fill='x', pady=10)
        
        ttk.Button(record_button_frame, text="Lưu bệnh án", command=self.save_record).pack(side='left', padx=5)
        ttk.Button(record_button_frame, text="Cập nhật", command=self.update_record).pack(side='left', padx=5)
        ttk.Button(record_button_frame, text="Xóa", command=self.delete_record).pack(side='left', padx=5)
        ttk.Button(record_button_frame, text="Làm mới", command=self.clear_record_form).pack(side='left', padx=5)
        ttk.Button(record_button_frame, text="Xem chi tiết", command=self.view_record_detail).pack(side='left', padx=5)
        
        # Danh sách bệnh án
        record_list_frame = ttk.LabelFrame(self.record_frame, text="Lịch sử khám bệnh", padding=10)
        record_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        record_columns = ('ID', 'Ngày khám', 'Chẩn đoán', 'Bác sĩ', 'Ghi chú')
        self.record_tree = ttk.Treeview(record_list_frame, columns=record_columns, show='headings', height=10)
        for col in record_columns:
            self.record_tree.heading(col, text=col)
            self.record_tree.column(col, width=120)
        
        record_scrollbar = ttk.Scrollbar(record_list_frame, orient='vertical', command=self.record_tree.yview)
        self.record_tree.configure(yscrollcommand=record_scrollbar.set)
        self.record_tree.pack(side='left', fill='both', expand=True)
        record_scrollbar.pack(side='right', fill='y')
        
        self.record_tree.bind('<Double-1>', self.on_record_select)
        # Gán sự kiện nhấp chuột trái
        self.record_tree.bind('<ButtonRelease-1>', self.on_record_select_left_click)
        
        # Load danh sách loại xét nghiệm và thuốc
        self.load_test_types()
        self.load_medicine_types()
        self.load_patient_combo()
    def on_record_select_left_click(self, event):
        """Xử lý khi nhấp chuột trái vào bệnh án: điền dữ liệu vào form và tải xét nghiệm/đơn thuốc"""
        selected = self.record_tree.selection()
        if selected:
            record_id = self.record_tree.item(selected[0])['values'][0]
            self.current_record_id = record_id  # Lưu record_id để sử dụng cho cập nhật

            # Lấy dữ liệu bệnh án
            self.cursor.execute('SELECT * FROM medical_records WHERE id=?', (record_id,))
            record = self.cursor.fetchone()
            
            if record:
                # Điền dữ liệu vào form
                self.visit_date.delete(0, tk.END)
                self.visit_date.insert(0, record[2])
                self.diagnosis.delete(0, tk.END)
                self.diagnosis.insert(0, record[3])
                self.symptoms.delete('1.0', tk.END)
                self.symptoms.insert('1.0', record[4] or '')
                self.treatment.delete('1.0', tk.END)
                self.treatment.insert('1.0', record[5] or '')
                self.notes.delete('1.0', tk.END)
                self.notes.insert('1.0', record[7] or '')
                self.doctor_name.delete(0, tk.END)
                self.doctor_name.insert(0, record[8])

                # Tải kết quả xét nghiệm và đơn thuốc
                self.load_test_results(record_id)
                self.load_prescriptions(record_id)


    def create_detail_tab(self):
        """Tạo tab xem chi tiết bệnh án"""
        patient_info_frame = ttk.LabelFrame(self.detail_frame, text="Thông tin bệnh nhân", padding=10)
        patient_info_frame.pack(fill='x', padx=10, pady=5)
        
        self.detail_patient_info = ttk.Label(patient_info_frame, text="Chưa chọn bệnh nhân", 
                                           font=('Arial', 12, 'bold'))
        self.detail_patient_info.pack(anchor='w')
        
        detail_list_frame = ttk.LabelFrame(self.detail_frame, text="Danh sách bệnh án chi tiết", padding=10)
        detail_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        detail_columns = ('ID', 'Ngày khám', 'Chẩn đoán', 'Triệu chứng', 'Điều trị', 'Bác sĩ', 'Ghi chú')
        self.medical_record_tree = ttk.Treeview(detail_list_frame, columns=detail_columns, show='headings', height=10)
        column_widths = {'ID': 50, 'Ngày khám': 100, 'Chẩn đoán': 150, 'Triệu chứng': 200, 
                        'Điều trị': 200, 'Bác sĩ': 120, 'Ghi chú': 150}
        for col in detail_columns:
            self.medical_record_tree.heading(col, text=col)
            self.medical_record_tree.column(col, width=column_widths.get(col, 100))
        
        detail_scrollbar_v = ttk.Scrollbar(detail_list_frame, orient='vertical', command=self.medical_record_tree.yview)
        detail_scrollbar_h = ttk.Scrollbar(detail_list_frame, orient='horizontal', command=self.medical_record_tree.xview)
        self.medical_record_tree.configure(yscrollcommand=detail_scrollbar_v.set, xscrollcommand=detail_scrollbar_h.set)
        self.medical_record_tree.pack(side='top', fill='both', expand=True)
        detail_scrollbar_v.pack(side='right', fill='y')
        detail_scrollbar_h.pack(side='bottom', fill='x')
        
        self.medical_record_tree.bind('<ButtonRelease-1>', self.on_medical_record_select)
        
        # Frame hiển thị chi tiết bệnh án được chọn
        selected_record_frame = ttk.LabelFrame(self.detail_frame, text="Chi tiết bệnh án được chọn", padding=10)
        selected_record_frame.pack(fill='x', padx=10, pady=5)
        
        self.selected_record_detail = scrolledtext.ScrolledText(selected_record_frame, height=8, width=100)
        self.selected_record_detail.pack(fill='x', padx=5, pady=5)
        
        # Frame kết quả xét nghiệm
        test_result_frame = ttk.LabelFrame(selected_record_frame, text="Kết quả xét nghiệm", padding=5)
        test_result_frame.pack(fill='x', padx=5, pady=5)
        
        test_result_columns = ('ID', 'Loại xét nghiệm', 'Kết quả', 'Ghi chú')
        self.detail_test_tree = ttk.Treeview(test_result_frame, columns=test_result_columns, show='headings', height=3)
        for col in test_result_columns:
            self.detail_test_tree.heading(col, text=col)
            self.detail_test_tree.column(col, width=150)
        self.detail_test_tree.pack(fill='x', padx=5, pady=5)
        
        # Frame đơn thuốc
        prescription_frame = ttk.LabelFrame(selected_record_frame, text="Đơn thuốc", padding=5)
        prescription_frame.pack(fill='x', padx=5, pady=5)
        
        prescription_columns = ('ID', 'Loại thuốc', 'Liều lượng', 'Số lượng', 'Hướng dẫn')
        self.detail_prescription_tree = ttk.Treeview(prescription_frame, columns=prescription_columns, show='headings', height=3)
        for col in prescription_columns:
            self.detail_prescription_tree.heading(col, text=col)
            self.detail_prescription_tree.column(col, width=120)
        self.detail_prescription_tree.pack(fill='x', padx=5, pady=5)
    
    
    def create_stats_tab(self):
        """Tạo tab thống kê"""
        stats_frame = ttk.Frame(self.stats_frame)
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame thống kê tổng quan
        overview_frame = ttk.LabelFrame(stats_frame, text="Thống kê tổng quan", padding=10)
        overview_frame.pack(fill='x', pady=5)
        
        # Tạo các label hiển thị thống kê
        self.total_patients_label = ttk.Label(overview_frame, text="Tổng số bệnh nhân: 0", font=('Arial', 12))
        self.total_patients_label.pack(pady=5, anchor='w')
        
        self.total_records_label = ttk.Label(overview_frame, text="Tổng số bệnh án: 0", font=('Arial', 12))
        self.total_records_label.pack(pady=5, anchor='w')
        
        self.today_records_label = ttk.Label(overview_frame, text="Bệnh án hôm nay: 0", font=('Arial', 12))
        self.today_records_label.pack(pady=5, anchor='w')
        
        self.this_month_records_label = ttk.Label(overview_frame, text="Bệnh án tháng này: 0", font=('Arial', 12))
        self.this_month_records_label.pack(pady=5, anchor='w')
        
        # Button cập nhật thống kê
        ttk.Button(overview_frame, text="Cập nhật thống kê", command=self.update_stats).pack(pady=10)
        
        # Frame thống kê theo thời gian
        time_stats_frame = ttk.LabelFrame(stats_frame, text="Thống kê theo thời gian", padding=10)
        time_stats_frame.pack(fill='both', expand=True, pady=5)
        
        # Treeview thống kê
        stats_columns = ('Tháng/Năm', 'Số bệnh nhân mới', 'Số lượt khám', 'Tổng cộng')
        self.stats_tree = ttk.Treeview(time_stats_frame, columns=stats_columns, show='headings', height=10)
        
        for col in stats_columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=120)
        
        stats_scrollbar = ttk.Scrollbar(time_stats_frame, orient='vertical', command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_tree.pack(side='left', fill='both', expand=True)
        stats_scrollbar.pack(side='right', fill='y')
        
        # Cập nhật thống kê ban đầu
        self.update_stats()
    
    def create_test_type_tab(self):
        """Tạo tab quản lý loại xét nghiệm"""
        frame = self.test_type_frame

        # Frame nhập liệu
        form_frame = ttk.LabelFrame(frame, text="Thông tin loại xét nghiệm", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Tên xét nghiệm:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.test_type_name = ttk.Entry(form_frame, width=40)
        self.test_type_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Mô tả:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.test_type_description = ttk.Entry(form_frame, width=40)
        self.test_type_description.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Thêm", command=self.add_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_test_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Làm mới", command=self.clear_test_type_form).pack(side='left', padx=5)

        # Treeview danh sách loại xét nghiệm
        list_frame = ttk.LabelFrame(frame, text="Danh sách loại xét nghiệm", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Tên xét nghiệm', 'Mô tả')
        self.test_type_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.test_type_tree.heading(col, text=col)
            self.test_type_tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.test_type_tree.yview)
        self.test_type_tree.configure(yscrollcommand=scrollbar.set)
        self.test_type_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.test_type_tree.bind('<ButtonRelease-1>', self.on_test_type_select)
        
        # Load danh sách
        self.load_test_types_list()

    def create_medicine_type_tab(self):
        """Tạo tab quản lý loại thuốc"""
        frame = self.medicine_type_frame

        # Frame nhập liệu
        form_frame = ttk.LabelFrame(frame, text="Thông tin loại thuốc", padding=10)
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Tên thuốc:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.medicine_type_name = ttk.Entry(form_frame, width=40)
        self.medicine_type_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Mô tả:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.medicine_type_description = ttk.Entry(form_frame, width=40)
        self.medicine_type_description.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Thêm", command=self.add_medicine_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_medicine_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_medicine_type).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Làm mới", command=self.clear_medicine_type_form).pack(side='left', padx=5)

        # Treeview danh sách loại thuốc
        list_frame = ttk.LabelFrame(frame, text="Danh sách loại thuốc", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('ID', 'Tên thuốc', 'Mô tả')
        self.medicine_type_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.medicine_type_tree.heading(col, text=col)
            self.medicine_type_tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.medicine_type_tree.yview)
        self.medicine_type_tree.configure(yscrollcommand=scrollbar.set)
        self.medicine_type_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.medicine_type_tree.bind('<ButtonRelease-1>', self.on_medicine_type_select)
        
        # Load danh sách
        self.load_medicine_types_list()
    def add_patient(self):
        """Thêm bệnh nhân mới"""
        name = self.patient_name.get().strip()
        birth_date = self.patient_birth.get()
        gender = self.patient_gender.get()
        phone = self.patient_phone.get().strip()
        address = self.patient_address.get().strip()

        # Kiểm tra dữ liệu đầu vào
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ tên bệnh nhân!")
            return
        if not re.match(r'^\d{10}$', phone) and phone:
            messagebox.showerror("Lỗi", "Số điện thoại không hợp lệ! (10 số)")
            return

        try:
            self.cursor.execute('''
                INSERT INTO patients (name, birth_date, gender, phone, address)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, birth_date, gender, phone, address))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm bệnh nhân thành công!")
            self.clear_patient_form()
            self.load_patients()
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm bệnh nhân: {e}")
    def on_medical_record_select(self, event):
        """Xử lý khi chọn bệnh án trong tab chi tiết"""
        selection = self.medical_record_tree.selection()
        if selection:
            item = self.medical_record_tree.item(selection[0])
            record_data = item['values']
            
            if record_data:
                detail_text = f"""
    ID: {record_data[0]}
    Ngày khám: {record_data[1]}
    Chẩn đoán: {record_data[2]}
    Triệu chứng: {record_data[3]}
    Điều trị: {record_data[4]}
    Đơn thuốc: {record_data[5]}
    Bác sĩ: {record_data[6]}
    Ghi chú: {record_data[7]}
    """
                self.selected_record_detail.delete("1.0", tk.END)
                self.selected_record_detail.insert("1.0", detail_text.strip())
    
    def update_patient(self):
        """Cập nhật thông tin bệnh nhân"""
        if not self.selected_patient_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn một bệnh nhân để cập nhật!")
            return

        name = self.patient_name.get().strip()
        birth_date = self.patient_birth.get()
        gender = self.patient_gender.get()
        phone = self.patient_phone.get().strip()
        address = self.patient_address.get().strip()

        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ tên bệnh nhân!")
            return
        if not re.match(r'^\d{10}$', phone) and phone:
            messagebox.showerror("Lỗi", "Số điện thoại không hợp lệ! (10 số)")
            return

        try:
            self.cursor.execute('''
                UPDATE patients
                SET name = ?, birth_date = ?, gender = ?, phone = ?, address = ?
                WHERE id = ?
            ''', (name, birth_date, gender, phone, address, self.selected_patient_id))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin bệnh nhân!")
            self.clear_patient_form()
            self.load_patients()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật bệnh nhân: {e}")

    # def clear_patient_form(self):
    #     """Xóa nội dung các trường nhập bệnh nhân"""
    #     self.patient_name.set("")
    #     self.patient_birth.set("")
    #     self.patient_gender.set("")
    #     self.patient_phone.set("")
    #     self.patient_address.set("")
    
    def delete_patient(self):
        """Xóa bệnh nhân"""
        if not self.selected_patient_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn một bệnh nhân để xóa!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa bệnh nhân này?"):
            try:
                # Kiểm tra xem bệnh nhân có bệnh án không
                self.cursor.execute("SELECT COUNT(*) FROM medical_records WHERE patient_id = ?", 
                                (self.selected_patient_id,))
                record_count = self.cursor.fetchone()[0]

                if record_count > 0:
                    messagebox.showerror("Lỗi", "Không thể xóa bệnh nhân vì đã có bệnh án liên quan!")
                    return

                self.cursor.execute("DELETE FROM patients WHERE id = ?", (self.selected_patient_id,))
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã xóa bệnh nhân!")
                self.clear_patient_form()
                self.load_patients()
                self.update_stats()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa bệnh nhân: {e}")
    
    def save_record(self):
        """Lưu bệnh án mới cùng với kết quả xét nghiệm và đơn thuốc"""
        if not self.validate_record_form():
            return
        
        try:
            patient_id = self.get_selected_patient_id()
            if not patient_id:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân!")
                return
            
            # Lưu bệnh án vào bảng medical_records
            self.cursor.execute('''
                INSERT INTO medical_records 
                (patient_id, visit_date, diagnosis, symptoms, treatment, notes, doctor_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                self.visit_date.get(),
                self.diagnosis.get(),
                self.symptoms.get('1.0', tk.END).strip(),
                self.treatment.get('1.0', tk.END).strip(),
                self.notes.get('1.0', tk.END).strip(),
                self.doctor_name.get()
            ))
            self.conn.commit()

            # Lấy ID của bệnh án vừa lưu
            self.cursor.execute("SELECT last_insert_rowid()")
            self.current_record_id = self.cursor.fetchone()[0]

            # Lưu kết quả xét nghiệm từ test_tree
            for item in self.test_tree.get_children():
                test_data = self.test_tree.item(item)['values']
                test_type_id = int(test_data[1].split(' - ')[0])  # Lấy test_type_id từ "ID - Tên"
                result = test_data[2]
                notes = test_data[3]
                if not result:
                    messagebox.showwarning("Cảnh báo", "Kết quả xét nghiệm không được để trống!")
                    self.conn.rollback()
                    return
                self.cursor.execute('''
                    INSERT INTO test_results (record_id, test_type_id, result, test_date, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    self.current_record_id,
                    test_type_id,
                    result,
                    self.visit_date.get(),
                    notes
                ))

            # Lưu đơn thuốc từ prescription_tree
            for item in self.prescription_tree.get_children():
                prescription_data = self.prescription_tree.item(item)['values']
                medicine_id = int(prescription_data[1].split(' - ')[0])  # Lấy medicine_id từ "ID - Tên"
                dosage = prescription_data[2]
                quantity = prescription_data[3]
                instructions = prescription_data[4]
                if not dosage or not quantity:
                    messagebox.showwarning("Cảnh báo", "Liều lượng và số lượng thuốc không được để trống!")
                    self.conn.rollback()
                    return
                try:
                    quantity = int(quantity)
                except ValueError:
                    messagebox.showwarning("Cảnh báo", "Số lượng thuốc phải là số nguyên!")
                    self.conn.rollback()
                    return
                self.cursor.execute('''
                    INSERT INTO prescriptions (record_id, medicine_id, dosage, quantity, instructions)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    self.current_record_id,
                    medicine_id,
                    dosage,
                    quantity,
                    instructions
                ))

            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã lưu bệnh án, kết quả xét nghiệm và đơn thuốc!")
            self.clear_record_form()
            
            # Cập nhật danh sách bệnh án
            self.load_records()
            self.load_medical_records(patient_id)  # Cập nhật medical_record_tree trong tab Chi tiết
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi", f"Không thể lưu bệnh án: {str(e)}")
    
    def update_record(self):
        """Cập nhật bệnh án"""
        selected = self.record_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh án để cập nhật!")
            return
        
        if not self.validate_record_form():
            return
        
        try:
            record_id = self.record_tree.item(selected[0])['values'][0]
            patient_id = self.get_selected_patient_id()
            if not patient_id:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân!")
                return
            
            # Cập nhật bệnh án trong bảng medical_records
            self.cursor.execute('''
                UPDATE medical_records 
                SET visit_date=?, diagnosis=?, symptoms=?, treatment=?, notes=?, doctor_name=?
                WHERE id=?
            ''', (
                self.visit_date.get(),
                self.diagnosis.get(),
                self.symptoms.get('1.0', tk.END).strip(),
                self.treatment.get('1.0', tk.END).strip(),
                self.notes.get('1.0', tk.END).strip(),
                self.doctor_name.get(),
                record_id
            ))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã cập nhật bệnh án!")
            self.clear_record_form()
            
            # Cập nhật danh sách bệnh án
            self.load_records()
            self.load_medical_records(patient_id)  # Cập nhật medical_record_tree trong tab Chi tiết
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")

    def delete_record(self):
        """Xóa bệnh án"""
        selected = self.record_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh án để xóa!")
            return
        
        record_id = self.record_tree.item(selected[0])['values'][0]
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân!")
            return
        
        # Kiểm tra xem bệnh án có kết quả xét nghiệm hoặc đơn thuốc không
        self.cursor.execute("SELECT COUNT(*) FROM test_results WHERE record_id = ?", (record_id,))
        test_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE record_id = ?", (record_id,))
        prescription_count = self.cursor.fetchone()[0]
        
        if test_count > 0 or prescription_count > 0:
            messagebox.showerror("Lỗi", "Không thể xóa bệnh án vì có kết quả xét nghiệm hoặc đơn thuốc liên quan!")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa bệnh án này?"):
            try:
                self.cursor.execute('DELETE FROM medical_records WHERE id=?', (record_id,))
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã xóa bệnh án!")
                self.clear_record_form()
                
                # Cập nhật danh sách bệnh án
                self.load_records()
                self.load_medical_records(patient_id)  # Cập nhật medical_record_tree trong tab Chi tiết
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {str(e)}")
    
    def load_patients(self):
        """Tải danh sách bệnh nhân vào treeview"""
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)

        try:
            self.cursor.execute("SELECT * FROM patients ORDER BY created_date DESC")
            patients = self.cursor.fetchall()
            for patient in patients:
                self.patient_tree.insert('', 'end', values=patient[0:6])
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách bệnh nhân: {e}")
    
    def load_patient_combo(self):
        """Tải danh sách bệnh nhân vào combobox"""
        self.cursor.execute('SELECT id, name FROM patients ORDER BY name')
        patients = self.cursor.fetchall()
        
        patient_list = [f"{p[0]} - {p[1]}" for p in patients]
        self.record_patient_combo['values'] = patient_list
    
    def load_records(self):
        """Tải danh sách bệnh án của bệnh nhân được chọn"""
        # Xóa dữ liệu cũ trong bảng record_tree
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)

        # Lấy ID bệnh nhân đang được chọn
        patient_id = self.get_selected_patient_id()
        if not patient_id:
            return

        # Gán ID vào biến toàn cục
        self.selected_patient_id = patient_id

        # Lấy tên bệnh nhân từ database
        self.cursor.execute("SELECT name FROM patients WHERE id = ?", (patient_id,))
        result = self.cursor.fetchone()
        self.selected_patient_name = result[0] if result else "Không rõ"

        # ✅ Cập nhật label hiển thị thông tin bệnh nhân
        # self.detail_patient_info.config(
        #     text=f"Bệnh nhân: {self.selected_patient_name} (ID: {self.selected_patient_id})"
        # )
        self.update_medical_record_patient_info(patient_id, self.selected_patient_name)
        # Truy vấn danh sách bệnh án của bệnh nhân
        self.cursor.execute('''
            SELECT id, visit_date, diagnosis, doctor_name, notes 
            FROM medical_records 
            WHERE patient_id=? 
            ORDER BY visit_date DESC
        ''', (patient_id,))
        records = self.cursor.fetchall()

        # Hiển thị các bệnh án trong treeview
        for record in records:
            self.record_tree.insert('', 'end', values=record)
    
    def search_patients(self, event=None):
        """Tìm kiếm bệnh nhân"""
        search_term = self.search_patient.get().lower()
        
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        
        if search_term:
            self.cursor.execute('''
                SELECT * FROM patients 
                WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(address) LIKE ?
                ORDER BY name
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        else:
            self.cursor.execute('SELECT * FROM patients ORDER BY name')
        
        patients = self.cursor.fetchall()
        for patient in patients:
            self.patient_tree.insert('', 'end', values=patient)
    
    def on_patient_select(self, event):
        """Xử lý khi chọn bệnh nhân"""
        selected = self.patient_tree.selection()
        if selected:
            patient_data = self.patient_tree.item(selected[0])['values']
            self.patient_name.delete(0, tk.END)
            self.patient_name.insert(0, patient_data[1])
            self.patient_birth.delete(0, tk.END)
            self.patient_birth.insert(0, patient_data[2])
            self.patient_gender.set(patient_data[3])
            self.patient_phone.delete(0, tk.END)
            self.patient_phone.insert(0, patient_data[4])
            self.patient_address.delete(0, tk.END)
            self.patient_address.insert(0, patient_data[5])
    
    def on_patient_combo_select(self, event):
        """Xử lý khi chọn bệnh nhân từ combobox"""
        self.load_records()
    
    def on_record_select(self, event):
        """Xử lý khi chọn bệnh án: chuyển sang tab Chi tiết Bệnh án và hiển thị thông tin"""
        selected = self.record_tree.selection()
        if selected:
            record_id = self.record_tree.item(selected[0])['values'][0]
            self.current_record_id = record_id  # Lưu record_id để sử dụng trong tab Chi tiết

            # Chuyển sang tab Chi tiết Bệnh án
            self.notebook.select(self.detail_frame)

            # Lấy dữ liệu bệnh án
            self.cursor.execute('SELECT * FROM medical_records WHERE id=?', (record_id,))
            record = self.cursor.fetchone()
            
            if record:
                # Cập nhật thông tin bệnh nhân
                patient_id = record[1]  # Giả định cột patient_id là cột thứ 2
                self.cursor.execute('SELECT name FROM patients WHERE id=?', (patient_id,))
                patient_name = self.cursor.fetchone()[0]
                self.detail_patient_info.config(text=f"Bệnh nhân: {patient_name}")

                # Tải danh sách bệnh án của bệnh nhân hiện tại vào medical_record_tree
                self.load_medical_records(patient_id)

                # Hiển thị chi tiết bệnh án được chọn trong selected_record_detail
                self.selected_record_detail.delete('1.0', tk.END)
                self.selected_record_detail.insert('1.0', 
                    f"ID: {record[0]}\n"
                    f"Ngày khám: {record[2]}\n"
                    f"Chẩn đoán: {record[3]}\n"
                    f"Triệu chứng: {record[4]}\n"
                    f"Điều trị: {record[5]}\n"
                    f"Bác sĩ: {record[8]}\n"
                    f"Ghi chú: {record[7]}"
                )

                # Tải kết quả xét nghiệm và đơn thuốc
                self.load_detail_test_results(record_id)
                self.load_detail_prescriptions(record_id)

                # Chọn bệnh án trong medical_record_tree
                for item in self.medical_record_tree.get_children():
                    if self.medical_record_tree.item(item)['values'][0] == record_id:
                        self.medical_record_tree.selection_set(item)
                        self.medical_record_tree.focus(item)
                        break
    def load_medical_records(self, patient_id):
        """Tải danh sách bệnh án của bệnh nhân vào medical_record_tree"""
        for item in self.medical_record_tree.get_children():
            self.medical_record_tree.delete(item)
        try:
            self.cursor.execute('''
                SELECT id, visit_date, diagnosis, symptoms, treatment, doctor_name, notes
                FROM medical_records
                WHERE patient_id = ?
            ''', (patient_id,))
            records = self.cursor.fetchall()
            for record in records:
                self.medical_record_tree.insert('', 'end', values=record)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách bệnh án: {e}")
    def get_selected_patient_id(self):
        """Lấy ID bệnh nhân được chọn"""
        selected_text = self.record_patient_combo.get()
        if selected_text:
            return int(selected_text.split(' - ')[0])
        return None
    
    def validate_patient_form(self):
        """Validate form bệnh nhân"""
        if not self.patient_name.get().strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên bệnh nhân!")
            return False
        
        # Validate ngày sinh (optional)
        birth_date = self.patient_birth.get().strip()
        if birth_date and not re.match(r'^\d{2}/\d{2}/\d{4}$', birth_date):
            messagebox.showwarning("Cảnh báo", "Ngày sinh không đúng định dạng (dd/mm/yyyy)!")
            return False
        
        # Validate số điện thoại (optional)
        phone = self.patient_phone.get().strip()
        if phone and not re.match(r'^\d{10,11}$', phone):
            messagebox.showwarning("Cảnh báo", "Số điện thoại không hợp lệ!")
            return False
        
        return True
    
    def validate_record_form(self):
        """Validate form bệnh án"""

        if not self.diagnosis.get().strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập chẩn đoán!")
            return False

        visit_date = self.visit_date.get().strip()
        if not visit_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập ngày khám!")
            return False

        if not re.match(r'^\d{2}/\d{2}/\d{4}$', visit_date):
            messagebox.showwarning("Cảnh báo", "Ngày khám không đúng định dạng (dd/mm/yyyy)!")
            return False

        try:
            datetime.strptime(visit_date, "%d/%m/%Y")  # ✅ dùng đúng hàm
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Ngày khám không hợp lệ!")
            return False

        return True
    def clear_patient_form(self):
        """Xóa nội dung form bệnh nhân"""
        self.patient_name.delete(0, tk.END)
        self.patient_birth.delete(0, tk.END)
        self.patient_gender.set('')
        self.patient_phone.delete(0, tk.END)
        self.patient_address.delete(0, tk.END)
        self.search_patient.delete(0, tk.END)
        
        # Clear selection trong treeview
        for item in self.patient_tree.selection():
            self.patient_tree.selection_remove(item)
    
    def clear_record_form(self):
        """Xóa dữ liệu trong form bệnh án"""
        self.visit_date.delete(0, tk.END)
        self.diagnosis.delete(0, tk.END)
        self.symptoms.delete('1.0', tk.END)
        self.treatment.delete('1.0', tk.END)
        self.notes.delete('1.0', tk.END)
        self.doctor_name.delete(0, tk.END)
        self.test_result.delete(0, tk.END)
        self.test_notes.delete(0, tk.END)
        self.dosage.delete(0, tk.END)
        self.quantity.delete(0, tk.END)
        self.instructions.delete(0, tk.END)
        if self.test_type_combo['values']:
            self.test_type_combo.set(self.test_type_combo['values'][0])
        if self.medicine_type_combo['values']:
            self.medicine_type_combo.set(self.medicine_type_combo['values'][0])
        self.test_tree.delete(*self.test_tree.get_children())
        self.prescription_tree.delete(*self.prescription_tree.get_children())
        self.current_record_id = None
    
    def view_record_detail(self):
        """Chuyển sang tab chi tiết bệnh án"""
        if not self.selected_patient_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn một bệnh nhân!")
            return
        self.notebook.select(2)
        self.update_medical_record_patient_info(self.selected_patient_id, self.selected_patient_name)
        self.load_patient_medical_records(self.selected_patient_id)
    
    def update_stats(self):
        """Cập nhật thống kê tổng quan và theo thời gian"""
        try:
            # Tổng số bệnh nhân
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            total_patients = self.cursor.fetchone()[0]
            self.total_patients_label.config(text=f"Tổng số bệnh nhân: {total_patients}")

            # Tổng số bệnh án
            self.cursor.execute("SELECT COUNT(*) FROM medical_records")
            total_records = self.cursor.fetchone()[0]
            self.total_records_label.config(text=f"Tổng số bệnh án: {total_records}")

            # Bệnh án hôm nay
            today = datetime.now().strftime('%d/%m/%Y')
            self.cursor.execute("SELECT COUNT(*) FROM medical_records WHERE visit_date = ?", (today,))
            today_records = self.cursor.fetchone()[0]
            self.today_records_label.config(text=f"Bệnh án hôm nay: {today_records}")

            # Bệnh án tháng này
            current_month = datetime.now().strftime('%m/%Y')
            self.cursor.execute("SELECT COUNT(*) FROM medical_records WHERE strftime('%m/%Y', visit_date) = ?", (current_month,))
            month_records = self.cursor.fetchone()[0]
            self.this_month_records_label.config(text=f"Bệnh án tháng này: {month_records}")

            # Thống kê theo tháng/năm
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)

            self.cursor.execute("""
                SELECT 
                    strftime('%m/%Y', created_date) as month_year,
                    COUNT(DISTINCT id) as new_patients,
                    (SELECT COUNT(*) FROM medical_records WHERE strftime('%m/%Y', visit_date) = strftime('%m/%Y', patients.created_date)) as visits
                FROM patients
                GROUP BY month_year
                ORDER BY month_year DESC
            """)
            stats = self.cursor.fetchall()
            for stat in stats:
                total = stat[1] + stat[2]
                self.stats_tree.insert('', 'end', values=(stat[0], stat[1], stat[2], total))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thống kê: {e}")
    def load_test_types(self):
        """Tải danh sách loại xét nghiệm"""
        try:
            self.cursor.execute("SELECT id, name FROM test_types")
            test_types = self.cursor.fetchall()
            self.test_type_combo['values'] = [f"{t[0]} - {t[1]}" for t in test_types]
            if test_types:
                self.test_type_combo.set(f"{test_types[0][0]} - {test_types[0][1]}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải loại xét nghiệm: {e}")

    def load_medicine_types(self):
        """Tải danh sách loại thuốc"""
        try:
            self.cursor.execute("SELECT id, name FROM medicine_types")
            medicines = self.cursor.fetchall()
            self.medicine_type_combo['values'] = [f"{m[0]} - {m[1]}" for m in medicines]
            if medicines:
                self.medicine_type_combo.set(f"{medicines[0][0]} - {medicines[0][1]}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải loại thuốc: {e}")

    def add_test_result(self):
        """Thêm kết quả xét nghiệm vào test_tree"""
        test_type = self.test_type_combo.get()
        result = self.test_result.get().strip()
        notes = self.test_notes.get().strip()
        
        if not test_type or not result:
            messagebox.showerror("Lỗi", "Vui lòng nhập loại xét nghiệm và kết quả!")
            return
        
        try:
            # Thêm vào test_tree với ID tạm thời (sẽ được cập nhật khi lưu vào DB)
            self.test_tree.insert('', 'end', values=(
                'TEMP',  # ID tạm thời
                test_type,  # Lưu cả "ID - Tên" để sử dụng trong save_record
                result,
                notes
            ))
            messagebox.showinfo("Thành công", "Đã thêm kết quả xét nghiệm vào danh sách tạm thời!")
            self.clear_test_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm xét nghiệm: {e}")

    def delete_test_result(self):
        """Xóa kết quả xét nghiệm"""
        selection = self.test_tree.selection()
        if not selection:
            messagebox.showerror("Lỗi", "Vui lòng chọn một xét nghiệm để xóa!")
            return
        
        test_id = self.test_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa xét nghiệm này?"):
            try:
                self.cursor.execute("DELETE FROM test_results WHERE id = ?", (test_id,))
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã xóa xét nghiệm!")
                self.load_test_results(self.current_record_id)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa xét nghiệm: {e}")

    def add_prescription(self):
        """Thêm đơn thuốc vào prescription_tree"""
        medicine_type = self.medicine_type_combo.get()
        dosage = self.dosage.get().strip()
        quantity = self.quantity.get().strip()
        instructions = self.instructions.get().strip()
        
        if not medicine_type or not dosage or not quantity:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin đơn thuốc!")
            return
        
        try:
            quantity = int(quantity)  # Kiểm tra số lượng là số nguyên
            # Thêm vào prescription_tree với ID tạm thời (sẽ được cập nhật khi lưu vào DB)
            self.prescription_tree.insert('', 'end', values=(
                'TEMP',  # ID tạm thời
                medicine_type,  # Lưu cả "ID - Tên" để sử dụng trong save_record
                dosage,
                quantity,
                instructions
            ))
            messagebox.showinfo("Thành công", "Đã thêm đơn thuốc vào danh sách tạm thời!")
            self.clear_prescription_form()
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng phải là số nguyên!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm đơn thuốc: {e}")

    def delete_prescription(self):
        """Xóa đơn thuốc"""
        selection = self.prescription_tree.selection()
        if not selection:
            messagebox.showerror("Lỗi", "Vui lòng chọn một đơn thuốc để xóa!")
            return
        
        prescription_id = self.prescription_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa đơn thuốc này?"):
            try:
                self.cursor.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,))
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã xóa đơn thuốc!")
                self.load_prescriptions(self.current_record_id)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa đơn thuốc: {e}")

    def load_test_results(self, record_id):
        """Tải danh sách kết quả xét nghiệm"""
        for item in self.test_tree.get_children():
            self.test_tree.delete(item)
        try:
            self.cursor.execute('''
                SELECT tr.id, tt.name, tr.result, tr.notes
                FROM test_results tr
                JOIN test_types tt ON tr.test_type_id = tt.id
                WHERE tr.record_id = ?
            ''', (record_id,))
            tests = self.cursor.fetchall()
            for test in tests:
                self.test_tree.insert('', 'end', values=test)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải kết quả xét nghiệm: {e}")

    def load_prescriptions(self, record_id):
        """Tải danh sách đơn thuốc"""
        for item in self.prescription_tree.get_children():
            self.prescription_tree.delete(item)
        try:
            self.cursor.execute('''
                SELECT p.id, mt.name, p.dosage, p.quantity, p.instructions
                FROM prescriptions p
                JOIN medicine_types mt ON p.medicine_id = mt.id
                WHERE p.record_id = ?
            ''', (record_id,))
            prescriptions = self.cursor.fetchall()
            for prescription in prescriptions:
                self.prescription_tree.insert('', 'end', values=prescription)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải đơn thuốc: {e}")

    def clear_test_form(self):
        """Làm mới form xét nghiệm"""
        self.test_result.delete(0, tk.END)
        self.test_notes.delete(0, tk.END)
        if self.test_type_combo['values']:
            self.test_type_combo.set(self.test_type_combo['values'][0])

    def clear_prescription_form(self):
        """Làm mới form đơn thuốc"""
        self.dosage.delete(0, tk.END)
        self.quantity.delete(0, tk.END)
        self.instructions.delete(0, tk.END)
        if self.medicine_type_combo['values']:
            self.medicine_type_combo.set(self.medicine_type_combo['values'][0])

    def on_test_select(self, event):
        """Xử lý khi chọn kết quả xét nghiệm"""
        selection = self.test_tree.selection()
        if selection:
            item = self.test_tree.item(selection[0])
            test_data = item['values']
            self.clear_test_form()
            self.test_type_combo.set(f"{test_data[0]} - {test_data[1]}")
            self.test_result.insert(0, test_data[2])
            self.test_notes.insert(0, test_data[3])

    def on_prescription_select(self, event):
        """Xử lý khi chọn đơn thuốc"""
        selection = self.prescription_tree.selection()
        if selection:
            item = self.prescription_tree.item(selection[0])
            prescription_data = item['values']
            self.clear_prescription_form()
            self.medicine_type_combo.set(f"{prescription_data[0]} - {prescription_data[1]}")
            self.dosage.insert(0, prescription_data[2])
            self.quantity.insert(0, prescription_data[3])
            self.instructions.insert(0, prescription_data[4])

    def on_medical_record_select(self, event):
        """Xử lý khi chọn bệnh án từ medical_record_tree trong tab Chi tiết Bệnh án"""
        selected = self.medical_record_tree.selection()
        if selected:
            record_id = self.medical_record_tree.item(selected[0])['values'][0]
            self.current_record_id = record_id

            # Lấy dữ liệu bệnh án
            self.cursor.execute('SELECT * FROM medical_records WHERE id=?', (record_id,))
            record = self.cursor.fetchone()
            
            if record:
                # Cập nhật chi tiết bệnh án trong selected_record_detail
                self.selected_record_detail.delete('1.0', tk.END)
                self.selected_record_detail.insert('1.0', 
                    f"ID: {record[0]}\n"
                    f"Ngày khám: {record[2]}\n"
                    f"Chẩn đoán: {record[3]}\n"
                    f"Triệu chứng: {record[4]}\n"
                    f"Điều trị: {record[5]}\n"
                    f"Bác sĩ: {record[8]}\n"
                    f"Ghi chú: {record[7]}"
                )

                # Tải kết quả xét nghiệm và đơn thuốc
                self.load_detail_test_results(record_id)
                self.load_detail_prescriptions(record_id)

    def load_detail_test_results(self, record_id):
        """Tải kết quả xét nghiệm cho tab Chi tiết Bệnh án"""
        for item in self.detail_test_tree.get_children():
            self.detail_test_tree.delete(item)
        try:
            self.cursor.execute('''
                SELECT tr.id, tt.name, tr.result, tr.notes
                FROM test_results tr
                JOIN test_types tt ON tr.test_type_id = tt.id
                WHERE tr.record_id = ?
            ''', (record_id,))
            tests = self.cursor.fetchall()
            for test in tests:
                self.detail_test_tree.insert('', 'end', values=test)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải kết quả xét nghiệm: {e}")

    def load_detail_prescriptions(self, record_id):
        """Tải đơn thuốc cho tab Chi tiết Bệnh án"""
        for item in self.detail_prescription_tree.get_children():
            self.detail_prescription_tree.delete(item)
        try:
            self.cursor.execute('''
                SELECT p.id, mt.name, p.dosage, p.quantity, p.instructions
                FROM prescriptions p
                JOIN medicine_types mt ON p.medicine_id = mt.id
                WHERE p.record_id = ?
            ''', (record_id,))
            prescriptions = self.cursor.fetchall()
            for prescription in prescriptions:
                self.detail_prescription_tree.insert('', 'end', values=prescription)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải đơn thuốc: {e}")

    # def save_record(self):
    #     """Lưu bệnh án mới"""
    #     if not self.selected_patient_id:
    #         messagebox.showerror("Lỗi", "Vui lòng chọn một bệnh nhân!")
    #         return

    #     visit_date = self.visit_date.get()
    #     diagnosis = self.diagnosis.get().strip()
    #     symptoms = self.symptoms.get("1.0", tk.END).strip()
    #     treatment = self.treatment.get("1.0", tk.END).strip()
    #     notes = self.notes.get("1.0", tk.END).strip()
    #     doctor_name = self.doctor_name.get().strip()

    #     if not diagnosis:
    #         messagebox.showerror("Lỗi", "Vui lòng nhập chẩn đoán!")
    #         return

    #     try:
    #         self.cursor.execute('''
    #             INSERT INTO medical_records (patient_id, visit_date, diagnosis, symptoms, treatment, 
    #                                       notes, doctor_name)
    #             VALUES (?, ?, ?, ?, ?, ?, ?)
    #         ''', (self.selected_patient_id, visit_date, diagnosis, symptoms, treatment, 
    #               notes, doctor_name))
    #         self.conn.commit()
    #         self.current_record_id = self.cursor.lastrowid
    #         messagebox.showinfo("Thành công", "Đã lưu bệnh án!")
    #         self.clear_record_form()
    #         self.load_patient_medical_records(self.selected_patient_id)
    #         self.update_stats()
    #     except Exception as e:
    #         messagebox.showerror("Lỗi", f"Không thể lưu bệnh án: {e}")

    def add_test_type(self):
        """Thêm loại xét nghiệm"""
        name = self.test_type_name.get().strip()
        description = self.test_type_description.get().strip()

        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên xét nghiệm!")
            return

        try:
            self.cursor.execute('''
                INSERT INTO test_types (name, description)
                VALUES (?, ?)
            ''', (name, description))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm loại xét nghiệm!")
            self.clear_test_type_form()
            self.load_test_types_list()
            self.load_test_types()  # Cập nhật combobox trong tab bệnh án
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm loại xét nghiệm: {e}")

    def update_test_type(self):
        """Cập nhật loại xét nghiệm"""
        selection = self.test_type_tree.selection()
        if not selection:
            messagebox.showerror("Lỗi", "Vui lòng chọn một loại xét nghiệm để cập nhật!")
            return

        test_type_id = self.test_type_tree.item(selection[0])['values'][0]
        name = self.test_type_name.get().strip()
        description = self.test_type_description.get().strip()

        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên xét nghiệm!")
            return

        try:
            self.cursor.execute('''
                UPDATE test_types
                SET name = ?, description = ?
                WHERE id = ?
            ''', (name, description, test_type_id))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã cập nhật loại xét nghiệm!")
            self.clear_test_type_form()
            self.load_test_types_list()
            self.load_test_types()  # Cập nhật combobox trong tab bệnh án
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật loại xét nghiệm: {e}")

    def delete_test_type(self):
        """Xóa loại xét nghiệm"""
        selection = self.test_type_tree.selection()
        if not selection:
            messagebox.showerror("Lỗi", "Vui lòng chọn một loại xét nghiệm để xóa!")
            return

        test_type_id = self.test_type_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa loại xét nghiệm này?"):
            try:
                # Kiểm tra xem loại xét nghiệm có được sử dụng trong test_results
                self.cursor.execute("SELECT COUNT(*) FROM test_results WHERE test_type_id = ?", (test_type_id,))
                if self.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Lỗi", "Không thể xóa vì loại xét nghiệm này đang được sử dụng!")
                    return

                self.cursor.execute("DELETE FROM test_types WHERE id = ?", (test_type_id,))
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã xóa loại xét nghiệm!")
                self.clear_test_type_form()
                self.load_test_types_list()
                self.load_test_types()  # Cập nhật combobox trong tab bệnh án
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa loại xét nghiệm: {e}")

    def clear_test_type_form(self):
        """Làm mới form loại xét nghiệm"""
        self.test_type_name.delete(0, tk.END)
        self.test_type_description.delete(0, tk.END)

    def on_test_type_select(self, event):
        """Xử lý khi chọn loại xét nghiệm từ treeview"""
        selection = self.test_type_tree.selection()
        if selection:
            item = self.test_type_tree.item(selection[0])
            test_type_data = item['values']
            self.clear_test_type_form()
            self.test_type_name.insert(0, test_type_data[1])
            self.test_type_description.insert(0, test_type_data[2])

    def load_test_types_list(self):
        """Tải danh sách loại xét nghiệm"""
        for item in self.test_type_tree.get_children():
            self.test_type_tree.delete(item)
        try:
            self.cursor.execute("SELECT id, name, description FROM test_types")
            test_types = self.cursor.fetchall()
            for test_type in test_types:
                self.test_type_tree.insert('', 'end', values=test_type)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách loại xét nghiệm: {e}")

    def add_medicine_type(self):
        """Thêm loại thuốc"""
        name = self.medicine_type_name.get().strip()
        description = self.medicine_type_description.get().strip()

        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên thuốc!")
            return

        try:
            self.cursor.execute('''
                INSERT INTO medicine_types (name, description)
                VALUES (?, ?)
            ''', (name, description))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã thêm loại thuốc!")
            self.clear_medicine_type_form()
            self.load_medicine_types_list()
            self.load_medicine_types()  # Cập nhật combobox trong tab bệnh án
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm loại thuốc: {e}")

    def update_medicine_type(self):
        """Cập nhật loại thuốc"""
        selection = self.medicine_type_tree.selection()
        if not selection:
            messagebox.showerror("Lỗi", "Vui lòng chọn một loại thuốc để cập nhật!")
            return

        medicine_type_id = self.medicine_type_tree.item(selection[0])['values'][0]
        name = self.medicine_type_name.get().strip()
        description = self.medicine_type_description.get().strip()

        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên thuốc!")
            return

        try:
            self.cursor.execute('''
                UPDATE medicine_types
                SET name = ?, description = ?
                WHERE id = ?
            ''', (name, description, medicine_type_id))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đã cập nhật loại thuốc!")
            self.clear_medicine_type_form()
            self.load_medicine_types_list()
            self.load_medicine_types()  # Cập nhật combobox trong tab bệnh án
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật loại thuốc: {e}")

    def delete_medicine_type(self):
        """Xóa loại thuốc"""
        selection = self.medicine_type_tree.selection()
        if not selection:
            messagebox.showerror("Lỗi", "Vui lòng chọn một loại thuốc để xóa!")
            return

        medicine_type_id = self.medicine_type_tree.item(selection[0])['values'][0]
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa loại thuốc này?"):
            try:
                # Kiểm tra xem loại thuốc có được sử dụng trong prescriptions
                self.cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE medicine_id = ?", (medicine_type_id,))
                if self.cursor.fetchone()[0] > 0:
                    messagebox.showerror("Lỗi", "Không thể xóa vì loại thuốc này đang được sử dụng!")
                    return

                self.cursor.execute("DELETE FROM medicine_types WHERE id = ?", (medicine_type_id,))
                self.conn.commit()
                messagebox.showinfo("Thành công", "Đã xóa loại thuốc!")
                self.clear_medicine_type_form()
                self.load_medicine_types_list()
                self.load_medicine_types()  # Cập nhật combobox trong tab bệnh án
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa loại thuốc: {e}")

    def clear_medicine_type_form(self):
        """Làm mới form loại thuốc"""
        self.medicine_type_name.delete(0, tk.END)
        self.medicine_type_description.delete(0, tk.END)

    def on_medicine_type_select(self, event):
        """Xử lý khi chọn loại thuốc từ treeview"""
        selection = self.medicine_type_tree.selection()
        if selection:
            item = self.medicine_type_tree.item(selection[0])
            medicine_type_data = item['values']
            self.clear_medicine_type_form()
            self.medicine_type_name.insert(0, medicine_type_data[1])
            self.medicine_type_description.insert(0, medicine_type_data[2])

    def load_medicine_types_list(self):
        """Tải danh sách loại thuốc"""
        for item in self.medicine_type_tree.get_children():
            self.medicine_type_tree.delete(item)
        try:
            self.cursor.execute("SELECT id, name, description FROM medicine_types")
            medicine_types = self.cursor.fetchall()
            for medicine_type in medicine_types:
                self.medicine_type_tree.insert('', 'end', values=medicine_type)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách loại thuốc: {e}")
        
    def __del__(self):
        """Đóng kết nối database khi thoát"""
        if hasattr(self, 'conn'):
            self.conn.close()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalRecordsApp(root)
    root.mainloop()