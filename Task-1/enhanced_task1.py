import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta
import numpy as np
from dotenv import load_dotenv

# Load environment variables for API key
load_dotenv()

class WeatherDashboard:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '5dfe1d2dd87128f61cdba9b8f1dcf9d8')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.cities = ["New Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"]
        
    def fetch_current_weather(self, city):
        """Fetch current weather data for a city"""
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {city}: {e}")
            return None
    
    def fetch_forecast(self, city):
        """Fetch 5-day forecast data for a city"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast for {city}: {e}")
            return None
    
    def process_weather_data(self, data):
        """Process weather data into a structured format"""
        if not data or data.get("cod") == "404":
            return None
            
        main_data = data["main"]
        weather_data = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": main_data["temp"],
            "feels_like": main_data["feels_like"],
            "humidity": main_data["humidity"],
            "pressure": main_data["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return weather_data
    
    def process_forecast_data(self, data):
        """Process forecast data into a structured format"""
        if not data or data.get("cod") == "404":
            return []
            
        forecast_list = []
        for item in data["list"]:
            forecast_data = {
                "city": data["city"]["name"],
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"],
                "wind_speed": item["wind"]["speed"]
            }
            forecast_list.append(forecast_data)
        return forecast_list
    
    def create_dashboard(self):
        """Create a comprehensive weather dashboard"""
        print("🌤️  Weather Dashboard - API Integration & Data Visualization")
        print("=" * 60)
        
        # Fetch data for multiple cities
        current_weather_data = []
        forecast_data = []
        
        for city in self.cities:
            print(f"Fetching data for {city}...")
            
            # Current weather
            current_data = self.fetch_current_weather(city)
            if current_data:
                processed_current = self.process_weather_data(current_data)
                if processed_current:
                    current_weather_data.append(processed_current)
            
            # Forecast
            forecast_data_city = self.fetch_forecast(city)
            if forecast_data_city:
                processed_forecast = self.process_forecast_data(forecast_data_city)
                forecast_data.extend(processed_forecast)
        
        if not current_weather_data:
            print("❌ No weather data could be fetched. Please check your API key and internet connection.")
            return
        
        # Create DataFrames
        df_current = pd.DataFrame(current_weather_data)
        df_forecast = pd.DataFrame(forecast_data)
        
        # Save data to CSV
        df_current.to_csv('current_weather_data.csv', index=False)
        df_forecast.to_csv('forecast_data.csv', index=False)
        print("✅ Data saved to CSV files")
        
        # Create comprehensive dashboard
        self.create_visualizations(df_current, df_forecast)
        
    def create_visualizations(self, df_current, df_forecast):
        """Create multiple visualizations for the dashboard"""
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Current Weather Comparison Across Cities
        plt.subplot(3, 3, 1)
        cities = df_current['city']
        temps = df_current['temperature']
        bars = plt.bar(cities, temps, color=sns.color_palette("viridis", len(cities)))
        plt.title('Current Temperature Across Cities', fontsize=14, fontweight='bold')
        plt.ylabel('Temperature (°C)')
        plt.xticks(rotation=45)
        
        # Add temperature values on bars
        for bar, temp in zip(bars, temps):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    f'{temp:.1f}°C', ha='center', va='bottom', fontweight='bold')
        
        # 2. Humidity Comparison
        plt.subplot(3, 3, 2)
        humidity = df_current['humidity']
        plt.pie(humidity, labels=cities, autopct='%1.1f%%', startangle=90)
        plt.title('Humidity Distribution', fontsize=14, fontweight='bold')
        
        # 3. Weather Parameters Radar Chart (for first city)
        plt.subplot(3, 3, 3)
        city_data = df_current.iloc[0]
        categories = ['Temperature', 'Humidity', 'Pressure', 'Wind Speed']
        values = [city_data['temperature'], city_data['humidity'], 
                 city_data['pressure']/10, city_data['wind_speed']*10]  # Normalize for better visualization
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        values += values[:1]  # Complete the circle
        angles += angles[:1]
        
        ax = plt.subplot(3, 3, 3, projection='polar')
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(f'Weather Parameters - {city_data["city"]}', fontsize=14, fontweight='bold')
        
        # 4. Temperature vs Humidity Scatter
        plt.subplot(3, 3, 4)
        plt.scatter(df_current['temperature'], df_current['humidity'], 
                   s=100, c=df_current['temperature'], cmap='viridis', alpha=0.7)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Humidity (%)')
        plt.title('Temperature vs Humidity', fontsize=14, fontweight='bold')
        plt.colorbar(label='Temperature (°C)')
        
        # Add city labels
        for i, city in enumerate(df_current['city']):
            plt.annotate(city, (df_current['temperature'].iloc[i], df_current['humidity'].iloc[i]),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # 5. Wind Speed Comparison
        plt.subplot(3, 3, 5)
        wind_speeds = df_current['wind_speed']
        colors = ['red' if ws > 5 else 'orange' if ws > 3 else 'green' for ws in wind_speeds]
        bars = plt.bar(cities, wind_speeds, color=colors, alpha=0.7)
        plt.title('Wind Speed Comparison', fontsize=14, fontweight='bold')
        plt.ylabel('Wind Speed (m/s)')
        plt.xticks(rotation=45)
        
        # 6. Forecast Temperature Trend (for first city)
        if not df_forecast.empty:
            plt.subplot(3, 3, 6)
            first_city_forecast = df_forecast[df_forecast['city'] == df_current['city'].iloc[0]]
            if not first_city_forecast.empty:
                first_city_forecast['datetime'] = pd.to_datetime(first_city_forecast['datetime'])
                plt.plot(first_city_forecast['datetime'], first_city_forecast['temperature'], 
                        marker='o', linewidth=2, markersize=6)
                plt.title(f'5-Day Temperature Forecast - {df_current["city"].iloc[0]}', 
                         fontsize=14, fontweight='bold')
                plt.ylabel('Temperature (°C)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
        
        # 7. Weather Description Distribution
        plt.subplot(3, 3, 7)
        weather_counts = df_current['description'].value_counts()
        plt.pie(weather_counts.values, labels=weather_counts.index, autopct='%1.1f%%')
        plt.title('Weather Conditions Distribution', fontsize=14, fontweight='bold')
        
        # 8. Pressure vs Temperature
        plt.subplot(3, 3, 8)
        plt.scatter(df_current['pressure'], df_current['temperature'], 
                   s=100, c=df_current['humidity'], cmap='plasma', alpha=0.7)
        plt.xlabel('Pressure (hPa)')
        plt.ylabel('Temperature (°C)')
        plt.title('Pressure vs Temperature', fontsize=14, fontweight='bold')
        plt.colorbar(label='Humidity (%)')
        
        # 9. Summary Statistics Table
        plt.subplot(3, 3, 9)
        plt.axis('off')
        
        # Create summary table
        summary_data = [
            ['City', 'Temp (°C)', 'Humidity (%)', 'Wind (m/s)'],
        ]
        for _, row in df_current.iterrows():
            summary_data.append([
                row['city'],
                f"{row['temperature']:.1f}",
                f"{row['humidity']:.0f}",
                f"{row['wind_speed']:.1f}"
            ])
        
        table = plt.table(cellText=summary_data[1:], colLabels=summary_data[0],
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        plt.title('Weather Summary', fontsize=14, fontweight='bold', pad=20)
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig('weather_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Weather Dashboard created successfully!")
        print("📊 Dashboard saved as 'weather_dashboard.png'")
        print("📁 Data saved as 'current_weather_data.csv' and 'forecast_data.csv'")
        
        # Print summary
        print("\n📋 Weather Summary:")
        print("-" * 40)
        for _, row in df_current.iterrows():
            print(f"{row['city']}: {row['temperature']:.1f}°C, {row['humidity']}% humidity, "
                  f"{row['wind_speed']:.1f} m/s wind")

def main():
    """Main function to run the weather dashboard"""
    print("🚀 Starting Weather API Integration & Data Visualization Dashboard")
    print("=" * 70)
    
    # Create and run dashboard
    dashboard = WeatherDashboard()
    dashboard.create_dashboard()
    
    print("\n🎉 Task-1 Completed Successfully!")
    print("✅ API Integration: OpenWeatherMap API")
    print("✅ Data Visualization: Multiple charts and dashboard")
    print("✅ Data Analysis: Cross-city comparison and trends")
    print("✅ Deliverables: Script, Dashboard, and Data Files")

if __name__ == "__main__":
    main() 