"""
Test Spark Analytics Engine
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("Testing PySpark import...")
    from pyspark.sql import SparkSession
    print("✓ PySpark imported successfully")
    
    print("\nTesting Spark session creation...")
    spark = SparkSession.builder.appName("Test").getOrCreate()
    print(f"✓ Spark session created: {spark.version}")
    
    print("\nTesting simple DataFrame...")
    data = [("Alice", 25), ("Bob", 30)]
    df = spark.createDataFrame(data, ["name", "age"])
    print(f"✓ DataFrame created with {df.count()} rows")
    
    spark.stop()
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
