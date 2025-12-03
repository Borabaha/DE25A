"""
Pipeline 2: Payment Behavior & Installment Analysis (Lab Style)

"""

from pathlib import Path

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    sum,
    count,
    avg,
    countDistinct,
    min,
    max,
    date_format,
    year,
    month,
    dayofweek,
    hour,
    desc,
    lag,
    when,
)
from pyspark.sql.window import Window


def main() -> None:
   
    # STEP 0: IMPORTS + SPARK SESSION
 
    sparkConf = SparkConf()
    
    # uncomment: sparkConf.setMaster("spark://spark-master:7077")
    sparkConf.setAppName("Pipeline2_PaymentAnalysis")


    spark = SparkSession.builder.master("yarn").config(conf=sparkConf).getOrCreate()


    # Step 2: GCS Configuration for BigQuery
  
    #  from: Lab 7 Lab7_4.ipynb
    # Use the Cloud Storage bucket for temporary BigQuery export data used by the connector.


    bucket = "assingment2-processed-data"  
    spark.conf.set("temporaryGcsBucket", bucket)

    # from Lab 7 Lab7_4.ipynb 
    # Setup hadoop fs configuration for schema gs://
    conf = spark.sparkContext._jsc.hadoopConfiguration()
    conf.set("fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    conf.set(
        "fs.AbstractFileSystem.gs.impl",
        "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
    )

  
    # STEP 1: LOAD DATA (Lab 7 Lab7_3.ipynb CSV reader)
    # Lab 7 Lab7_5.ipynb -  GCS file path
    print("Step 1: Loading datasets from Google Cloud Storage...")

    # Load data from GCS (for Dataproc)
    orders = spark.read.format("csv")\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .load("gs://assingment2-raw-data/olist_orders_dataset.csv")

    payments = spark.read.format("csv")\
        .option("header", "true")\
        .option("inferSchema", "true")\
        .load("gs://assingment2-raw-data/olist_order_payments_dataset.csv")

    """
    # Local development paths (for Docker/local runs)
    base_data_path = Path("/home/jovyan/data/sample")
    orders = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(str(base_data_path / "olist_orders_dataset.csv"))
    )

    payments = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load(str(base_data_path / "olist_order_payments_dataset.csv"))
    )
    """

    print(f"Orders rows: {orders.count()}")
    print(f"Payments rows: {payments.count()}")

    # Quick schema peek (Lab 7 habit: print schema + a few rows)
    orders.printSchema()
    payments.printSchema()
    orders.show(5)
    payments.show(5)

    # STEP 2: CLEAN DATA (Lab 8 BasicDF filters)
    # Similar Lab 8 BasicDF_1.ipynb (`where`, `isin`, comparison ops)
    print("Filtering valid orders + payments...")

    orders_clean = orders.where(
        col("order_status").isin(["delivered", "invoiced", "shipped"])
    )

    payments_clean = payments.where(col("payment_value") > 0)

    print(f"Clean orders: {orders_clean.count()}")
    print(f"Clean payments: {payments_clean.count()}")

   
    # STEP 3: SINGLE JOIN (Lab 8 AdvancedDF join)
    
    print("Joining orders with payments on order_id (single join)...")

    full_data = orders_clean.join(
        payments_clean,
        "order_id",
        "inner",
    )

    print(f"Joined rows: {full_data.count()}")
    full_data.select("order_id", "payment_type", "payment_value").show(5)

   
    # STEP 4: TIME FEATURES (Lab 8 BasicDF_2 date functions)
    print("Deriving year/month/day/hour columns...")

    full_data = (
        full_data.withColumn(
            "year_month",
            date_format(col("order_purchase_timestamp"), "yyyy-MM"),
        )
        .withColumn(
            "year",
            year(col("order_purchase_timestamp")),
        )
        .withColumn(
            "month",
            month(col("order_purchase_timestamp")),
        )
        .withColumn(
            "day_of_week",
            dayofweek(col("order_purchase_timestamp")),
        )
        .withColumn(
            "hour",
            hour(col("order_purchase_timestamp")),
        )
    )

    full_data.select("order_id", "year_month", "day_of_week", "hour").show(5)

  
    # STEP 5: PAYMENT RANGE + INSTALLMENT LABELS (Lab 8 when/otherwise)
  
    )

    full_data = (
        full_data.withColumn(
            "payment_range",
            when(col("payment_value") < 50, "0-50")
            .when(
                (col("payment_value") >= 50) & (col("payment_value") < 100),
                "50-100",
            )
            .when(
                (col("payment_value") >= 100) & (col("payment_value") < 200),
                "100-200",
            )
            .when(
                (col("payment_value") >= 200) & (col("payment_value") < 500),
                "200-500",
            )
            .otherwise("500+"),
        )
        .withColumn(
            "installment_category",
            when(col("payment_installments") == 1, "Single Payment")
            .when(
                (col("payment_installments") >= 2)
                & (col("payment_installments") <= 3),
                "2-3 Installments",
            )
            .when(
                (col("payment_installments") >= 4)
                & (col("payment_installments") <= 6),
                "4-6 Installments",
            )
            .when(
                (col("payment_installments") >= 7)
                & (col("payment_installments") <= 12),
                "7-12 Installments",
            )
            .otherwise("12+ Installments"),
        )
        .withColumn(
            "monthly_installment_amount",
            col("payment_value") / col("payment_installments"),
        )
    )

    full_data.select(
        "order_id",
        "payment_range",
        "installment_category",
        "monthly_installment_amount",
    ).show(5)

    # STEP 6: PAYMENT TYPE SUMMARY (Lab 8 AdvancedDF groupBy + agg)
    # from: Lab 8 
    
    print("Aggregation 1 → payment type distribution...")

    payment_types = (
        full_data.groupBy("payment_type")
        .agg(
            count("*").alias("transaction_count"),
            countDistinct("order_id").alias("unique_orders"),
            sum("payment_value").alias("total_value"),
            avg("payment_value").alias("avg_value"),
            min("payment_value").alias("min_value"),
            max("payment_value").alias("max_value"),
            avg("payment_installments").alias("avg_installments"),
        )
        .orderBy(desc("transaction_count"))
    )

    payment_types.show(truncate=False)

   
    # STEP 7: MONTHLY PAYMENT TRENDS (Lab 8 multi-column groupBy)
    # Ffrom Lab 8 AdvancedDF aggregation on InvoiceNo + CustomerId
    
    print("Aggregation 2 → monthly payment trends by type...")

    monthly_payments = (
        full_data.groupBy("year_month", "payment_type")
        .agg(
            count("*").alias("transaction_count"),
            sum("payment_value").alias("total_value"),
            avg("payment_value").alias("avg_value"),
            avg("payment_installments").alias("avg_installments"),
        )
        .orderBy("year_month", "payment_type")
    )

    monthly_payments.show(20, truncate=False)

    
    # STEP 8: INSTALLMENT PATTERNS (Lab 8 groupBy + agg)
    #  from: Lab 8 multi-key aggregation examples
    print("Aggregation 3 → installment behavior by payment range...")

    installment_patterns = (
        full_data.groupBy("payment_range", "installment_category")
        .agg(
            count("*").alias("transaction_count"),
            avg("payment_installments").alias("avg_installments"),
            sum("payment_value").alias("total_value"),
            avg("payment_value").alias("avg_value"),
        )
        .orderBy("payment_range", "installment_category")
    )

    installment_patterns.show(20, truncate=False)

    
    # STEP 9: TEMPORAL PATTERNS (Lab 8 aggregations)
    # Similarfrom: Lab 8 hourly grouping demos
    
    print("Aggregation 4 → hourly payment behavior per type...")

    hourly_patterns = (
        full_data.groupBy("hour", "payment_type")
        .agg(
            count("*").alias("transaction_count"),
            avg("payment_value").alias("avg_value"),
        )
        .orderBy("hour", "payment_type")
    )

    hourly_patterns.show(24, truncate=False)

    
    # STEP 10: CASH FLOW ESTIMATE (Lab 8 sum over groupBy)
    # Simiilar to Lab 8 revenue aggregation + derived columns

    print("Aggregation 5 → monthly cash flow (order value vs. installment inflow)...")

    cash_flow = (
        full_data.groupBy("year_month", "payment_type")
        .agg(
            sum("payment_value").alias("total_order_value"),
            sum("monthly_installment_amount").alias(
                "estimated_monthly_cash_inflow"
            ),
            count("*").alias("transaction_count"),
            avg("payment_installments").alias("avg_installments"),
        )
        .orderBy("year_month", "payment_type")
    )

    cash_flow.show(20, truncate=False)

    # STEP 11: WINDOW FUNCTIONS (running totals + moving averages)
    # from: Lab 8 AdvancedDF window spec + rowsBetween(-2, 0)
   
    print("Window 1 → cumulative + 3-month moving average per payment_type...")

    window_spec = Window.partitionBy("payment_type").orderBy("year_month")
    window_moving = (
        Window.partitionBy("payment_type")
        .orderBy("year_month")
        .rowsBetween(-2, 0)
    )

    payment_trends = (
        monthly_payments.withColumn(
            "cumulative_value",
            sum("total_value").over(window_spec),
        ).withColumn(
            "moving_avg_3month",
            avg("total_value").over(window_moving),
        )
    )

    payment_trends.show(20, truncate=False)

    #Lab 8 AdvancedDF lag() growth calculation
    print("Window 2 → month-over-month growth by payment_type...")

    window_lag = Window.partitionBy("payment_type").orderBy("year_month")

    payment_growth = payment_trends.withColumn(
        "prev_month_value",
        lag("total_value", 1).over(window_lag),
    ).withColumn(
        "growth_rate",
        ((col("total_value") - col("prev_month_value")) / col("prev_month_value") * 100),
    )

    payment_growth.select(
        "year_month",
        "payment_type",
        "total_value",
        "prev_month_value",
        "growth_rate",
    ).show(20, truncate=False)


    
    # STEP 14: WRITE TO BIGQUERY (Lab 7 Lab7_4)
    # Lab 7 BigQuery connector example (table + temporary bucket)
    
    print("\nStep 11: Writing results to BigQuery...")

    # Pattern: Lab 7 Lab7_4.ipynb - write.format('bigquery').option('table', ...).mode("overwrite").save()
    payment_types.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.payment_type_summary"
    ).mode("overwrite").save()

    print("✓ Written: payment_type_summary")

    monthly_payments.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.payment_monthly_trends"
    ).mode("overwrite").save()

    print("✓ Written: payment_monthly_trends")

    installment_patterns.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.installment_patterns"
    ).mode("overwrite").save()

    print("✓ Written: installment_patterns")

    hourly_patterns.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.hourly_payment_patterns"
    ).mode("overwrite").save()

    print("✓ Written: hourly_payment_patterns")

    cash_flow.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.payment_cash_flow"
    ).mode("overwrite").save()

    print("✓ Written: payment_cash_flow")

    payment_growth.write.format("bigquery").option(
        "table", "de25a2.olist_analytics.payment_growth_trends"
    ).mode("overwrite").save()

    print("✓ Written: payment_growth_trends")

   
    print("\nPipeline 2 completed successfully!")
    print("Summary:")
    print(f"  - Processed {full_data.count()} payment transactions")
    print(f"  - Analyzed {payment_types.count()} payment types")
    print(f"  - Generated monthly, hourly, and installment pattern metrics")

    # Stop the Spark context
    spark.stop()


if __name__ == "__main__":
    main()


