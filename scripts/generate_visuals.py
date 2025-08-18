import os
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path('assets')
ASSETS_DIR.mkdir(exist_ok=True)

SERVICES = [
    ('api_gateway', []),
    ('database_service', []),
    ('user_service', ['database_service']),
    ('payment_service', ['database_service']),
    ('echo_service', []),
]

COLORS = {
    'healthy': '#2ecc71',  # green
    'unhealthy': '#e74c3c',  # red
    'neutral': '#95a5a6',
}


def draw_dependency_graph(filename: str, unhealthy=None):
    unhealthy = set(unhealthy or [])
    G = nx.DiGraph()
    for svc, deps in SERVICES:
        G.add_node(svc)
        for d in deps:
            G.add_edge(svc, d)

    pos = {
        'api_gateway': (0.0, 0.8),
        'user_service': (-0.6, 0.2),
        'payment_service': (0.6, 0.2),
        'database_service': (0.0, -0.4),
        'echo_service': (1.2, -0.4),
    }

    node_colors = [COLORS['unhealthy'] if n in unhealthy else COLORS['healthy'] for n in G.nodes()]

    plt.figure(figsize=(8, 5))
    nx.draw_networkx(
        G,
        pos=pos,
        node_color=node_colors,
        edge_color='#34495e',
        arrows=True,
        with_labels=True,
        font_size=9,
        node_size=1800,
    )
    plt.axis('off')
    out_path = ASSETS_DIR / filename
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved {out_path}")


def draw_port_in_use_modal(filename: str, port: int = 8002, pid: int = 12345, cmdline: str = 'python services/database_service.py'):
    w, h = 900, 520
    img = Image.new('RGB', (w, h), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Backdrop overlay rectangle
    overlay_color = (0, 0, 0, 60)

    # Modal box
    box_w, box_h = 720, 320
    box_x = (w - box_w) // 2
    box_y = (h - box_h) // 2
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=16, fill=(255, 255, 255), outline=(200, 200, 200))

    # Text
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    title = f"Port {port} is already in use"
    draw.text((box_x + 24, box_y + 20), title, font=font_title, fill=(34, 34, 34))

    lines = [
        ("Service:", "database_service"),
        ("Port:", str(port)),
        ("PID:", str(pid)),
        ("Command:", cmdline),
    ]

    y = box_y + 70
    for key, val in lines:
        draw.text((box_x + 24, y), f"{key}", font=font_text, fill=(90, 90, 90))
        draw.text((box_x + 160, y), val, font=font_text, fill=(20, 20, 20))
        y += 36

    # Buttons
    btn_w, btn_h, gap = 160, 44, 16
    btn2_x = box_x + box_w - 24 - btn_w
    btn1_x = btn2_x - gap - btn_w
    btn_y = box_y + box_h - 24 - btn_h

    draw.rounded_rectangle([btn1_x, btn_y, btn1_x + btn_w, btn_y + btn_h], radius=8, fill=(230, 230, 230), outline=(180, 180, 180))
    draw.text((btn1_x + 26, btn_y + 12), "Cancel", font=font_text, fill=(50, 50, 50))

    draw.rounded_rectangle([btn2_x, btn_y, btn2_x + btn_w, btn_y + btn_h], radius=8, fill=(192, 57, 43), outline=(142, 27, 23))
    draw.text((btn2_x + 10, btn_y + 12), "Force Kill & Retry", font=font_text, fill=(255, 255, 255))

    out_path = ASSETS_DIR / filename
    img.save(out_path)
    print(f"Saved {out_path}")


def draw_one_brain_arch(filename: str):
    w, h = 900, 520
    img = Image.new('RGB', (w, h), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    draw.text((24, 20), "One Brain Architecture", font=font_title, fill=(34, 34, 34))

    # Nodes
    monitor_box = (360, 200, 540, 270)
    dash_box = (80, 200, 240, 270)
    svc_boxes = [
        (660, 120, 840, 170, 'api_gateway'),
        (660, 180, 840, 230, 'database_service'),
        (660, 240, 840, 290, 'user_service'),
        (660, 300, 840, 350, 'payment_service'),
        (660, 360, 840, 410, 'echo_service'),
    ]

    def box(rect, label, fill=(245,245,245)):
        draw.rounded_rectangle(rect, radius=10, fill=fill, outline=(200,200,200))
        x1, y1, x2, y2 = rect
        draw.text((x1 + 12, y1 + 10), label, font=font_text, fill=(20,20,20))

    box(dash_box, 'Dashboard (UI)')
    box(monitor_box, 'Monitor (one brain)', fill=(235, 247, 255))
    for x1,y1,x2,y2,name in svc_boxes:
        box((x1,y1,x2,y2), name)

    # Arrows
    def arrow(from_xy, to_xy, color=(52,73,94)):
        draw.line([from_xy, to_xy], fill=color, width=3)
        # simple arrow head
        hx, hy = to_xy
        draw.polygon([(hx, hy), (hx-8, hy-4), (hx-8, hy+4)], fill=color)

    # UI -> Monitor (actions)
    arrow((240, 235), (360, 235))
    draw.text((260, 210), "actions", font=font_text, fill=(80,80,80))
    # Monitor -> Services (control)
    for x1,y1,x2,y2,name in svc_boxes:
        arrow((540, 235), (660, (y1+y2)//2))
    draw.text((560, 210), "control", font=font_text, fill=(80,80,80))
    # Monitor -> status.json (truth)
    box((360, 300, 540, 350), 'data/status.json', fill=(252, 247, 225))
    arrow((450, 270), (450, 300))

    out_path = ASSETS_DIR / filename
    img.save(out_path)
    print(f"Saved {out_path}")


def main():
    draw_dependency_graph('deps_overview.png', unhealthy=['database_service'])
    draw_port_in_use_modal('port_in_use.png', port=8002, pid=43210, cmdline='python services/database_service.py')
    draw_one_brain_arch('one_brain.png')
    print("All visuals generated in ./assets")


if __name__ == '__main__':
    main()
