"""
Pipeline 1: Product Category Sales Performance

"""

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    sum,
    count,
    avg,
    countDistinct,
    date_format,
    year,
    month,
    quarter,
    desc,
    rank,
    percent_rank,
    lag,
    when,
)
from pyspark.sql.window import Window


def main() -> None:
    sparkConf = SparkConf()
 #   sparkConf.setMaster("spark://spark-master:7077")  # Docker Spark cluster master URL
    sparkConf.setAppName("Pipeline1_CategorySalesPerformance")
    # Optional: Uncomment for local development
    # sparkConf.set("spark.driver.memory", "2g")
    # sparkConf.set("spark.executor.cores", "1")
    # sparkConf.set("spark.driver.cores", "1")

    
    #Lab 7 dataproc_example.py
    spark = SparkSession.builder.config(conf=sparkConf).getOrCreate()


    # Use the Cloud Storage bucket for temporary BigQuery export data used by the connector.
    bucket = "assingment2-processed-data"  # use your bucket - must exist in GCP
    spark.conf.set("temporaryGcsBucket", bucket)


    # Setup hadoop fs configuration for schema gs://
    conf = spark.sparkContext._jsc.hadoopConfiguration()
    conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    conf.set(
        "fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
    )

   
    # Step 3: Load Data from GCS / local
    
    
    orders = spark.read.format("csv")\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .load("gs://assingment2-raw-data/olist_orders_dataset.csv")

    order_items = spark.read.format("csv")\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .load("gs://assingment2-raw-data/olist_order_items_dataset.csv")

    products = spark.read.format("csv")\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .load("gs://assingment2-raw-data/olist_products_dataset.csv")

    category_translation = spark.read.format("csv")\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .load("gs://assingment2-raw-data/product_category_name_translation.csv")

    print(f"Orders loaded: {orders.count()} records")
    print(f"Order items loaded: {order_items.count()} records")
    print(f"Products loaded: {products.count()} records")
    """

    # Local development paths (from notebook)
    orders = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load("/home/jovyan/data/olist_orders_dataset.csv")
    )

    order_items = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load("/home/jovyan/data/olist_order_items_dataset.csv")
    )

    products = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load("/home/jovyan/data/olist_products_dataset.csv")
    )

    category_translation = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load("/home/jovyan/data/product_category_name_translation.csv")
    )"""

    
    print("\nStep 2: Cleaning data...")

    # Pattern: Lab 7 dataproc_example.py - df.where(df.Country == "France")
    orders_clean = orders.where(orders.order_status == "delivered")

    # Pattern: Lab 7 - using col() and isNotNull() for null filtering
    order_items_clean = order_items.where(
        col("order_id").isNotNull()
        & col("product_id").isNotNull()
        & col("price").isNotNull()
    )

    products_clean = products.where(col("product_category_name").isNotNull())

    print(f"Clean orders: {orders_clean.count()}")
    print(f"Clean order items: {order_items_clean.count()}")

    # Step 5: Join Operations

    print("\nStep 3: Joining datasets...")

    # Join 1: Order items with products
   
    items_products = order_items_clean.join(
        products_clean,
        "product_id",
        "left",
    )

    # Join 2: Add category translation (English names)
    # Lab 8 AdvancedDF.ipynb
    items_category = items_products.join(
        category_translation,
        items_products.product_category_name
        == category_translation.product_category_name,
        "left",
    )

    # Select only the columns we need
   
    items_category = items_category.select(
        items_products["order_id"],
        items_products["product_id"],
        items_products["price"],
        items_products["freight_value"],
        items_products["product_category_name"],
        category_translation.product_category_name_english.alias("category"),
    )

    # Join 3: Add order timestamps
    # Lab 8 - inner join to get only matching records
    full_data = items_category.join(
        orders_clean.select("order_id", "order_purchase_timestamp"),
        "order_id",
        "inner",
    )

    print(f"Final joined dataset: {full_data.count()} records")
    full_data.show(5)

   
    print("\nStep 4: Creating time-based features...")

    # Lab 8 - date_format() function
    full_data = full_data.withColumn(
        "year_month",
        date_format(col("order_purchase_timestamp"), "yyyy-MM"),
    )

    # Lab 8 - year(), quarter() functions
    full_data = full_data.withColumn("year", year(col("order_purchase_timestamp")))
    full_data = full_data.withColumn(
        "quarter",
        quarter(col("order_purchase_timestamp")),
    )

    #  Lab 8 - column arithmetic operations
    full_data = full_data.withColumn(
        "total_revenue",
        col("price") + col("freight_value"),
    )

    #Lab 8 - when/otherwise for conditional logic
    full_data = full_data.withColumn(
        "category_final",
        when(col("category").isNull(), col("product_category_name")).otherwise(
            col("category")
        ),
    )

    full_data.select("order_id", "category_final", "year_month", "total_revenue").show(
        5
    )

    # Step 7: Aggregations - Monthly Category Sales

    print("\nStep 5: Aggregating monthly category sales...")

    monthly_category_sales = full_data.groupBy("year_month", "category_final").agg(
        sum("total_revenue").alias("total_revenue"),
        count("order_id").alias("total_orders"),
        avg("price").alias("avg_price"),
        sum("freight_value").alias("total_freight"),
        countDistinct("order_id").alias("unique_orders"),
        countDistinct("product_id").alias("unique_products"),
    )

    #Lab 8 - orderBy() with desc() for descending order
    monthly_category_sales = monthly_category_sales.orderBy(
        "year_month", desc("total_revenue")
    )

    print(
        f"Monthly category sales aggregated: {monthly_category_sales.count()} records"
    )
    monthly_category_sales.show(20)

    # Step 8: Aggregations - Top Categories Overall

    print("Step 6: Calculating overall top categories")

    top_categories = (
        full_data.groupBy("category_final")
        .agg(
            sum("total_revenue").alias("total_revenue"),
            count("*").alias("total_items_sold"),
            countDistinct("order_id").alias("unique_orders"),
            avg("price").alias("avg_price"),
            countDistinct("product_id").alias("unique_products"),
        )
        .orderBy(desc("total_revenue"))
    )

    print(f"Top categories calculated: {top_categories.count()} categories")
    print("\n=== TOP 10 CATEGORIES ===")
    top_categories.show(10, truncate=False)

   
    # Step 9: Window Functions - Category Rankings
    print("\nStep 7: Calculating category rankings using window functions...")

    # Lab 8 AdvancedDF.ipynb (Cell 26) - Window.partitionBy().orderBy()
    windowSpec = Window.partitionBy("year_month").orderBy(desc("total_revenue"))

    # Lab 8 AdvancedDF.ipynb (Cell 28) - rank() and percent_rank() over window
    monthly_ranked = monthly_category_sales.withColumn(
        "rank_in_month",
        rank().over(windowSpec),
    ).withColumn(
        "revenue_percentile",
        percent_rank().over(windowSpec),
    )

    print("Category rankings calculated")
    print("\n=== TOP 5 CATEGORIES PER MONTH ===")
    monthly_ranked.where(col("rank_in_month") <= 5).orderBy(
        "year_month", "rank_in_month"
    ).show(50, truncate=False)

    # Step 10: Window Functions - Moving Averages
    print("\nStep 8: Calculating 3-month moving averages...")

    # Lab 8 AdvancedDF.ipynb - rowsBetween(-2, 0) means current row and 2 previous
    windowMoving = (
        Window.partitionBy("category_final")
        .orderBy("year_month")
        .rowsBetween(-2, 0)
    )

    # Lab 8 - avg() over window with rowsBetween
    monthly_trends = monthly_ranked.withColumn(
        "revenue_3month_avg",
        avg("total_revenue").over(windowMoving),
    ).withColumn(
        "orders_3month_avg",
        avg("total_orders").over(windowMoving),
    )

    print("Moving averages calculated")
    # Show example for one category
    monthly_trends.where(col("category_final") == "furniture_decor").orderBy(
        "year_month"
    ).show(20, truncate=False)

    # Step 11: Window Functions - Growth Rate
    
    print("\nStep 9: Calculating month-over-month growth rates...")

    # Lab 8 - Window.partitionBy().orderBy() for lag operations
    windowLag = Window.partitionBy("category_final").orderBy("year_month")

    # Lab 8 - lag() to get previous value, then calculate percentage change
    monthly_growth = monthly_trends.withColumn(
        "prev_month_revenue",
        lag("total_revenue", 1).over(windowLag),
    ).withColumn(
        "growth_rate",
        ((col("total_revenue") - col("prev_month_revenue")) / col("prev_month_revenue"))
        * 100,
    )

    print("Growth rates calculated")
    print("\n=== HIGH GROWTH CATEGORIES (Last Month) ===")
    monthly_growth.where(col("growth_rate") > 50).orderBy(
        desc("growth_rate")
    ).show(20, truncate=False)

  
    # Step 12: Quarterly Aggregation
    print("\nStep 10: Aggregating quarterly sales...")

    quarterly_sales = (
        full_data.groupBy("year", "quarter", "category_final")
        .agg(
            sum("total_revenue").alias("total_revenue"),
            count("order_id").alias("total_orders"),
            avg("price").alias("avg_price"),
        )
        .orderBy("year", "quarter", desc("total_revenue"))
    )

    print(f"Quarterly sales aggregated: {quarterly_sales.count()} records")
    quarterly_sales.show(20)

    # Step 13: Write Results to BigQuery
    # Form file Lab 7 Lab7_4.ipynb 
    print("\nStep 11: Writing results to BigQuery...")

    #Lab 7 Lab7_4.ipynb - write.format('bigquery').option('table', ...).mode("overwrite").save()
    monthly_growth.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.category_monthly_performance"
    ).mode("overwrite").save()

    print("✓ Written: category_monthly_performance")

    top_categories.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.category_overall_performance"
    ).mode("overwrite").save()

    print("✓ Written: category_overall_performance")

    quarterly_sales.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.category_quarterly_sales"
    ).mode("overwrite").save()

    print("✓ Written: category_quarterly_sales")


    print("\nPipeline 1 completed successfully!")
    

    # Stop the Spark context
    spark.stop()


if __name__ == "__main__":
    main()


