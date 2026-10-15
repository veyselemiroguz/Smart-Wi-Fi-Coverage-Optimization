import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# matplotlib.use('Qt5Agg')

from shapely.geometry import Polygon, LineString
from scipy.optimize import minimize
from typing import List, Tuple
import logging

# Report & 3D libraries
from docx import Document
from fpdf import FPDF
import open3d as o3d
import plotly.graph_objects as go
import pyvista as pv
from vedo import Plotter, Box, Sphere, Points
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Room setup
class Furniture:
    def __init__(self, name: str, x_min: float, y_min: float, x_max: float, y_max: float, attenuation_per_meter: float):
        self.name = name
        self.polygon = Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
        self.attenuation_per_meter = attenuation_per_meter

class Room:
    def __init__(self, width: float, height: float, noise: float = 5.0):
        self.width = width
        self.height = height
        self.noise = noise
        self.furniture: List[Furniture] = []

    def add_furniture(self, furniture: Furniture):
        self.furniture.append(furniture)

def setup_room() -> Room:
    room = Room(7, 5)
    room.add_furniture(Furniture("Metal Dolap", 1, 1, 2, 2, 4))
    room.add_furniture(Furniture("Ahşap Masa", 4, 1, 5, 2, 2))
    room.add_furniture(Furniture("Plastik Sandalye", 3, 3, 3.5, 3.5, 1))
    room.add_furniture(Furniture("Koltuk", 5, 3.5, 6, 4.5, 1.5))
    room.add_furniture(Furniture("Televizyon", 6, 0.5, 6.5, 1.5, 3.5))
    room.add_furniture(Furniture("Halı", 0, 0, 7, 5, 0.5))
    room.add_furniture(Furniture("Kuzey Duvarı", 0, 0, 0.1, 5, 20))
    room.add_furniture(Furniture("Güney Duvarı", 6.9, 0, 7, 5, 20))
    room.add_furniture(Furniture("Batı Duvarı", 0, 0, 7, 0.1, 20))
    room.add_furniture(Furniture("Doğu Duvarı", 0, 4.9, 7, 5, 20))
    return room

class WiFiPropagationModel:
    def __init__(self, room: Room, start_power=20.0, path_loss_exponent=2.5, reference_loss=40.0, d0=1.0):
        self.room = room
        self.start_power = start_power
        self.n = path_loss_exponent
        self.PL0 = reference_loss
        self.d0 = d0

    def calculate_path_loss(self, router_pos, point):
        d = max(np.linalg.norm(router_pos - point), self.d0)
        return self.PL0 + 10 * self.n * np.log10(d / self.d0)

    def calculate_total_attenuation(self, router_pos, point):
        line = LineString([router_pos, point])
        total_att = self.room.noise
        for f in self.room.furniture:
            if line.crosses(f.polygon):
                inter = line.intersection(f.polygon)
                length = inter.length if inter.geom_type == "LineString" else 0.1
                total_att += f.attenuation_per_meter * length
        return total_att

    def calculate_signal_strength(self, router_pos, point):
        return self.start_power - self.calculate_path_loss(router_pos, point) - self.calculate_total_attenuation(router_pos, point)

    def optimization_objective(self, router_pos, _):  
        resolution = 20 
        grid_x, grid_y = np.meshgrid(
            np.linspace(0, self.room.width, resolution),
            np.linspace(0, self.room.height, resolution)
        )

        signals = []
        for i in range(resolution):
            for j in range(resolution):
                point = np.array([grid_x[i, j], grid_y[i, j]])
                signal = self.calculate_signal_strength(router_pos, point)
                signals.append(signal)

        signals = np.array(signals)
        mean_signal = np.mean(signals)
        std_signal = np.std(signals)
        penalty = np.sum((signals < -65) * (abs(signals + 65)))                       
        score = (mean_signal + 100) / 10 - 0.2 * std_signal - 0.5 * penalty
        return -score

def generate_measurement_points(room: Room, num_points=10, seed=42):
    np.random.seed(seed)
    pts = np.random.rand(num_points, 2)
    pts[:, 0] *= room.width
    pts[:, 1] *= room.height
    return pts

def optimize_router_position(model, points):
    best_score = float("inf")
    best_pos = None
    for x in np.linspace(0, model.room.width, 50):
        for y in np.linspace(0, model.room.height, 50):
            pos = np.array([x, y])
            score = model.optimization_objective(pos, points)
            if score < best_score:
                best_score = score
                best_pos = pos
    return minimize(model.optimization_objective, best_pos, args=(points,), bounds=[(0, model.room.width), (0, model.room.height)]).x
