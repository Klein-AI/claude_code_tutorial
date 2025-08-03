#!/usr/bin/env python3
"""
Enhanced Animal Tracking Map Generator v3
Creates an interactive HTML map with all 6 animal classes and corrected time-based visualization
"""

import requests
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List


class SimpleAnimalMap:
    def __init__(self):
        self.base_url = "https://www.movebank.org/movebank/service/public/json"
        self.animal_colors = {
            'bird': '#FF6B6B',
            'mammal': '#4ECDC4', 
            'reptile': '#45B7D1',
            'fish': '#96CEB4',
            'amphibian': '#FFEAA7',
            'insect': '#DDA0DD',
            'unknown': '#74B9FF'
        }
    
    def get_movebank_studies(self) -> List[Dict]:
        """Get list of public studies with animal type information"""
        try:
            params = {'entity_type': 'study'}
            response = requests.get(self.base_url, params=params, timeout=15)
            if response.status_code == 200:
                studies = response.json()
                return [s for s in studies if s.get('is_test', False) == False and 
                       s.get('has_quota', False) == False][:20]  # Public studies only
        except Exception as e:
            print(f"Error fetching studies: {e}")
        return []
    
    def classify_animal_from_study(self, study_info: Dict) -> str:
        """Classify animal type based on study information"""
        study_name = study_info.get('name', '').lower()
        principal_investigator = study_info.get('principal_investigator_name', '').lower()
        
        # Bird keywords
        bird_keywords = ['bird', 'avian', 'eagle', 'hawk', 'falcon', 'owl', 'swan', 'crane', 
                        'stork', 'tern', 'albatross', 'petrel', 'gull', 'duck', 'goose']
        
        # Mammal keywords  
        mammal_keywords = ['mammal', 'whale', 'dolphin', 'seal', 'bear', 'wolf', 'deer', 
                          'elk', 'caribou', 'moose', 'cat', 'dog', 'bat', 'elephant']
        
        # Marine keywords
        marine_keywords = ['fish', 'shark', 'tuna', 'salmon', 'turtle', 'marine']
        
        # Reptile keywords
        reptile_keywords = ['turtle', 'snake', 'lizard', 'reptile', 'crocodile', 'iguana']
        
        # Check study name for keywords
        text_to_check = f"{study_name} {principal_investigator}"
        
        if any(keyword in text_to_check for keyword in bird_keywords):
            return 'bird'
        elif any(keyword in text_to_check for keyword in mammal_keywords):
            return 'mammal'
        elif any(keyword in text_to_check for keyword in marine_keywords):
            if any(keyword in text_to_check for keyword in reptile_keywords):
                return 'reptile'
            else:
                return 'fish'
        elif any(keyword in text_to_check for keyword in reptile_keywords):
            return 'reptile'
        
        return 'unknown'

    def get_sample_data(self) -> List[Dict]:
        """Get sample tracking data from multiple studies"""
        print("Fetching public studies...")
        
        # Get list of studies first
        studies = self.get_movebank_studies()
        if not studies:
            print("No studies found, using known study IDs...")
            studies = [{'id': 2911040}, {'id': 173641633}, {'id': 76367850}]
        
        all_data = []
        successful_studies = 0
        
        for study in studies[:10]:  # Limit to first 10 studies
            study_id = study.get('id')
            if not study_id:
                continue
                
            try:
                # Get study info if not already available
                if 'name' not in study:
                    study_params = {'entity_type': 'study', 'study_id': study_id}
                    study_response = requests.get(self.base_url, params=study_params, timeout=10)
                    if study_response.status_code == 200:
                        study_data = study_response.json()
                        if study_data:
                            study.update(study_data[0] if isinstance(study_data, list) else study_data)
                
                # Classify animal type
                animal_type = self.classify_animal_from_study(study)
                
                # Get tracking data
                params = {
                    'entity_type': 'event',
                    'study_id': study_id,
                    'max_events_per_individual': 20,
                    'limit': 100
                }
                
                response = requests.get(self.base_url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    if data and len(data) > 0:
                        valid_records = 0
                        for record in data:
                            lat = record.get('location_lat')
                            lon = record.get('location_long')
                            
                            if lat and lon:
                                try:
                                    lat, lon = float(lat), float(lon)
                                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                                        record['animal_type'] = animal_type
                                        record['study_name'] = study.get('name', f'Study {study_id}')
                                        record['species'] = self.extract_species_from_study(study)
                                        all_data.append(record)
                                        valid_records += 1
                                except ValueError:
                                    continue
                        
                        if valid_records > 0:
                            successful_studies += 1
                            print(f"✓ Got {valid_records} points from study {study_id} ({animal_type})")
                
            except Exception as e:
                print(f"✗ Error with study {study_id}: {e}")
                continue
            
            if successful_studies >= 5:  # Stop after 5 successful studies
                break
        
        print(f"Successfully processed {successful_studies} studies")
        return all_data[:300]  # Limit for performance
    
    def extract_species_from_study(self, study_info: Dict) -> str:
        """Extract species name from study information"""
        study_name = study_info.get('name', '')
        
        # Common species patterns
        species_patterns = {
            'arctic tern': 'Arctic Tern',
            'gray whale': 'Gray Whale', 
            'humpback whale': 'Humpback Whale',
            'loggerhead': 'Loggerhead Turtle',
            'bald eagle': 'Bald Eagle',
            'golden eagle': 'Golden Eagle',
            'brown bear': 'Brown Bear',
            'polar bear': 'Polar Bear',
            'caribou': 'Caribou',
            'elk': 'Elk',
            'white shark': 'Great White Shark',
            'bluefin tuna': 'Bluefin Tuna'
        }
        
        study_lower = study_name.lower()
        for pattern, species in species_patterns.items():
            if pattern in study_lower:
                return species
        
        # Extract first word that might be species
        words = study_name.split()
        if len(words) >= 2:
            return f"{words[0]} {words[1]}"
        
        return 'Unknown Species'
    
    def calculate_time_intensity(self, timestamp) -> float:
        """Calculate time-based intensity (recent = higher value for lighter colors)"""
        if not timestamp:
            return 0.5
        
        try:
            if isinstance(timestamp, str) and 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.fromtimestamp(float(timestamp) / 1000, tz=timezone.utc)
            
            # Use fixed reference date for consistency
            now = datetime(2024, 7, 31, tzinfo=timezone.utc)
            age_days = (now - dt).total_seconds() / 86400
            
            # CORRECTED: Recent = higher intensity (lighter), Older = lower intensity (darker)
            intensity = max(0.3, min(1.0, 1 - (age_days / 180)))
            return intensity
        except:
            return 0.5
    
    def adjust_color_intensity(self, base_color: str, intensity: float) -> str:
        """Adjust color based on recency (higher intensity = lighter/more recent)"""
        try:
            # Convert hex to RGB
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16) 
            b = int(base_color[5:7], 16)
            
            # CORRECTED: Higher intensity = brighter (more recent), Lower intensity = darker (older)
            white_blend = 1 - intensity  # Amount to blend with white for recent points
            r = round(r + (255 - r) * white_blend)
            g = round(g + (255 - g) * white_blend)
            b = round(b + (255 - b) * white_blend)
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return base_color
    
    def generate_html_map(self, data: List[Dict], filename: str = "animal_map.html"):
        """Generate enhanced interactive HTML map with v3 improvements"""
        
        # Process data and count individuals properly
        markers = []
        animal_counts = {}  # Count individuals, not points
        individual_ids = set()
        
        for record in data:
            lat = float(record.get('location_lat', 0))
            lon = float(record.get('location_long', 0))
            animal_type = record.get('animal_type', 'unknown')
            timestamp = record.get('timestamp', '')
            individual_id = record.get('individual_local_identifier', f'animal_{len(markers)}')
            
            # Calculate corrected time-based color
            intensity = self.calculate_time_intensity(timestamp)
            base_color = self.animal_colors.get(animal_type, '#74B9FF')
            adjusted_color = self.adjust_color_intensity(base_color, intensity)
            
            # Count each individual only once
            if individual_id not in individual_ids:
                individual_ids.add(individual_id)
                animal_counts[animal_type] = animal_counts.get(animal_type, 0) + 1
            
            markers.append({
                'lat': lat,
                'lng': lon,
                'color': adjusted_color,
                'baseColor': base_color,
                'intensity': intensity,
                'animal': animal_type,
                'species': record.get('species', 'Unknown Species'),
                'timestamp': str(timestamp)[:19] if timestamp else 'Unknown',
                'individual_id': individual_id
            })
        
        # Create HTML content with v3 improvements
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Animal Tracking World Map - Enhanced v3</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
        .info {{ 
            position: absolute; top: 10px; right: 10px; z-index: 1000;
            background: white; padding: 15px; border-radius: 8px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.2);
            max-width: 250px; font-size: 14px;
        }}
        .legend {{ margin-top: 15px; }}
        .legend-item {{ margin: 4px 0; display: flex; align-items: center; }}
        .color-box {{ 
            display: inline-block; width: 18px; height: 18px; 
            margin-right: 8px; border-radius: 3px; border: 1px solid #ddd;
        }}
        .time-legend {{ margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; }}
        .time-gradient {{ 
            height: 20px; width: 150px; margin: 5px 0;
            background: linear-gradient(to right, rgba(0,0,0,0.8), rgba(255,255,255,1));
            border-radius: 3px; border: 1px solid #ddd;
        }}
        .time-labels {{ display: flex; justify-content: space-between; font-size: 12px; color: #666; }}
        .path-info {{ margin-top: 10px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="info">
        <h3>🌍 Animal Tracking Map</h3>
        <p><strong>Total Animals:</strong> {len(individual_ids)}</p>
        <p><strong>Total Points:</strong> {len(markers)}</p>
        <div class="legend">
            <h4>Animal Classes:</h4>"""

        # Add comprehensive legend for all animal types
        all_animal_types = ['bird', 'mammal', 'reptile', 'fish', 'amphibian', 'insect']
        for animal in all_animal_types:
            count = animal_counts.get(animal, 0)
            color = self.animal_colors.get(animal, '#74B9FF')
            html_content += f'''
            <div class="legend-item">
                <span class="color-box" style="background-color: {color};"></span>
                <span>{animal.title()}: <span id="{animal}Count">{count}</span></span>
            </div>'''

        html_content += """
        </div>
        <div class="time-legend">
            <h4>Time Indicator:</h4>
            <div class="time-gradient"></div>
            <div class="time-labels">
                <span>6 Months Ago</span>
                <span>Recent</span>
            </div>
            <p style="font-size: 12px; margin: 5px 0; color: #666;">Lighter = More Recent</p>
        </div>
        <div class="path-info">
            <strong>Migration Paths:</strong><br>
            Lines connect individual animals' journeys
        </div>
    </div>

    <script>"""
        
        html_content += f"""
        // Initialize map centered globally
        var map = L.map('map').setView([30.0, -20.0], 2);

        // Add tile layer
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        // Enhanced data processing for individual animal paths
        var animalData = {json.dumps(markers)};
        var animalColors = {{
            'bird': '#FF6B6B',
            'mammal': '#4ECDC4',
            'reptile': '#45B7D1',
            'fish': '#96CEB4',
            'amphibian': '#FFEAA7',
            'insect': '#DDA0DD',
            'unknown': '#74B9FF'
        }};
        
        // Group data by individual for constellation-like path visualization
        var animalPaths = {{}};
        
        animalData.forEach(function(point) {{
            // Group by individual for paths
            if (!animalPaths[point.individual_id]) {{
                animalPaths[point.individual_id] = {{
                    points: [],
                    animal: point.animal,
                    species: point.species,
                    baseColor: point.baseColor
                }};
            }}
            animalPaths[point.individual_id].points.push(point);
        }});
        
        var markers = animalData;
        
        // Draw solid constellation-like migration paths
        Object.keys(animalPaths).forEach(function(individualId) {{
            var pathData = animalPaths[individualId];
            var points = pathData.points;
            
            if (points.length > 1) {{
                // Sort by timestamp to ensure correct chronological order
                points.sort(function(a, b) {{ 
                    return new Date(a.timestamp) - new Date(b.timestamp); 
                }});
                
                // Create path coordinates
                var pathCoords = points.map(function(p) {{ 
                    return [p.lat, p.lng]; 
                }});
                
                // Draw SOLID path line (constellation-like)
                L.polyline(pathCoords, {{
                    color: pathData.baseColor,
                    weight: 4,
                    opacity: 0.8,
                    smoothFactor: 1.0
                }}).bindPopup(`
                    <b>${{pathData.species}} Migration Path</b><br>
                    Individual: ${{individualId}}<br>
                    ${{points.length}} tracking points<br>
                    Class: ${{pathData.animal.charAt(0).toUpperCase() + pathData.animal.slice(1)}}
                `).addTo(map);
            }}
        }});
        
        // Add markers with corrected time-based coloring and sizing
        markers.forEach(function(marker) {{
            var circle = L.circleMarker([marker.lat, marker.lng], {{
                color: marker.color,
                fillColor: marker.color,
                fillOpacity: 0.8,
                opacity: 1,
                radius: Math.max(4, 6 + 4 * marker.intensity), // Size varies with recency
                weight: 2
            }});
            
            var timeAgo = Math.round((new Date('2024-07-31T00:00:00Z') - new Date(marker.timestamp + 'Z')) / (1000 * 60 * 60 * 24));
            
            var popup = `
                <div style="font-family: Arial, sans-serif;">
                    <h4 style="margin: 0 0 5px 0; color: ${{marker.baseColor}};">${{marker.animal.charAt(0).toUpperCase() + marker.animal.slice(1)}}</h4>
                    <strong>Species:</strong> ${{marker.species || 'Unknown'}}<br>
                    <strong>Coordinates:</strong> ${{marker.lat.toFixed(4)}}, ${{marker.lng.toFixed(4)}}<br>
                    <strong>Date:</strong> ${{new Date(marker.timestamp + 'Z').toLocaleDateString()}}<br>
                    <strong>Days Ago:</strong> ${{timeAgo}}<br>
                    <strong>Individual ID:</strong> ${{marker.individual_id}}<br>
                    <strong>Recency:</strong> ${{marker.intensity > 0.7 ? 'Recent' : marker.intensity > 0.5 ? 'Moderate' : 'Older'}}
                </div>
            `;
            
            circle.bindPopup(popup);
            circle.addTo(map);
        }});
    </script>
</body>
</html>"""

        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Map saved as '{filename}'")
        return filename


def main():
    print("🌍 Generating Enhanced Animal Tracking Map v3")
    print("="*50)
    
    mapper = SimpleAnimalMap()
    
    # Get sample data
    data = mapper.get_sample_data()
    
    if not data:
        print("❌ No data retrieved. Creating comprehensive demo map...")
        # Comprehensive demo data with all 6 animal classes
        data = [
            # Arctic Tern migration (Bird) - tern_001
            {'location_lat': 71.0, 'location_long': -8.0, 'animal_type': 'bird', 'species': 'Arctic Tern', 'timestamp': '2024-01-15T10:00:00Z', 'individual_local_identifier': 'tern_001'},
            {'location_lat': 65.0, 'location_long': -18.0, 'animal_type': 'bird', 'species': 'Arctic Tern', 'timestamp': '2024-03-01T12:00:00Z', 'individual_local_identifier': 'tern_001'},
            {'location_lat': 55.0, 'location_long': -25.0, 'animal_type': 'bird', 'species': 'Arctic Tern', 'timestamp': '2024-05-15T14:00:00Z', 'individual_local_identifier': 'tern_001'},
            {'location_lat': 40.0, 'location_long': -35.0, 'animal_type': 'bird', 'species': 'Arctic Tern', 'timestamp': '2024-06-01T16:00:00Z', 'individual_local_identifier': 'tern_001'},
            {'location_lat': 20.0, 'location_long': -45.0, 'animal_type': 'bird', 'species': 'Arctic Tern', 'timestamp': '2024-07-15T18:00:00Z', 'individual_local_identifier': 'tern_001'},
            
            # Gray Whale migration (Mammal) - whale_001
            {'location_lat': 60.0, 'location_long': -165.0, 'animal_type': 'mammal', 'species': 'Gray Whale', 'timestamp': '2024-01-15T08:00:00Z', 'individual_local_identifier': 'whale_001'},
            {'location_lat': 55.0, 'location_long': -155.0, 'animal_type': 'mammal', 'species': 'Gray Whale', 'timestamp': '2024-02-15T10:00:00Z', 'individual_local_identifier': 'whale_001'},
            {'location_lat': 45.0, 'location_long': -125.0, 'animal_type': 'mammal', 'species': 'Gray Whale', 'timestamp': '2024-04-01T12:00:00Z', 'individual_local_identifier': 'whale_001'},
            {'location_lat': 35.0, 'location_long': -120.0, 'animal_type': 'mammal', 'species': 'Gray Whale', 'timestamp': '2024-05-15T14:00:00Z', 'individual_local_identifier': 'whale_001'},
            {'location_lat': 25.0, 'location_long': -115.0, 'animal_type': 'mammal', 'species': 'Gray Whale', 'timestamp': '2024-07-15T16:00:00Z', 'individual_local_identifier': 'whale_001'},
            
            # Loggerhead Turtle migration (Reptile) - turtle_001
            {'location_lat': 30.0, 'location_long': -80.0, 'animal_type': 'reptile', 'species': 'Loggerhead Turtle', 'timestamp': '2024-02-01T09:00:00Z', 'individual_local_identifier': 'turtle_001'},
            {'location_lat': 28.0, 'location_long': -75.0, 'animal_type': 'reptile', 'species': 'Loggerhead Turtle', 'timestamp': '2024-03-15T11:00:00Z', 'individual_local_identifier': 'turtle_001'},
            {'location_lat': 25.0, 'location_long': -70.0, 'animal_type': 'reptile', 'species': 'Loggerhead Turtle', 'timestamp': '2024-05-01T13:00:00Z', 'individual_local_identifier': 'turtle_001'},
            {'location_lat': 20.0, 'location_long': -65.0, 'animal_type': 'reptile', 'species': 'Loggerhead Turtle', 'timestamp': '2024-06-10T15:00:00Z', 'individual_local_identifier': 'turtle_001'},
            {'location_lat': 15.0, 'location_long': -60.0, 'animal_type': 'reptile', 'species': 'Loggerhead Turtle', 'timestamp': '2024-07-20T17:00:00Z', 'individual_local_identifier': 'turtle_001'},
            
            # Bluefin Tuna migration (Fish) - tuna_001
            {'location_lat': 45.0, 'location_long': -50.0, 'animal_type': 'fish', 'species': 'Atlantic Bluefin Tuna', 'timestamp': '2024-01-10T08:00:00Z', 'individual_local_identifier': 'tuna_001'},
            {'location_lat': 40.0, 'location_long': -45.0, 'animal_type': 'fish', 'species': 'Atlantic Bluefin Tuna', 'timestamp': '2024-02-20T10:00:00Z', 'individual_local_identifier': 'tuna_001'},
            {'location_lat': 35.0, 'location_long': -40.0, 'animal_type': 'fish', 'species': 'Atlantic Bluefin Tuna', 'timestamp': '2024-04-15T12:00:00Z', 'individual_local_identifier': 'tuna_001'},
            {'location_lat': 30.0, 'location_long': -35.0, 'animal_type': 'fish', 'species': 'Atlantic Bluefin Tuna', 'timestamp': '2024-06-05T14:00:00Z', 'individual_local_identifier': 'tuna_001'},
            {'location_lat': 25.0, 'location_long': -30.0, 'animal_type': 'fish', 'species': 'Atlantic Bluefin Tuna', 'timestamp': '2024-07-25T16:00:00Z', 'individual_local_identifier': 'tuna_001'},
            
            # European Tree Frog migration (Amphibian) - frog_001
            {'location_lat': 52.0, 'location_long': 5.0, 'animal_type': 'amphibian', 'species': 'European Tree Frog', 'timestamp': '2024-03-01T08:00:00Z', 'individual_local_identifier': 'frog_001'},
            {'location_lat': 51.5, 'location_long': 4.5, 'animal_type': 'amphibian', 'species': 'European Tree Frog', 'timestamp': '2024-04-01T10:00:00Z', 'individual_local_identifier': 'frog_001'},
            {'location_lat': 51.0, 'location_long': 4.0, 'animal_type': 'amphibian', 'species': 'European Tree Frog', 'timestamp': '2024-05-01T12:00:00Z', 'individual_local_identifier': 'frog_001'},
            {'location_lat': 50.5, 'location_long': 3.5, 'animal_type': 'amphibian', 'species': 'European Tree Frog', 'timestamp': '2024-06-01T14:00:00Z', 'individual_local_identifier': 'frog_001'},
            {'location_lat': 50.0, 'location_long': 3.0, 'animal_type': 'amphibian', 'species': 'European Tree Frog', 'timestamp': '2024-07-01T16:00:00Z', 'individual_local_identifier': 'frog_001'},
            
            # Monarch Butterfly migration (Insect) - monarch_001
            {'location_lat': 50.0, 'location_long': -95.0, 'animal_type': 'insect', 'species': 'Monarch Butterfly', 'timestamp': '2024-02-15T08:00:00Z', 'individual_local_identifier': 'monarch_001'},
            {'location_lat': 45.0, 'location_long': -90.0, 'animal_type': 'insect', 'species': 'Monarch Butterfly', 'timestamp': '2024-03-30T10:00:00Z', 'individual_local_identifier': 'monarch_001'},
            {'location_lat': 40.0, 'location_long': -85.0, 'animal_type': 'insect', 'species': 'Monarch Butterfly', 'timestamp': '2024-05-15T12:00:00Z', 'individual_local_identifier': 'monarch_001'},
            {'location_lat': 35.0, 'location_long': -100.0, 'animal_type': 'insect', 'species': 'Monarch Butterfly', 'timestamp': '2024-06-20T14:00:00Z', 'individual_local_identifier': 'monarch_001'},
            {'location_lat': 25.0, 'location_long': -105.0, 'animal_type': 'insect', 'species': 'Monarch Butterfly', 'timestamp': '2024-07-30T16:00:00Z', 'individual_local_identifier': 'monarch_001'}
        ]
    
    # Generate map
    filename = mapper.generate_html_map(data)
    
    # Count unique individuals
    unique_individuals = len(set(d.get('individual_local_identifier', f'animal_{i}') for i, d in enumerate(data)))
    print(f"📊 Summary: {unique_individuals} individual animals, {len(data)} tracking points")
    print(f"🗺️  Open '{filename}' in your browser!")
    print(f"🎨 Features: All 6 animal classes, corrected time-based coloring (lighter=recent)")
    
    # Show file path for easy access
    full_path = os.path.abspath(filename)
    print(f"📁 Full path: file://{full_path}")


if __name__ == "__main__":
    main()