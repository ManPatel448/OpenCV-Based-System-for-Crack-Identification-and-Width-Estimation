import cv2
import numpy as np


def detect_components(binary, config):
    k = int(config["morphology_kernel"])
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    iterations = int(config["morphology_iterations"])
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=iterations)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned, 8)
    minimum = int(config["minimum_region_area"])
    mask = np.zeros_like(cleaned)
    components = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < minimum:
            continue
        component_mask = np.where(labels == label, 255, 0).astype(np.uint8)
        contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        components.append({"label": label, "area": area, "mask": component_mask, "contour": max(contours, key=cv2.contourArea)})
        mask[labels == label] = 255
    return cleaned, mask, components


def filter_crack_components(components, config):
    """Keep thin, elongated regions and reject generic blobs from ordinary photos."""
    minimum_aspect = float(config.get("minimum_crack_aspect_ratio", 3.0))
    crack_components = []
    for component in components:
        _, (width, height), _ = cv2.minAreaRect(component["contour"])
        short_side = min(width, height)
        aspect_ratio = max(width, height) / max(short_side, 1.0)
        points = np.argwhere(component["mask"] > 0)
        if len(points) < 2:
            continue
        _, singular_values, _ = np.linalg.svd(points - points.mean(axis=0), full_matrices=False)
        principal_ratio = float(singular_values[0] / max(singular_values[1], 1e-6))
        if aspect_ratio >= minimum_aspect or principal_ratio >= minimum_aspect:
            crack_components.append(component)
    return crack_components


def validate_crack_image(components, image_shape, config):
    """Reject unrelated images while allowing fragmented, dominant crack paths."""
    if not components:
        return False
    max_components = int(config.get("maximum_crack_components", 60))
    max_coverage = float(config.get("maximum_crack_coverage", 0.08))
    image_area = max(1, image_shape[0] * image_shape[1])
    coverage = sum(component["area"] for component in components) / image_area
    alignment_ratio = _component_alignment_ratio(components)
    dispersed_limit = int(config.get("maximum_dispersed_components", 8))
    if len(components) <= max_components and coverage <= max_coverage and (
        len(components) <= dispersed_limit
        or alignment_ratio >= float(config.get("minimum_crack_path_alignment", 3.0))
    ):
        return True

    dominant = max(components, key=lambda component: component["area"])
    _, (width, height), _ = cv2.minAreaRect(dominant["contour"])
    short_side = min(width, height)
    dominant_aspect = max(width, height) / max(short_side, 1.0)
    dominant_area_ratio = dominant["area"] / image_area
    return (
        dominant_area_ratio >= float(config.get("minimum_dominant_crack_area_ratio", 0.002))
        and dominant_aspect >= float(config.get("minimum_dominant_crack_aspect_ratio", 5.0))
        and alignment_ratio >= float(config.get("minimum_fragmented_crack_alignment", 3.0))
        and coverage <= float(config.get("maximum_fragmented_crack_coverage", 0.15))
    )


def _component_alignment_ratio(components):
    centers = []
    for component in components:
        ys, xs = np.where(component["mask"] > 0)
        if len(xs):
            centers.append((float(xs.mean()), float(ys.mean())))
    if len(centers) <= 3:
        return float("inf")
    _, values, _ = np.linalg.svd(np.asarray(centers) - np.mean(centers, axis=0), full_matrices=False)
    return float(values[0] / max(values[1], 1e-6))
