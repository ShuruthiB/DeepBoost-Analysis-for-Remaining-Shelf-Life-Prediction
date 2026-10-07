import time
import requests
import random

API_URL = "http://127.0.0.1:8000/api/predict"

def simulate_sensor():
    print("Starting DeepBoost IoT Simulator...")
    print("Simulating a broken refrigeration unit. Temperatures will slowly rise...")
    
    temperatures = [4.0, 4.0, 4.0, 4.0, 4.0]
    item_name = "Banana"
    ph = 4.8
    moisture = 0.75
    day_count = 0
    
    while True:
        day_count += 1
        
        # Simulate Broken Fridge: slow rise in temp, then a sudden heatwave
        new_temp = temperatures[-1] + random.uniform(-0.5, 1.5)
        if day_count > 10:
            new_temp += 3.0 # Heatwave
            
        temperatures.pop(0)
        temperatures.append(round(new_temp, 2))
        
        payload = {
            "item_name": item_name,
            "ph": ph,
            "moisture": moisture,
            "temperatures": temperatures
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                result = response.json()
                print(f"[Day {day_count}] Sent Temp: {new_temp:.1f}C | Predicted Shelf Life: {result['predicted_shelf_life_days']} days | Status: {result['status']}")
            else:
                print(f"Error from server: {response.text}")
        except requests.exceptions.ConnectionError:
            print("Backend not running. Start FastAPI server using: python main.py")
            
        time.sleep(2)

if __name__ == "__main__":
    simulate_sensor()
