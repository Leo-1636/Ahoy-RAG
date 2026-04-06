from ultralytics import YOLO

model = YOLO("DLA.pt")

results = model(["test1.png", "test2.png", "test3.png"])

all_results = [result.boxes.data.tolist() for result in results]

print(all_results)
print(len(all_results))

results = model("test1.png")

print(results[0].boxes.data.tolist())

results = model("test2.png")

print(results[0].boxes.data.tolist())

import json
from pathlib import Path
if not Path("test.json").exists():
    data = []
else:
    with Path("test.json").open("r", encoding = "utf-8") as file:
        data = json.load(file)

print(data)