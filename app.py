import requests
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


def fetch_nav(scheme_code: str, date: str) -> Optional[float]:
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}?date={date}"
        response = requests.get(url)
        nav_data = response.json()
        if 'data' in nav_data:
            for nav_entry in nav_data['data']:
                nav_entry_date = datetime.strptime(nav_entry['date'], '%d-%m-%Y').strftime('%Y-%m-%d')
                if nav_entry_date == date:
                    return float(nav_entry['nav'])
    except Exception as e:
        print(f"Error fetching NAV data: {e}")
    return None

def calculate_profit(scheme_code: str, start_date: str, end_date: str, capital: float = 1000000.0) -> Optional[float]:
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')

        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        nav_start = fetch_nav(scheme_code, start_date_obj.strftime('%Y-%m-%d'))
        nav_end = fetch_nav(scheme_code, end_date_obj.strftime('%Y-%m-%d'))
        if nav_start is not None and nav_end is not None:
            units_allotted = capital / nav_start
            value_end = units_allotted * nav_end
            profit = value_end - capital
            return profit
    except Exception as e:
        print(f"Error calculating profit: {e}")
    return None

@app.get("/profit")
async def get_profit(
    scheme_code: str = Query(..., description="The unique scheme code of the mutual fund."),
    start_date: str = Query(..., description="The purchase date of the mutual fund in dd-mm-yyyy format."),
    end_date: str = Query(..., description="The redemption date of the mutual fund in dd-mm-yyyy format."),
    capital: float = Query(1000000.0, description="The initial investment amount (default: 1000000.0)."),
):
    profit = calculate_profit(scheme_code, start_date, end_date, capital)
    if profit is not None:
        response_data = {"profit": profit}
        return JSONResponse(content=response_data)
    else:
        return JSONResponse(content={"error": "Failed to calculate profit"}, status_code=500)
