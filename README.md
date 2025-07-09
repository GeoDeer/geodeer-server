# 🦌 GeoDeer | A Map-Based Treasure Hunt Game

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat-square&logo=django&logoColor=white)
![HTML](https://img.shields.io/badge/-HTML-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/-CSS-1572B6?style=flat-square&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Flutter](https://img.shields.io/badge/-Flutter-02569B?style=flat-square&logo=flutter&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![PostGIS](https://img.shields.io/badge/-PostGIS-4185CA?style=flat-square&logo=postgis&logoColor=white)
![Leaflet](https://img.shields.io/badge/-Leaflet-199900?style=flat-square&logo=leaflet&logoColor=white)
![Render](https://img.shields.io/badge/-Render-00979D?style=flat-square&logo=render&logoColor=white)

🌐 **Live Demo:** [geodeer.render.com](https://geodeer.onrender.com)

GeoDeer is an interactive treasure hunt game designed for mobile and web platforms, combining GIS technology with gamification to enhance spatial awareness, cultural learning, and outdoor exploration.

Developed as a graduation project at Hacettepe University by the 2024-2025 Geomatics Engineering team, GeoDeer offers real-time tracking, dynamic scoring, and multiplayer interaction through a client-server architecture.

The project won 1st place in the 2025 Hacettepe University Geomatics Engineering Department Graduation Project Exhibition.

## 🎯 Problem Statement

Modern digital lifestyles often keep people indoors, limiting their interaction with real environments. As a result, spatial awareness and cultural connection are weakened. GeoDeer addresses this issue by encouraging players to explore outdoor environments through location-based tasks and challenges.

## 🧩 Key Features

- 🗺️ Interactive Map with Waypoints, Hints & Questions  
- 📱 Real-time Geolocation via Mobile & Web  
- 🧠 Dynamic Scoring System (based on time, location, and performance)  
- ⛔ Emulator/vehicle usage detection & disqualification  
- 👤 Main Menu & Profile Screen for Game Creators
- 📊 Game Monitor for Live User Location Tracking and Score Visualization  
- 🛠️ Admin Dashboard for Game Creation and Management  

## ⚙️ Tech Stack

| Component        | Technology                                 |
|------------------|---------------------------------------------|
| Frontend (Web)   | HTML, CSS, JavaScript, Leaflet              |
| [**Mobile**](https://github.com/GeoDeer/geodeer-mobile)          | Flutter, Geolocator                         |
| Backend API      | Django, Django REST Framework               |
| Database         | PostgreSQL with PostGIS extension           |
| Deployment       | Render.com                                  |
| Version Control  | GitHub                                      |

## 📡 System Architecture
![image](https://github.com/user-attachments/assets/26c4e030-25f1-421b-8e06-e117d2037325)

## 🧮 Scoring System

The total score of each player is calculated based on:

1. **Question-Based Score**  
   `Difficulty × 5` (0 if unanswered)

2. **Time-Based Bonus**  
   `Total Minutes – Game Duration`

3. **Answer-Time Bonus**  
   `Answer Time × (Difficulty / 10)`

4. **Location-Based Score**  
   `Performance = Distance / Time`

## 👥 Team & Contributions

### [**Haluk Hindistan**](https://github.com/halukhndstn) — Project Management, Backend & Deployment
- Project planning, task distribution, meeting coordination  
- Backend development
- Database management
- REST API integration  
- Dynamic web interface integration  
- Deployment management  
---

### [**Selin Altınok**](https://github.com/seliin21) — Frontend (Web) & Visual Designs
- Web client interface design
- Final project poster and presentation design
---

### [**Yağız Özkaya**](https://github.com/Y-1109) — Frontend (Web) & Media Edits
- E-chart designs
- Responsive design implementation
- Final project promotional video editing 
---

### [**Aziz Atacan Sancaktaroğlu**](https://github.com/aatacans) — Mobile
- Flutter-based mobile client development
- Database management
- REST API integration 
---

### [**Zeynep Aygül**](https://github.com/zeynepaygul) — Mobile
- Flutter-based mobile client development  


##  👨‍💻 Authors

**Team GeoDeer:** Aziz Atacan Sancaktaroğlu, Haluk Hindistan, Selin Altınok, Yağız Özkaya, Zeynep Aygül

**Advisor:** Asst. Prof. Dr. Murat Durmaz

Department of Geomatics Engineering, Hacettepe University, 2024–2025
