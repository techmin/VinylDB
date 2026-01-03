"""
Download PostgreSQL JDBC driver for Spark
"""
import urllib.request
import os

jdbc_url = "https://jdbc.postgresql.org/download/postgresql-42.7.1.jar"
output_path = os.path.join(os.path.dirname(__file__), "postgresql-42.7.1.jar")

print(f"Downloading PostgreSQL JDBC driver...")
print(f"From: {jdbc_url}")
print(f"To: {output_path}")

urllib.request.urlretrieve(jdbc_url, output_path)

print(f"✓ Downloaded successfully!")
print(f"File size: {os.path.getsize(output_path)} bytes")
