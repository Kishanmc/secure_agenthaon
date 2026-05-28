# App Settings
import os

DEBUG = True
PORT = 8080

# VULNERABLE: Hardcoded credential
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE/qAwE129381283hjasdhf/AWS"
DATABASE_URL = "postgresql://db_user:password123@localhost/prod_db"
