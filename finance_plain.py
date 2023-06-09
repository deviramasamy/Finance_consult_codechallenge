rom pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from datetime import datetime
import uuid
from delta import *

spark = SparkSession.builder \
    .appName("myApp") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()


# Read the CSV file into a DataFrame
df = spark.read.format("csv").option("header", "true").load(file_path)
#df = spark.read.option("header", "true").csv(input_path)
print(df.show(5))
#print("file read")

# Add the ingestion timestamp and batch ID as new columns to the DataFrame
ingestion_tms = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
batch_id = str(uuid.uuid4())
df_with_extras = df.withColumn("ingestion_tms", lit(ingestion_tms)).withColumn("batch_id", lit(batch_id))
print(df_with_extras.show(5))

# Create or replace table with path and add properties
DeltaTable.createOrReplace(spark) \
  .addColumn("id", "INT") \
  .addColumn("company", "STRING") \
  .addColumn("last_name", "STRING") \
  .addColumn("first_name", "STRING", comment = "surname") \
  .addColumn("phone", "INT") \
  .addColumn("address", "STRING") \
  .addColumn("city_and_state", "STRING") \
  .addColumn("postal_code", "INT") \
  .addColumn("country", "STRING") \
  .addColumn("ingestion_tms", "TIMESTAMP") \
  .addColumn("batch_id", "STRING") \
  .property("description", "table with amended data") \
  .location("/default/delta-table") \
  .execute()

# Write the DataFrame to DeltaLake using APPEND mode
output_path = "/tmp/delta-table"
#output_path = "/delta/output"
#df_with_extras.write.mode("append").format("delta").save(output_path)
df_with_extras.write.mode("append").format("delta").saveAsTable("output_path")
print(output_path)


# Stop the Spark session
spark.stop()
