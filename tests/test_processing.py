import cv2
import numpy as np

from services.calibration_service import convert_pixels, validate_pixels_per_mm
from services.classification_service import classify
from services.detection_service import detect_components, filter_crack_components, validate_crack_image
from services.measurement_service import measure_component
from services.preprocessing_service import preprocess


CONFIG = {"gaussian_kernel": 5, "clahe_clip_limit": 2, "clahe_tile_grid": 8, "blackhat_kernel": 21,
          "morphology_kernel": 3, "morphology_iterations": 1, "minimum_region_area": 10}


def test_pipeline_detects_synthetic_dark_crack():
    image = np.full((220, 220, 3), 210, dtype=np.uint8)
    cv2.line(image, (25, 30), (190, 180), (20, 20, 20), 5)
    stages = preprocess(image, CONFIG)
    _, _, components = detect_components(stages["binary"], CONFIG)
    assert components
    assert filter_crack_components(components, CONFIG)
    assert validate_crack_image(filter_crack_components(components, CONFIG), image.shape, CONFIG)
    result = measure_component(components[0], 10)
    assert result["skeleton_length_px"] > 0
    assert result["skeleton_length_mm"] is not None


def test_calibration_and_classification():
    assert validate_pixels_per_mm("4") == 4
    assert validate_pixels_per_mm("0") is None
    assert convert_pixels(20, 4) == 5
    assert classify(10, 1) == "Good"
    assert classify(10, 4) == "Medium"
    assert classify(6000, 1) == "Heavy"


def test_validation_rejects_round_non_crack_region():
    image = np.full((220, 220, 3), 210, dtype=np.uint8)
    cv2.circle(image, (110, 110), 35, (20, 20, 20), -1)
    stages = preprocess(image, CONFIG)
    _, _, components = detect_components(stages["binary"], CONFIG)
    assert not filter_crack_components(components, CONFIG)


def test_validation_rejects_text_heavy_image():
    image = np.full((220, 220, 3), 210, dtype=np.uint8)
    for y in range(20, 210, 20):
        cv2.putText(image, "TEXT", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (20, 20, 20), 1)
    stages = preprocess(image, CONFIG)
    _, _, components = detect_components(stages["binary"], CONFIG)
    filtered = filter_crack_components(components, CONFIG)
    assert not validate_crack_image(filtered, image.shape, CONFIG)


def test_validation_allows_fragmented_dominant_crack():
    image = np.full((220, 220, 3), 210, dtype=np.uint8)
    for start, end in [((15, 110), (70, 100)), ((75, 98), (130, 80)), ((135, 78), (205, 45))]:
        cv2.line(image, start, end, (20, 20, 20), 4)
    stages = preprocess(image, {**CONFIG, "maximum_crack_components": 1, "maximum_crack_coverage": 0.001})
    _, _, components = detect_components(stages["binary"], {**CONFIG, "maximum_crack_components": 1})
    filtered = filter_crack_components(components, CONFIG)
    assert validate_crack_image(filtered, image.shape, {**CONFIG, "maximum_crack_components": 1, "maximum_crack_coverage": 0.001})


def test_validation_rejects_dispersed_portrait_like_regions():
    image = np.full((220, 220, 3), 210, dtype=np.uint8)
    for x, y in ((30, 30), (110, 35), (185, 45), (40, 150), (120, 140), (195, 165)):
        cv2.line(image, (x, y), (x + 15, y + 4), (20, 20, 20), 4)
    stages = preprocess(image, CONFIG)
    _, _, components = detect_components(stages["binary"], CONFIG)
    filtered = filter_crack_components(components, CONFIG)
    assert not validate_crack_image(
        filtered,
        image.shape,
        {**CONFIG, "maximum_crack_components": 1, "maximum_crack_coverage": 0.001},
    )
