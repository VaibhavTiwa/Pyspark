# -*- coding: utf-8 -*-
"""NYC DATA ETL PYSPARK

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14mVpKR6P6IXqT-jqPwMJiyPNIxxt2X4z
"""

!pip install pyspark

from pyspark.sql import *
spark=SparkSession.builder.master('local[*]').appName('NYC DATA PIPELINE').getOrCreate()

from google.colab import drive
drive.mount('/content/drive')
print("this is the code to  mount data from drive in colab")

data1=spark.read.parquet('/content/drive/MyDrive/yellow_tripdata_2023-01.parquet')
data1.show()

"""WE WILL SELECT SOME OF THE COLUMNS FROM THIS NOT ALL 
# **LIKE pickup_datetime", "dropoff_datetime", "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude", "passenger_count", "trip_distance", "fare_amount", "tip_amount", "total_amount").**
# ***🚛***
"""

# we are doing some change in the column name for our own use
data1.printSchema()
Extraction1=data1.withColumnRenamed('tpep_pickup_datetime','pick_up_time')\
                  .withColumnRenamed('tpep_dropoff_datetime','drop_off_time')\

Extraction1.show()

print('Picking some specific columns for our own use "pickup_longitude", "pickup_latitude", "dropoff_longitude", "dropoff_latitude", "passenger_count", "trip_distance", "fare_amount", "tip_amount", "total_amount"')

Extraction1.createOrReplaceTempView('DATA')
sql_query='''
              select VENDORID, pick_up_time,drop_off_time,passenger_count,trip_distance,
              total_amount,fare_amount,tip_amoUnt
              
              from DATA



'''
Extraction2=spark.sql(sql_query)
Extraction2.show()

"""# **CLEANING OF DATA**"""

Cleaning1=Extraction2.dropna(how='any')

Cleaning1.show()

"""# ***We will find the speed of each trip first***

# 🚄
"""

from pyspark.sql.functions import *
#to create udf and for other functions too

#creating a new columnn for to get the total trip time
# T1=Cleaning1.withColumns('total_trip_trime',(' drop_off_time')-('pick_up_time'))
print("we cant perform this as both the time stamp is string ")
T1 = Cleaning1.withColumn('pickup', to_timestamp("pick_up_time"))\
    .withColumn('drop',to_timestamp('drop_off_time'))
    


print('We have successfully changed the pick_up_time to datatime  and dropped the useless columns')
T1.printSchema()

# from pyspark.sql.functions import to_timestamp, unix_timestamp, from_unixtime

# df = df.withColumn("pickup_time", to_timestamp("pickup_time", "yyyy-MM-dd HH:mm:ss"))
# df = df.withColumn("dropoff_time", to_timestamp("dropoff_time", "yyyy-MM-dd HH:mm:ss"))

# df = df.withColumn("pickup_unix", unix_timestamp("pickup_time"))
# df = df.withColumn("dropoff_unix", unix_timestamp("dropoff_time"))



# df.select("pickup_time", "dropoff_time", "time_diff").show()
# from pyspark.sql.functions import unix_timestamp, from_unixtime, second

# # assuming T is the DataFrame containing the pickup and dropoff columns
# T1 = T.withColumn("pickup_unix", unix_timestamp(T["pickup"], "yyyy-MM-dd HH:mm:ss"))
# T2 = T1.withColumn("dropoff_unix", unix_timestamp(T1["dropoff"], "yyyy-MM-dd HH:mm:ss"))
# T3 = T2.withColumn("time_diff", T2["dropoff_unix"] - T2["pickup_unix"])
# T4 = T3.withColumn("time_diff_sec", second(from_unixtime(T3["time_diff"])))

# T4.select("time_diff_sec").show()

# T2 =T1.withColumn("timestamp_seconds", unix_timestamp(T1["pickupdate"]).cast("int"))\
 
#        #.withColumn('dropoff_unix', unix_timestamp('dropoffdate'))

# T2.show()

# # T3 = T2.withColumn("time_diff", from_unixtime(T2["dropoff_unix"] - T2["pickup_unix"], "HH:mm:ss"))

# # T4=T3.drop('pickup_unix','dropoff_unix')

# # print('we have successfully created a time difference')
# # T4.printSchema()

T2 = T1.withColumn("time_diff", (col("drop") - col("pickup")).cast("int"))
T2.printSchema()

"""# **NOW WE WILL CREATE A UDF TO CALCULATE THE SPEED**"""

T2.drop('pick_up_time','drop_off_time')
T2.printSchema()

"""MISTAKE


"""

# T3 = T2.withColumn("speed_mps", col("trip_distance"*1000) / col("time_diff"))
# T4 = T3.withColumn("speed_kmph", round(col("speed_mps") * 3.6, 2))
# T4.show()
# def dis(d):
#   distance=d*1000
#   return distance

# from pyspark.sql.functions import udf
# from pyspark.sql.types import Integer

# # assuming 'trip_distance' is the name of the input column containing distances in kilometers
# T3= T2.withColumn('trip_distance_m', udf(dis, IntegerType())('trip_distance'))
# T3.show()

from pyspark.sql.functions import udf
from pyspark.sql.types import *
def dis(d,t):
    distance = d
    time=t/3600
    speed=distance/time
    return speed
def rounds(s):
  return(round(s))



# Register UDF
udf_dis = udf(dis, FloatType())

# Apply UDF to DataFrame
T3=T2.drop('pick_up_time','drop_off_time')
T3 = T3.withColumn("speed of cab in KM/HR", rounds(udf_dis("trip_distance",'time_diff')))

T3.printSchema()

T3.show()

T4 = T3.createOrReplaceTempView('DATATRANSFORM')
sql_query = '''
    SELECT  VendorID,COUNT(passenger_count) as Total_passenger, AVG(trip_distance) as AVG_DIS_travelled_today, AVG(total_amount) as EARNED_today 
    FROM DATATRANSFORM
    GROUP BY VendorID
'''
result = spark.sql(sql_query)
result.show(100)

# result.write.csv("path/to/output/file.csv", header=True)