"""
Spark Configuration for VinylDB Analytics
Provides Spark session management and PostgreSQL connectivity
"""

from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class SparkManager:
    """Manages Spark session lifecycle and configuration"""
    
    _instance: Optional[SparkSession] = None
    
    @classmethod
    def get_spark_session(cls) -> SparkSession:
        """Get or create Spark session with PostgreSQL support"""
        if cls._instance is None:
            # Get database URL from environment
            database_url = os.getenv("DATABASE_URL")
            
            # Parse PostgreSQL connection details
            # Format: postgresql+asyncpg://user:pass@host:port/dbname
            if database_url:
                # Remove the asyncpg part for JDBC
                jdbc_url = database_url.replace("postgresql+asyncpg://", "jdbc:postgresql://")
                # Remove SSL mode if present
                if "?" in jdbc_url:
                    jdbc_url = jdbc_url.split("?")[0]
            else:
                raise ValueError("DATABASE_URL environment variable not set")
            
            # Configure Spark
            conf = SparkConf()
            conf.setAppName("VinylDB Analytics")
            conf.set("spark.driver.memory", "2g")
            conf.set("spark.executor.memory", "2g")
            conf.set("spark.sql.adaptive.enabled", "true")
            conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
            
            # Create Spark session
            cls._instance = (
                SparkSession.builder
                .config(conf=conf)
                .getOrCreate()
            )
            
            # Set log level to reduce noise
            cls._instance.sparkContext.setLogLevel("WARN")
            
        return cls._instance
    
    @classmethod
    def stop_spark_session(cls):
        """Stop the Spark session"""
        if cls._instance is not None:
            cls._instance.stop()
            cls._instance = None
    
    @classmethod
    def get_jdbc_properties(cls) -> dict:
        """Get JDBC connection properties from DATABASE_URL"""
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Parse the URL
        # Format: postgresql+asyncpg://user:pass@host:port/dbname?sslmode=require
        url_parts = database_url.replace("postgresql+asyncpg://", "").split("@")
        
        if len(url_parts) != 2:
            raise ValueError("Invalid DATABASE_URL format")
        
        # Extract credentials
        credentials = url_parts[0].split(":")
        user = credentials[0]
        password = credentials[1] if len(credentials) > 1 else ""
        
        # Extract host, port, and database
        host_parts = url_parts[1].split("/")
        host_port = host_parts[0].split(":")
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"
        
        # Extract database name (remove query params)
        db_name = host_parts[1].split("?")[0] if len(host_parts) > 1 else ""
        
        # Build JDBC URL
        jdbc_url = f"jdbc:postgresql://{host}:{port}/{db_name}"
        
        return {
            "url": jdbc_url,
            "user": user,
            "password": password,
            "driver": "org.postgresql.Driver",
            "ssl": "true",
            "sslmode": "require"
        }


def get_spark() -> SparkSession:
    """Convenience function to get Spark session"""
    return SparkManager.get_spark_session()
