"""
Analytics Engine for VinylDB using Apache Spark
Provides scalable data aggregation and metrics for vinyl collection visualization
Designed for production multi-user deployment
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from typing import Dict, List, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class SparkAnalyticsEngine:
    """Spark-based analytics engine for vinyl collection metrics"""
    
    def __init__(self):
        """Initialize Spark session and load data"""
        self.spark = self._get_spark_session()
        self.jdbc_properties = self._get_jdbc_properties()
        
    def _get_spark_session(self) -> SparkSession:
        """Get or create Spark session"""
        spark = (
            SparkSession.builder
            .appName("VinylDB Analytics")
            .config("spark.driver.memory", "2g")
            .config("spark.executor.memory", "2g")
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.driver.extraClassPath", os.path.join(os.path.dirname(__file__), "postgresql-42.7.1.jar"))
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("WARN")
        return spark
    
    def _get_jdbc_properties(self) -> dict:
        """Get JDBC connection properties from DATABASE_URL"""
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Parse the URL: postgresql+asyncpg://user:pass@host:port/dbname?sslmode=require
        url_clean = database_url.replace("postgresql+asyncpg://", "")
        
        # Split credentials and host
        if "@" in url_clean:
            creds, host_db = url_clean.split("@", 1)
            user, password = creds.split(":", 1) if ":" in creds else (creds, "")
        else:
            raise ValueError("Invalid DATABASE_URL format")
        
        # Split host/port and database
        if "/" in host_db:
            host_port, db_params = host_db.split("/", 1)
            db_name = db_params.split("?")[0]  # Remove query params
        else:
            raise ValueError("Invalid DATABASE_URL format")
        
        # Extract host and port
        if ":" in host_port:
            host, port = host_port.split(":", 1)
        else:
            host, port = host_port, "5432"
        
        jdbc_url = f"jdbc:postgresql://{host}:{port}/{db_name}"
        
        return {
            "url": jdbc_url,
            "user": user,
            "password": password,
            "driver": "org.postgresql.Driver",
            "ssl": "true",
            "sslmode": "require"
        }
    
    def _load_vinyls_df(self) -> DataFrame:
        """Load vinyls table as Spark DataFrame"""
        try:
            df = (
                self.spark.read
                .format("jdbc")
                .option("url", self.jdbc_properties["url"])
                .option("dbtable", "vinyls")
                .option("user", self.jdbc_properties["user"])
                .option("password", self.jdbc_properties["password"])
                .option("driver", self.jdbc_properties["driver"])
                .load()
            )
            return df
        except Exception as e:
            # Fallback: create empty DataFrame with schema if connection fails
            print(f"Warning: Could not load data from database: {e}")
            from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
            schema = StructType([
                StructField("id", IntegerType(), True),
                StructField("title", StringType(), True),
                StructField("artist", StringType(), True),
                StructField("year", IntegerType(), True),
                StructField("genre", StringType(), True),
                StructField("cat_no", StringType(), True),
                StructField("created_at", TimestampType(), True)
            ])
            return self.spark.createDataFrame([], schema)
    
    async def get_collection_overview(self) -> Dict[str, Any]:
        """Get overall collection statistics using Spark"""
        df = self._load_vinyls_df()
        
        # Calculate aggregates
        total_vinyls = df.count()
        total_artists = df.select("artist").filter(F.col("artist").isNotNull()).distinct().count()
        total_genres = df.select("genre").filter(F.col("genre").isNotNull()).distinct().count()
        
        # Year range
        year_stats = df.agg(
            F.min("year").alias("oldest"),
            F.max("year").alias("newest")
        ).collect()[0]
        
        # Recent additions
        recent_df = (
            df.orderBy(F.col("created_at").desc())
            .limit(5)
            .select("id", "title", "artist", "year", "created_at")
        )
        
        recent_additions = [
            {
                "id": row.id,
                "title": row.title,
                "artist": row.artist,
                "year": row.year,
                "added_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in recent_df.collect()
        ]
        
        return {
            "total_vinyls": total_vinyls,
            "total_artists": total_artists,
            "total_genres": total_genres,
            "year_range": {
                "oldest": year_stats.oldest,
                "newest": year_stats.newest
            },
            "recent_additions": recent_additions
        }
    
    async def get_artist_distribution(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top artists by vinyl count using Spark"""
        df = self._load_vinyls_df()
        
        artist_counts = (
            df.filter(F.col("artist").isNotNull())
            .groupBy("artist")
            .agg(F.count("id").alias("count"))
            .orderBy(F.col("count").desc())
            .limit(limit)
        )
        
        return [
            {"artist": row.artist, "count": row.count}
            for row in artist_counts.collect()
        ]
    
    async def get_genre_distribution(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get genre distribution using Spark"""
        df = self._load_vinyls_df()
        
        genre_counts = (
            df.filter(F.col("genre").isNotNull())
            .groupBy("genre")
            .agg(F.count("id").alias("count"))
            .orderBy(F.col("count").desc())
            .limit(limit)
        )
        
        return [
            {"genre": row.genre, "count": row.count}
            for row in genre_counts.collect()
        ]
    
    async def get_year_distribution(self) -> List[Dict[str, Any]]:
        """Get vinyl distribution by decade using Spark"""
        df = self._load_vinyls_df()
        
        # Calculate decade and aggregate
        decade_counts = (
            df.filter(F.col("year").isNotNull())
            .withColumn("decade", (F.floor(F.col("year") / 10) * 10).cast("int"))
            .groupBy("decade")
            .agg(F.count("id").alias("count"))
            .orderBy("decade")
        )
        
        return [
            {"decade": f"{row.decade}s", "count": row.count}
            for row in decade_counts.collect()
        ]
    
    async def get_collection_timeline(self) -> List[Dict[str, Any]]:
        """Get collection growth over time using Spark"""
        df = self._load_vinyls_df()
        
        # Group by month
        monthly_counts = (
            df.withColumn("month", F.date_trunc("month", F.col("created_at")))
            .groupBy("month")
            .agg(F.count("id").alias("added"))
            .orderBy("month")
        )
        
        # Calculate cumulative total using window function
        window_spec = Window.orderBy("month").rowsBetween(Window.unboundedPreceding, Window.currentRow)
        timeline_df = monthly_counts.withColumn("total", F.sum("added").over(window_spec))
        
        return [
            {
                "month": row.month.isoformat() if row.month else None,
                "added": row.added,
                "total": row.total
            }
            for row in timeline_df.collect()
        ]
    
    async def search_analytics(self, query: str) -> Dict[str, Any]:
        """Get analytics for search results using Spark"""
        df = self._load_vinyls_df()
        
        query_lower = query.lower()
        
        # Filter matches
        matches_df = df.filter(
            F.lower(F.col("title")).contains(query_lower) |
            F.lower(F.col("artist")).contains(query_lower) |
            F.lower(F.col("genre")).contains(query_lower)
        )
        
        total_matches = matches_df.count()
        
        # Count matches by field
        title_matches = matches_df.filter(F.lower(F.col("title")).contains(query_lower)).count()
        artist_matches = matches_df.filter(F.lower(F.col("artist")).contains(query_lower)).count()
        genre_matches = matches_df.filter(F.lower(F.col("genre")).contains(query_lower)).count()
        
        return {
            "total_matches": total_matches,
            "matches_by_field": {
                "title": title_matches,
                "artist": artist_matches,
                "genre": genre_matches
            }
        }
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data using Spark"""
        return {
            "overview": await self.get_collection_overview(),
            "top_artists": await self.get_artist_distribution(),
            "genre_distribution": await self.get_genre_distribution(),
            "year_distribution": await self.get_year_distribution(),
            "collection_timeline": await self.get_collection_timeline(),
            "generated_at": datetime.utcnow().isoformat(),
            "engine": "Apache Spark"
        }
    
    def __del__(self):
        """Cleanup: Note that Spark session is shared and should not be stopped here"""
        pass


