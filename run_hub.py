from src.database import init_db, save_reading
from src.data_loader import fetch_farm_data, FARMS
from src.ml_engine import predict
import time

def main():
    print("Initializing Database...")
    init_db()
    
    print("Fetching data from sensors...")
    for farm_id in FARMS.keys():
        # 1. Fetch Data (Real or Synthetic fallback)
        data = fetch_farm_data(farm_id)
        
        # 2. Get AI Recommendation
        data['recommendation'] = predict(data)
        
        # 3. Save to SQLite
        save_reading(data)
        print(f"Saved data for {farm_id}: {data['recommendation']}")

if __name__ == "__main__":
    main()