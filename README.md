# 🎵 Music Recommendation System

## 📌 Overview
This project is a **Flask-based intelligent music/video recommendation system** that suggests videos based on user preferences, goals, and skill levels.

The system uses a **custom scoring algorithm** to recommend the most relevant videos from a dataset.

---

## 🚀 Features

- 🎯 Personalized recommendations  
- 📊 Multi-factor scoring system  
- 🔍 Filtering based on user input  
- ⚡ Fast API responses  
- 📁 CSV-based dataset handling  
- 🧠 Explanation for each recommendation  

---

## 🧠 How It Works

The system follows this workflow:

1. Load video data from CSV  
2. Take user input (goals, level, etc.)  
3. Apply scoring algorithm  
4. Rank videos  
5. Return top recommendations with explanation  

---

## 🏗️ Project Structure
├── app.py # Main Flask app
├── data_loader.py # Loads and filters dataset
├── recommendation_engine.py # Core recommendation logic
├── requirements.txt # Dependencies
├── Video Youtube algorythm.csv # Dataset

---

## ⚙️ Installation

### 1. Clone Repository
```bash
git clone https://github.com/MRizwanMalik/Music_Recomendation.git
cd Music_Recomendation

pip install -r requirements.txt

python app.py
http://127.0.0.1:5000

