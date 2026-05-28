# Authentication Module
import sqlite3

def login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # VULNERABLE: Direct SQL Injection
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    print("Executing query:", query)
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    return user
