# 🌍 Interactive Animal Tracking Map

A professional interactive world map visualization showing real-time animal migration patterns with time-based color coding and constellation-like path visualization.

## 🎥 Tutorial Video

This repository accompanies a tutorial video demonstrating how to build an interactive animal tracking map from scratch using Python and modern web technologies.

## ✨ Features

- **📍 Multi-Class Animal Tracking**: Supports 6 animal classes (Bird, Mammal, Reptile, Fish, Amphibian, Insect)
- **🛤️ Migration Paths**: Constellation-like solid lines connecting individual animal journeys
- **⏰ Time-Based Visualization**: Lighter colors indicate more recent data points
- **📊 Interactive Legend**: Dynamic counts and comprehensive class breakdown
- **🗺️ Global Coverage**: Worldwide animal tracking with realistic migration patterns
- **🔗 Real Data Integration**: Connects to Movebank API for live animal tracking data
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Modern web browser

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd claude_code_tutorial
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the generator:**
   ```bash
   python animal_tracking_map.py
   ```

4. **Open the generated map:**
   ```bash
   # Open animal_map.html in your browser
   # Or view the pre-generated enhanced_animal_tracking_map_v3.html
   ```

## 📁 Project Structure

```
claude_code_tutorial/
├── animal_tracking_map.py              # Main Python script
├── enhanced_animal_tracking_map_v3.html # Pre-generated enhanced map
├── requirements.txt                     # Python dependencies
├── README.md                           # This file
└── data/                               # Sample data (created on first run)
```

## 🎨 Features Demonstrated

### 1. Animal Class Visualization
- **🐦 Birds**: Arctic Terns (Red #FF6B6B)
- **🐾 Mammals**: Gray Whales (Teal #4ECDC4)
- **🦎 Reptiles**: Loggerhead Turtles (Blue #45B7D1)
- **🐟 Fish**: Atlantic Bluefin Tuna (Green #96CEB4)
- **🐸 Amphibians**: European Tree Frogs (Yellow #FFEAA7)
- **🦗 Insects**: Monarch Butterflies (Purple #DDA0DD)

### 2. Migration Path Visualization
Each individual animal's journey is connected by solid lines, creating constellation-like patterns that clearly show migration routes over time.

### 3. Time-Based Color Coding
- **Lighter colors** = More recent tracking data
- **Darker colors** = Older tracking data
- **Variable marker sizes** = Recency indicator

### 4. Interactive Elements
- **Click markers** for detailed animal information
- **Click paths** for migration summary
- **Responsive legend** with live counts
- **Time gradient indicator**

## 🔧 Technical Implementation

### Data Sources
- **Primary**: [Movebank](https://www.movebank.org/) - Global animal tracking database
- **Fallback**: Comprehensive demo data with realistic migration patterns

### Technologies Used
- **Backend**: Python 3 with `requests` library
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapping**: [Leaflet.js](https://leafletjs.com/) - Open-source interactive maps
- **Data Format**: JSON for seamless data exchange

### Key Components

1. **Data Processing** (`animal_tracking_map.py`):
   - Movebank API integration
   - Animal classification algorithms
   - Time-based color calculation
   - Individual tracking aggregation

2. **Visualization** (Generated HTML):
   - Interactive Leaflet map
   - Dynamic marker rendering
   - Path visualization
   - Responsive UI components

## 🌟 Code Highlights

### Time-Based Color Calculation
```python
def calculate_time_intensity(self, timestamp) -> float:
    """Calculate time-based intensity (recent = higher value for lighter colors)"""
    # Recent data gets higher intensity (lighter colors)
    # Older data gets lower intensity (darker colors)
    intensity = max(0.3, min(1.0, 1 - (age_days / 180)))
    return intensity
```

### Path Visualization
```javascript
// Draw solid constellation-like migration paths
L.polyline(pathCoords, {
    color: pathData.baseColor,
    weight: 4,
    opacity: 0.8,
    smoothFactor: 1.0
}).addTo(map);
```

## 📊 Sample Data

The project includes comprehensive demo data featuring:
- **6 individual animals** from different classes
- **30 tracking points** spanning 6 months
- **Realistic migration patterns** based on actual animal behavior
- **Global coverage** across multiple continents

## 🛠️ Customization

### Adding New Animal Classes
1. Update `animal_colors` dictionary in `animal_tracking_map.py`
2. Add classification keywords in `classify_animal_from_study()`
3. Include sample data for the new class

### Modifying Time Ranges
Adjust the time calculation in `calculate_time_intensity()` to change the recency window.

### Styling Changes
Customize colors, marker sizes, and UI elements in the generated HTML template.

## 🤝 Contributing

This project is part of a tutorial series. Feel free to:
- Report issues
- Suggest improvements
- Share your own animal tracking visualizations

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

## 🙋‍♂️ Support

For questions about this tutorial:
- Check the tutorial video
- Review the code comments
- Open an issue in this repository

---

**Built with ❤️ for the animal tracking and data visualization community**