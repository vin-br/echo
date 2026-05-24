# Data

## Classification

Curated 4-class brain tumor MRI dataset (cleaned from the original Kaggle source).

```
data/classification/
├── train/
│   ├── glioma_tumor/
│   ├── meningioma_tumor/
│   ├── no_tumor/
│   └── pituitary_tumor/
└── test/
    ├── glioma_tumor/
    ├── meningioma_tumor/
    ├── no_tumor/
    └── pituitary_tumor/
```

## Detection

3-class brain tumor bounding-box detection (YOLOv8 format):

```
data/detection/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```
