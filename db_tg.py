import sqlite3

conn = sqlite3.connect("patients.db", check_same_thread=False)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    surname TEXT,
    age INTEGER,
    date TEXT
)
''')
conn.commit()

def add_patients(name, surname, age, date):
    cur.execute('INSERT INTO patients (name, surname, age, date) VALUES (?, ?, ?, ?)', (name, surname, age, date)
                )
    conn.commit()

def get_patients():
    cur.execute('SELECT id, name, surname, age, date FROM patients')
    return cur.fetchall()

def update_date(patient_id, new_date):
    cur.execute('UPDATE patients SET date = ? WHERE id = ?'), (new_date, patient_id)
    conn.commit()
