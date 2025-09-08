# 🚦 AATOS – Artificially Augmented Traffic Observation System

## 📌 Overview
AATOS is a **smart traffic management system** that uses **YOLOv11 for car detection** and provides **dynamic traffic signal control** at a 4-way junction.

- 🚗 Vehicle detection using **YOLOv11**
- ⏱️ Variable green light timing based on traffic density
- 🤖 Optional **LLM-powered decision making** for adaptive policies
- 🔧 Future-ready for **hardware integration (Raspberry Pi/Arduino + LEDs)**

---

## 📂 Project Structure
AATOS/
│── traffic_yolo.py # YOLOv11 car detection + counting
│── traffic_controller.py # Junction logic
│── traffic_llm.py # LLM-based decision making (optional)
│── main.py # Entry point
│── requirements.txt # Dependencies
│── README.md # Documentation
---

## ⚡ Installation
```bash
git clone https://github.com/yourusername/AATOS.git
cd AATOS
pip install -r requirements.txt


## ▶️ Usage
# Run rule-based system:
python main.py

# Run with LLM decisions (requires OpenAI API key):
python main.py --llm

## 🚀 Example Output
North: 🚗 12 cars → Green 35s
North: 🟡 Yellow 2s
North: 🔴 Red

East: 🚗 3 cars → Green 10s
...