def draw_heatmap(model, router_pos, resolution=100):
    grid_x, grid_y = np.meshgrid(
        np.linspace(0, model.room.width, resolution),
        np.linspace(0, model.room.height, resolution)
    )
    signal_map = np.zeros_like(grid_x)
    for i in range(resolution):
        for j in range(resolution):
            signal_map[i, j] = model.calculate_signal_strength(router_pos, np.array([grid_x[i, j], grid_y[i, j]]))
    return grid_x, grid_y, signal_map

def show_static_heatmap(model, router_pos):
    grid_x, grid_y, signal_map = draw_heatmap(model, router_pos)
    fig, ax = plt.subplots(figsize=(12, 7))
    contour = ax.contourf(grid_x, grid_y, signal_map, levels=50, cmap='plasma')
    plt.colorbar(contour, ax=ax, label="Signal Strength (dBm)")
    for f in model.room.furniture:
        x, y = f.polygon.exterior.xy
        ax.fill(x, y, alpha=0.3, label=f.name)
    ax.scatter(router_pos[0], router_pos[1], c='white', edgecolors='black', s=200, label='Optimize Router')
    ax.set_title("Optimize Edilmiş Router için Sabit Isı Haritası")
    ax.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def show_interactive_with_score(model, initial_router_pos, measurement_points, optimal_score):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, model.room.width)
    ax.set_ylim(0, model.room.height)
    for f in model.room.furniture:
        x, y = f.polygon.exterior.xy
        ax.fill(x, y, alpha=0.4, label=f.name)
    ax.scatter(measurement_points[:, 0], measurement_points[:, 1], c='red', marker='x', s=100, label="Test Points")
    for i, (x, y) in enumerate(measurement_points):
        ax.text(x, y + 0.1, str(i+1), color='blue', fontsize=10, ha='center')
    router_plot = ax.scatter(initial_router_pos[0], initial_router_pos[1], c='white', edgecolors='black', s=200, label="Router")
    ax.set_title("Wi-Fi Router Optimizasyonu")
    ax.legend()
    ax.grid(True)

    def onclick(event):
        if not event.inaxes:
            return
        new_pos = np.array([event.xdata, event.ydata])
        router_plot.set_offsets([new_pos])
        new_signals = [model.calculate_signal_strength(new_pos, p) for p in measurement_points]
        penalty = np.sum(np.array(new_signals) < -65)
        mean_dbm = np.mean(new_signals)
        std_dbm = np.std(new_signals)
        score = ((mean_dbm + 100) / 10) - 0.2 * std_dbm - 0.5 * penalty
        score = max(0, min(10, score))
        print(f"\nYeni Router Konumu: ({new_pos[0]:.2f}, {new_pos[1]:.2f})")
        for i, sig in enumerate(new_signals):
            print(f"  Nokta {i+1}: {sig:.2f} dBm")
        print(f"  Bu konumun puanı: {score:.2f} / 10")
        print(f"  Optimize konum puanı: {optimal_score:.2f} / 10")
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.tight_layout()
    plt.show()

def generate_word_report(optimal_pos, optimal_signals):
    doc = Document()
    doc.add_heading("WiFi Router Optimization Report", 0)
    doc.add_paragraph(f"Optimal Router Position: {optimal_pos}")
    doc.add_paragraph("Signal Strengths:")
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Point"
    table.rows[0].cells[1].text = "Signal (dBm)"
    for i, s in enumerate(optimal_signals):
        row = table.add_row().cells
        row[0].text = f"Point {i+1}"
        row[1].text = f"{s:.2f}"
    doc.save("wifi_report.docx")

def generate_pdf_report(optimal_pos, optimal_signals):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "WiFi Optimization Report", ln=True, align='C')
    pdf.cell(200, 10, f"Optimal Router Position: {optimal_pos}", ln=True)
    pdf.ln(5)
    for i, s in enumerate(optimal_signals):
        pdf.cell(200, 10, f"Point {i+1}: {s:.2f} dBm", ln=True)
    pdf.output("wifi_report.pdf")

