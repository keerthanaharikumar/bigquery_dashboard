from fastapi import FastAPI,Query,HTTPException
from google.cloud import bigquery
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pandas as pd

app=FastAPI(
    title="GA4 Analytics API",
    description="Queries Google Analytics 4 public dataset from BigQuery",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

client=bigquery.Client(project='pythonbigq')


@app.get("/",tags=['General'])
def home():
    "Welcome !! Lets check if the API is running"
    return{"message":"GA4 Analytics API is running"}
#____________END POINT 1____________________

@app.get("/events",tags=['Events'])
def event_names(
    start: str = Query(default="20201101", description="Start date YYYYMMDD"),
    end: str= Query(default="20201107", description="End date YYYYMMDD")
):
    """Returns the events that happened in the given date range"""

    query=f"""
    SELECT DISTINCT event_name
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '{start}' AND '{end}'
    """
    rows=client.query(query).result()
    return {
            "description":"Events Happened",
            "date_range":f"{start} to {end}",
            "data": [{"event_name": row.event_name} for row in rows]
    }
#________________________END POINT 2_________________________________________

@app.get("/top_events",tags=['Events'])
def get_top_events(
    start: str = Query(default="20201101", description="Start date YYYYMMDD"),
    end: str= Query(default="20201107", description="End date YYYYMMDD")
    ):
    """Returns the top 10 events by count for a given date range."""

    query= f"""
    SELECT event_name,COUNT(*) AS event_count
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '{start}' AND '{end}'
    GROUP BY event_name
    ORDER BY event_count DESC
    LIMIT 10
    """
    rows=client.query(query).result()
    return {
            "description":"Top 10 events by count",
            "date_range":f"{start} to {end}",
            "data": [{"event_name": row.event_name, "count": row.event_count} for row in rows]
    }
     

#_______________________ END POINT 3______________________________

@app.get("/revenue",tags=['Ecommerce'])
def revenue(
    start: str = Query(default="20201101", description="Start date YYYYMMDD"),
    end: str= Query(default="20201107", description="End date YYYYMMDD")
):
    """Returns the total revenue by date given date range"""

    query=f"""
    SELECT  event_date, COUNT(*) AS purchase,
    ROUND(SUM(ecommerce.purchase_revenue),2) AS total_revenue
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '{start}' AND '{end}'
    AND event_name='purchase'
    GROUP BY event_date
    ORDER BY total_revenue DESC

    """

    rows=client.query(query).result()
    return {
            "description":"Total Revenue",
            "date_range":f"{start} to {end}",
            "data": [{"event_date": row.event_date, "total_revenue": row.total_revenue} for row in rows]
    }

#________________________END POINT 4___________________________________________________


@app.get("/device",tags=['Audience'])
def device(
    start: str = Query(default="20201101", description="Start date YYYYMMDD"),
    end: str= Query(default="20201107", description="End date YYYYMMDD")
):
    """Number of unique users who visited each device in a given date range"""

    query=f"""
    SELECT  COUNT(DISTINCT user_pseudo_id) as visitors,
        device.category AS device
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN '{start}' AND '{end}'
    GROUP BY device
    ORDER BY visitors DESC
    """
    rows=client.query(query).result()
    return {
            "description":" Number of users per device",
            "date_range":f"{start} to {end}",
            "data": [{"no_of_visitors": row.visitors, "device": row.device} for row in rows]
    }

#___________________________END POINT 5__________________________________________________

@app.get("/percentage",tags=['Audience'])
def percentage(
    date: str = Query(default="20201101", 
                      description="Single date in YYYYMMDD format. Available dates: 20201101 to 20211231"),
):
    """Percentage of visits came from Mobile v/s Desktop v/s Tablet on a day.
    Available date range: November 2020 to December 2021"""
    
    if not (20201101 <= int(date) <= 20211231):
         raise HTTPException(
            status_code=400,
            detail="Date out of range. Please use a date between 20201101 and 20211231"
        )
       

    query=f"""
    WITH temp AS (
    SELECT COUNT(user_pseudo_id) as total_visitors
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX = '{date}'
    )


    SELECT  COUNT(user_pseudo_id) as visitors ,
            device.category AS device,(COUNT(user_pseudo_id)  * 100.0) / (MAX(total_visitors)) AS percentage
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` CROSS JOIN temp
    WHERE device.category IN ('mobile','desktop','tablet') AND _TABLE_SUFFIX = '{date}'
    GROUP BY device
    ORDER BY percentage DESC
    """
    rows=client.query(query).result()
    return {
            "description":" Percentage of visits per device",
            "date":date,
            "data": [{"device": row.device, "percentage": row.percentage} for row in rows]
    }

#________________________END POINT 6_________________________________________________________

@app.get("/country",tags=['Audience'])
def get_visitors_per_country(
    date: str = Query(default="20201101", 
                      description="Single date in YYYYMMDD format. Available dates: 20201101 to 20211231"),
):
    """Visitors per country on a day.
    Available date range: November 2020 to December 2021"""

    if not (20201101 <= int(date) <= 20211231):
        raise HTTPException(
            status_code=400,
            detail="Date out of range. Please use a date between 20201101 and 20211231"
        )
       

    query=f"""
    SELECT COUNT(DISTINCT user_pseudo_id) AS visitors,
    geo.country AS country
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX = '{date}'
    GROUP BY country
    ORDER BY visitors
    """
    rows=client.query(query).result()
    return {
            "description":" Visitors per country",
            "date":date,
            "data": [{"country": row.country, "visitors": row.visitors} for row in rows]

    }

#__________________________ END POINT 7___________________________________________
@app.get("/purchase",tags=['Ecommerce'])
def purchase_in_month(
    month: str = Query(default="202011", 
                      description="Year and month e.g. 202011"),
):
    """ Daily Purchases in a month."""
    
    if not (202011 <= int(month) <= 202112):
        raise HTTPException(
            status_code=400,
            detail="Month out of range. Please use a month between 202011 and 202112"
        )

    query=f"""
    SELECT event_date , COUNT(*) as purchases 
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX LIKE '{month}%' AND event_name='purchase'
    GROUP BY event_date
    ORDER BY purchases DESC
    """
    df=client.query(query).to_dataframe()
    df['event_date'] = pd.to_datetime(df['event_date'], format='%Y%m%d')
    return {
            "description":" Daily Purchases",
            "month":month,
            "data": df.to_dict(orient="records")

    }

#___________________________________END POINT 8______________________________________

@app.get("/avg_purchase",tags=['Ecommerce'])
def avg_purchase(
    month: str = Query(default="202011", 
                      description="Year and month e.g. 202011"),
):
    """ Top 10 Daily Average Revenue per Purchase in A Month."""
    
    if not (202011 <= int(month) <= 202112):
        raise HTTPException(
            status_code=400,
            detail="Month out of range. Please use a month between 202011 and 202112"
        )


    query=f"""
    SELECT event_date, ROUND(AVG(ecommerce.purchase_revenue), 2) as avg,COUNT(*) AS purchases
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX LIKE '{month}%' AND event_name='purchase'
    GROUP BY event_date
    ORDER BY avg DESC
    LIMIT 10
    """
    rows=client.query(query).result()
    return {
            "description":" Daily Average Revenue per Purchase",
            "month":month,
            "data": [{"date": row.event_date, "avg_revenue": row.avg , "purchase": row.purchases} for row in rows]

    }

#___________________________________END POINT 9 _____________________________________________

@app.get("/conversion",tags=['Ecommerce'])
def conv(
    month: str = Query(default="202011", 
                      description="Year and month e.g. 202011"),
):
    """ Daily Conversion Rates in A Month."""

    if not (202011 <= int(month) <= 202112):
        raise HTTPException(
            status_code=400,
            detail="Month out of range. Please use a month between 202011 and 202112"
        )

    query=f"""
    WITH temp AS (
    SELECT event_date,COUNT(DISTINCT user_pseudo_id) as total_users
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX LIKE '{month}%'
    GROUP BY event_date
    )


    SELECT  COUNT(DISTINCT user_pseudo_id) as users ,e.event_date,
            ROUND(COUNT(DISTINCT user_pseudo_id)*100.0 /MAX(total_users),2) as con_rate
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`AS e 
    INNER JOIN temp AS t ON t.event_date = e.event_date
    WHERE _TABLE_SUFFIX LIKE '{month}%' AND event_name ='purchase'
    GROUP BY e.event_date
    ORDER BY e.event_date
    """
    rows=client.query(query).result()
    return {
            "description":" Daily Conversion Rates",
            "month":month,
            "data": [{"date": row.event_date, "conversion rate":row.con_rate} for row in rows]

    }