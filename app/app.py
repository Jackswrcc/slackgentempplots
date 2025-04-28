from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
import pandas as pd
import matplotlib.pyplot as plt
import os

app = FastAPI()

# Load data once
file_path = "SLACKPLOTS/nysm_latest.csv"
data = pd.read_csv(file_path)
data['time'] = pd.to_datetime(data['time'], errors='coerce', format='mixed')
data = data.dropna(subset=['time'])

@app.get("/plot/{station_id}")
def plot_temperature(station_id: str):
    station_id = station_id.upper()
    station_data = data[data['station'] == station_id]

    if station_data.empty:
        return {"error": f"No data found for station: {station_id}"}

    station_data['temp_2m [degF]'] = station_data['temp_2m [degC]'] * 9/5 + 32

    plt.figure(figsize=(10, 6))
    plt.plot(station_data['time'], station_data['temp_2m [degF]'], label='2m Temperature (°F)', color='red')
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('2m Temperature (°F)', fontsize=12)
    plt.title(f'2m Temperature for Station: {station_id}', fontsize=14)
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    filename = f"{station_id}_plot.png"
    plt.savefig(filename)
    plt.close()

    return FileResponse(filename, media_type='image/png', filename=filename)

@app.post("/slack/plot")
async def slack_plot(request: Request):
    form_data = await request.form()
    text = form_data.get("text", "").strip().upper()

    if not text:
        return JSONResponse(content={"text": "Please provide a station ID like `/plot KALB`."})

    # URL where the plot can be accessed (your Render app URL)
    plot_url = f"https://your-app-name.onrender.com/plot/{text}"

    # Send the image in Slack
    slack_response = {
        "response_type": "in_channel",
        "attachments": [
            {
                "fallback": f"Temperature Plot for {text}",
                "image_url": plot_url,
                "text": f"Temperature Plot for {text}"
            }
        ]
    }

    return JSONResponse(content=slack_response)