def plot_open3d(room, router_pos, measurement_points):
    geometries = []
    for f in room.furniture:
        x, y = f.polygon.exterior.xy
        box = o3d.geometry.TriangleMesh.create_box(width=np.ptp(x), height=np.ptp(y), depth=1)
        box.translate([np.min(x), np.min(y), 0])
        box.paint_uniform_color([0.7, 0.7, 0.7])
        geometries.append(box)
    sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.2)
    sphere.translate([router_pos[0], router_pos[1], 1])
    sphere.paint_uniform_color([1, 0, 0])
    geometries.append(sphere)
    points = o3d.geometry.PointCloud()
    points.points = o3d.utility.Vector3dVector(np.c_[measurement_points[:, 0], measurement_points[:, 1], [0.5]*len(measurement_points)])
    points.paint_uniform_color([0, 0, 1])
    geometries.append(points)
    o3d.visualization.draw_geometries(geometries)

def plot_plotly(room, router_pos, measurement_points):
    fig = go.Figure()
    for f in room.furniture:
        x, y = f.polygon.exterior.xy
        fig.add_trace(go.Mesh3d(x=list(x), y=list(y), z=[0]*len(x), color='lightgrey', opacity=0.5))
    fig.add_trace(go.Scatter3d(x=[router_pos[0]], y=[router_pos[1]], z=[1], mode='markers',
                               marker=dict(size=6, color='red'), name='Router'))
    fig.add_trace(go.Scatter3d(x=measurement_points[:, 0], y=measurement_points[:, 1], z=[0.5]*len(measurement_points),
                               mode='markers', marker=dict(size=5, color='blue'), name='Test Points'))
    fig.update_layout(title="3D Room - Plotly", scene=dict(xaxis_title='Width', yaxis_title='Height', zaxis_title='Z'))
    fig.show()

def plot_vedo(room, router_pos, measurement_points):
    plt3d = Plotter()
    for f in room.furniture:
        x, y = f.polygon.exterior.xy
        box = Box(pos=(np.mean(x), np.mean(y), 0.5), length=np.ptp(x), width=np.ptp(y), height=1,
                  c='lightgrey', alpha=0.5)
        plt3d += box
    router = Sphere(pos=(router_pos[0], router_pos[1], 1), r=0.2, c='red')
    points = Points([(*p, 0.5) for p in measurement_points], r=10, c='blue')
    plt3d += router + points
    plt3d.show(title="3D Room - Vedo")

def plot_pyvista(room, router_pos, measurement_points):
    pvplt = pv.Plotter()
    for f in room.furniture:
        x, y = f.polygon.exterior.xy
        base = pv.PolyData(np.c_[x, y, np.zeros(len(x))])
        wall = base.delaunay_2d().extrude((0, 0, 1), capping=True)
        pvplt.add_mesh(wall, color="lightgrey", opacity=0.5)
    pvplt.add_mesh(pv.Sphere(center=(router_pos[0], router_pos[1], 1), radius=0.2), color="red")
    pvplt.add_points(np.c_[measurement_points[:, 0], measurement_points[:, 1], [0.5]*len(measurement_points)],
                     color="blue", point_size=10)
    pvplt.show(title="3D Room - PyVista")

def main():
    print("1. Basladi") 
    room = setup_room()
    print("2. Oda kuruldu")  

    points = generate_measurement_points(room)
    print("3. Test noktalari olusturuldu")  

    model = WiFiPropagationModel(room)
    print("4. Model olusturuldu")  

    opt_pos = optimize_router_position(model, points)
    print(f"5. En iyi router pozisyonu bulundu: {opt_pos}") 

    opt_signals = [model.calculate_signal_strength(opt_pos, p) for p in points]
    print("6. Optimize edilmis sinyaller hesaplandi")  

    penalty = np.sum(np.array(opt_signals) < -65)
    mean_dbm = np.mean(opt_signals)
    std_dev = np.std(opt_signals)
    score = ((mean_dbm + 100) / 10) - 0.2 * std_dev - 0.5 * penalty
    score = max(0, min(10, score))

    print(f" Optimize konum puani: {score:.2f} / 10")

    print("7. Interaktif ekran basliyor...")  
    show_interactive_with_score(model, opt_pos, points, score)

 
    print("8. Isi haritasi basliyor...")    
    show_static_heatmap(model, opt_pos)

    print("9. Word/PDF raporu hazirlaniyor...")     
    generate_word_report(opt_pos, opt_signals)
    generate_pdf_report(opt_pos, opt_signals)

    print("10. 3D cizimler basliyor...")    
    plot_open3d(room, opt_pos, points)
    plot_plotly(room, opt_pos, points)
    plot_vedo(room, opt_pos, points)
    plot_pyvista(room, opt_pos, points)

if __name__ == "__main__":
    main()
