# 🚀 Smart Wi-Fi Coverage Optimization (BSc Graduation Project)

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Institution](https://img.shields.io/badge/Mersin%20University-Electrical%20%26%20Electronics-red.svg)](https://www.mersin.edu.tr/)

An advanced indoor Wi-Fi signal coverage optimization system developed as a Bachelor's Graduation Project at Mersin University, Department of Electrical and Electronics Engineering.

---

## 📌 Project Overview
Random router placement in indoor environments often leads to signal degradation, dead zones, and connection instability. This project introduces an automated optimization framework in Python that models physical obstructions (walls, furniture, metal cabinets) and calculates the optimal placement for a Wi-Fi router to achieve maximum signal strength and homogeneity.

---

## 🛠️ Key Features & Technologies
* **Geometric Environment Modeling:** Utilizes the `Shapely` library to model indoor layouts and calculate signal attenuation based on obstacle intersection lengths.
* **Mathematical Optimization:** Implements custom utility score functions combining mean signal strength, standard deviation, and threshold penalties, optimized via `SciPy`.
* **Multi-Library 3D & 2D Visualizations:** Generates 2D heatmaps (`Matplotlib`) and interactive 3D visualizations (`Open3D`, `Plotly`, `PyVista`, `Vedo`).
* **Automated Reporting:** Automatically exports evaluation results and point-by-point signal metrics into Word (`.docx`) and PDF formats.
* **Interactive Interface:** Allows users to manually reposition the router and evaluate real-time performance scores.

---

## 📁 Repository Structure
```text
Smart-Wi-Fi-Coverage-Optimization/
│
├── code/
│   └── wifi_optimization.py       # Main Python optimization script
├── reports/
│   ├── wifi_report.docx           # Automated Word evaluation report
│   └── wifi_report.pdf            # Automated PDF evaluation report
├── assets/
│   └── heatmap.png                # Signal strength heatmap
├── index.html                     # GitHub Pages portfolio website
└── README.md                      # Project documentation
## 📊 Project Poster
![Wi-Fi Optimization Poster](assets/bitirme%20projesı%20poster.jpg)



<img width="789" height="452" alt="3" src="https://github.com/user-attachments/assets/3d32272c-7ac2-4fee-9dac-4bbe59e2ef1e" />
<img width="775" height="422" alt="2" src="https://github.com/user-attachments/assets/245720ba-cb04-4713-9e31-40acc62df71c" />
<img width="817" height="409" alt="1" src="https://github.com/user-attachments/assets/7f60359c-cc5b-4c0e-b1ef-e31fa1bce704" />
<img width="761" height="602" alt="8" src="https://github.com/user-attachments/assets/5fd1fbf7-1c32-4bfc-9ceb-9373f4846963" />
<img width="787" height="482" alt="7" src="https://github.com/user-attachments/assets/83139f94-6bc3-4bb4-af10-e6ceded005b3" />
<img width="729" height="493" alt="5" src="https://github.com/user-attachments/assets/ff3739a0-e0fe-45ab-a3e4-188918d0129b" />
<img width="693" height="721" alt="4" src="https://github.com/user-attachments/assets/56153696-10f0-4074-8e4a-1a67cdecc69e" />
