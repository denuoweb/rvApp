
# Nomadic Worker Platform

## Introduction

The Nomadic Worker Platform is a web-based application designed to assist nomadic workers and travelers in planning their routes, finding accommodation, and staying informed about the weather conditions along their journey. This platform integrates Google Maps for route planning and the OpenWeatherMap API for real-time weather updates, providing a seamless experience for planning trips, whether for work or leisure.

## Features

- **Route Planning:** Users can input their start and end destinations, travel mode, and waypoints to receive a detailed route plan.
- **Weather Updates:** Offers real-time weather information for each planned stop along the route.
- **Hotel Finder:** Displays a list of nearby hotels at each stop, aiding in accommodation planning.
- **Customizable Interval Planning:** Users can set custom intervals for stops, making long-distance travel planning more manageable.

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Dependencies

The project relies on several third-party libraries:

- Flask
- googlemaps
- requests

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/nomadic-worker-platform.git
cd nomadic-worker-platform
```

2. **Create a virtual environment** (Optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **API Keys**

You need to obtain API keys for Google Maps and OpenWeatherMap and set them in your environment variables or directly in your `app.py` file (not recommended for production).

## Configuration

Before running the application, ensure you have set the necessary API keys in your environment variables:

- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key.
- `OPENWEATHERMAP_API_KEY`: Your OpenWeatherMap API key.

## Running the Application

1. Start the Flask application:

```bash
python app.py
```

2. Open a web browser and navigate to `http://127.0.0.1:5000/` to access the Nomadic Worker Platform.

## Usage

- **Planning a Route:**
  1. Enter your start and end destinations.
  2. Choose your mode of travel.
  3. Specify your preferred interval for stops.
  4. Optionally, add waypoints to customize your route.
  5. Submit the form to receive your detailed route plan, including weather updates and hotel suggestions.

- **Finding Hotels and Weather Information:**
  - Along with the route details, the platform provides a list of nearby hotels and current weather conditions for each planned stop.

## Contributing

Contributions to the Nomadic Worker Platform are welcome. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments

- Google Maps API for providing map data and services.
- OpenWeatherMap for offering weather information.
