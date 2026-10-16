import pandas as pd
import numpy as np
import math
import time

def calculate_q10_decay_vectorized(temps, base_life, ph, moisture):
    """
    Vectorized calculation of the physical Q10 exponential decay equation.
    Runs in milliseconds for millions of records using NumPy.
    """
    cumulative = np.zeros(len(base_life))
    for i in range(5):
        t = temps[:, i]
        cumulative = (cumulative * 1.3) + np.exp((t - 20) / 6.0)
        
    static_mod = (ph / 4.0) * (moisture / 0.8)
    shelf_life = (base_life * static_mod) - (cumulative / 4.0)
    
    return np.clip(shelf_life, 0.0, 40.0)

def generate_1m_dataset():
    print("Generating 1,000,000 synthetic records...")
    start_time = time.time()
    
    N = 1_000_000
    
    varieties = ['Banana', 'Orange', 'Pineapple', 'Tomato']
    bases = {'Banana': 15.0, 'Orange': 28.0, 'Pineapple': 10.0, 'Tomato': 18.0}
    
    # Randomly assign varieties
    v_choices = np.random.choice(varieties, N)
    base_lives = np.array([bases[v] for v in v_choices])
    
    ph = np.zeros(N)
    moisture = np.zeros(N)
    temps = np.zeros((N, 5))
    
    # Biological optimal ranges
    optimal = {
        'Banana': {'ph': 4.8, 'm': 0.77, 't': 14.0},
        'Orange': {'ph': 3.8, 'm': 0.87, 't': 5.0},
        'Pineapple': {'ph': 3.6, 'm': 0.84, 't': 11.5},
        'Tomato': {'ph': 4.5, 'm': 0.92, 't': 14.0}
    }
    
    for v in varieties:
        mask = (v_choices == v)
        count = np.sum(mask)
        if count == 0: continue
        
        # pH and moisture with realistic gaussian noise
        ph[mask] = np.random.normal(optimal[v]['ph'], 0.2, count)
        moisture[mask] = np.random.normal(optimal[v]['m'], 0.03, count)
        
        # Temperatures (5 day history)
        base_t = optimal[v]['t']
        
        # 80% normal conditions, 20% anomaly (severe heatwave)
        anomaly = np.random.choice([0, 1], size=count, p=[0.8, 0.2])
        
        for day in range(5):
            t_noise = np.random.normal(0, 1.5, count)
            # If anomaly=1 and day >= 2, inject a severe temperature spike
            spike = np.where((anomaly == 1) & (day >= 2), np.random.uniform(4, 9, count), 0)
            temps[mask, day] = base_t + t_noise + spike
            
    # Calculate physical target variable
    shelf_life = calculate_q10_decay_vectorized(temps, base_lives, ph, moisture)
    
    # Compile into a Pandas DataFrame
    df = pd.DataFrame({
        'Batch_ID': [f'BATCH-{i:07d}' for i in range(N)],
        'Variety': v_choices,
        'pH': np.round(ph, 2),
        'Moisture': np.round(moisture, 2),
        'Temp_Day1': np.round(temps[:, 0], 1),
        'Temp_Day2': np.round(temps[:, 1], 1),
        'Temp_Day3': np.round(temps[:, 2], 1),
        'Temp_Day4': np.round(temps[:, 3], 1),
        'Temp_Day5': np.round(temps[:, 4], 1),
        'Target_Shelf_Life_Days': np.round(shelf_life, 1)
    })
    
    print(f"Data generated in memory in {time.time() - start_time:.2f} seconds.")
    
    # 1. Export as CSV
    print("Saving to CSV...")
    csv_start = time.time()
    df.to_csv('inventory_dataset_1M.csv', index=False)
    print(f"CSV saved successfully! ({time.time() - csv_start:.2f} seconds)")
    
    # 2. Export as Excel (.xlsx)
    print("Saving to Excel (Warning: 1 Million rows will take a few minutes)...")
    excel_start = time.time()
    # Engine 'xlsxwriter' is required as it handles massive data streams without crashing your RAM
    df.to_excel('inventory_dataset_1M.xlsx', index=False, engine='xlsxwriter')
    print(f"Excel saved successfully! ({time.time() - excel_start:.2f} seconds)")

if __name__ == "__main__":
    generate_1m_dataset()
