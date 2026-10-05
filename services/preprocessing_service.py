import cv2


def preprocess(image, config):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel_size = int(config["gaussian_kernel"])
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    clahe = cv2.createCLAHE(
        clipLimit=float(config["clahe_clip_limit"]),
        tileGridSize=(int(config["clahe_tile_grid"]), int(config["clahe_tile_grid"])),
    )
    enhanced = clahe.apply(blurred)
    k = int(config["blackhat_kernel"])
    blackhat = cv2.morphologyEx(enhanced, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    _, binary = cv2.threshold(blackhat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return {"gray": gray, "blurred": blurred, "clahe": enhanced, "blackhat": blackhat, "binary": binary}
