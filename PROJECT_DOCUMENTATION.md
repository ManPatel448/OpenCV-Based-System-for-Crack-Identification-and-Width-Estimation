# Crack Detaction - Project Documentation

## 1. Project overview

**Crack Detaction** is a Flask and OpenCV web application for detecting crack-like regions in uploaded images. It is designed for concrete, road, wall, and pavement image analysis.

The application:

- Accepts one or more JPG, JPEG, JFIF, or PNG images.
- Resizes images while preserving aspect ratio.
- Generates intermediate image-processing stages.
- Detects elongated crack candidates.
- Measures area, skeleton length, mean width, and maximum width.
- Converts pixel measurements to millimeters using the configured scale.
- Classifies measurements as `Good`, `Medium`, or `Heavy`.
- Displays results in a browser.
- Exports CSV, PDF, and ZIP reports.
- Stores records in MongoDB when available.
- Uses an in-memory fallback store when MongoDB is unavailable.

> **Important:** This is automated image analysis, not a certified structural safety assessment. Results must be reviewed by a qualified professional before making structural decisions.

## 2. Technology stack

| Area | Technology |
|---|---|
| Backend web framework | Flask 3 |
| Image processing | OpenCV |
| Numerical processing | NumPy |
| Skeleton and image algorithms | scikit-image |
| Tabular report generation | pandas |
| PDF generation | ReportLab |
| Database | MongoDB with PyMongo |
| Test database fallback | mongomock |
| Frontend | Server-rendered Jinja templates, Bootstrap 5, CSS, vanilla JavaScript |
| Runtime | Python 3.10 or newer |
| Testing | pytest |

## 3. Project structure

Generated and environment directories such as `.venv/`, `__pycache__/`, `.pytest_cache/`, and runtime `storage/` data are not source-code modules and should not be edited manually.

```text
Vs Project/
├── app.py
├── config.py
├── requirements.txt
├── pytest.ini
├── .env
├── run_crackscope.bat
├── README.md
├── PROJECT_DOCUMENTATION.md
│
├── models/
│   ├── __init__.py
│   ├── database.py
│   ├── analysis_model.py
│   ├── image_model.py
│   └── measurement_model.py
│
├── routes/
│   ├── __init__.py
│   ├── upload_routes.py
│   ├── analysis_routes.py
│   ├── history_routes.py
│   └── report_routes.py
│
├── services/
│   ├── __init__.py
│   ├── calibration_service.py
│   ├── classification_service.py
│   ├── csv_service.py
│   ├── detection_service.py
│   ├── image_service.py
│   ├── measurement_service.py
│   ├── pdf_service.py
│   ├── preprocessing_service.py
│   ├── storage_service.py
│   └── zip_service.py
│
├── utils/
│   ├── __init__.py
│   ├── file_utils.py
│   └── validators.py
│
├── templates/
│   ├── base.html
│   ├── upload.html
│   ├── results.html
│   ├── history.html
│   ├── reports.html
│   └── analysis_not_found.html
│
├── static/
│   ├── app.css
│   └── app.js
│
└── tests/
    ├── test_app.py
    └── test_processing.py
```

## 4. Application startup

The application entry point is `app.py`.

`create_app()`:

1. Creates the Flask application.
2. Loads the `Config` class.
3. Creates the configured storage directory.
4. Creates the main storage subdirectories.
5. Initializes MongoDB or the fallback store.
6. Registers upload, analysis, history, and report blueprints.
7. Registers JSON handling for upload-size errors.
8. Registers the favicon and 404 handlers.

The direct script entry point starts Flask on:

```text
http://127.0.0.1:5000
```

The root route redirects to `/upload`.

## 5. Configuration

Configuration is defined in `config.py`. Environment variables are loaded using `python-dotenv`.

| Setting | Environment variable | Default |
|---|---|---|
| Flask secret | `FLASK_SECRET_KEY` | Development-only key |
| MongoDB URI | `MONGO_URI` | `mongodb://localhost:27017` |
| MongoDB database | `MONGO_DB_NAME` | `crack_detection_db` |
| Maximum request size | `MAX_CONTENT_LENGTH` | 16 MB |
| Storage directory | `STORAGE_DIR` | `<project>/storage` |
| Allowed extensions | Code setting | jpg, jpeg, jfif, png |
| Maximum files per analysis | Code setting | 20 |
| Maximum image dimension | Code setting | 8000 pixels |
| Default pixels per millimeter | Code setting | 10.0 |

Processing configuration includes:

- Resize maximum dimension: `1600`
- Gaussian kernel: `5`
- CLAHE clip limit: `2.0`
- CLAHE tile grid: `8`
- BlackHat kernel: `21`
- Morphology kernel: `3`
- Morphology iterations: `1`
- Minimum connected-component area: `30`
- Minimum crack aspect ratio: `3.0`
- Maximum crack components: `60`
- Maximum crack coverage: `0.08`
- Crack severity thresholds:
  - Good: mean width up to `3 px`
  - Medium: mean width above `3 px` and up to `8 px`
  - Heavy: mean width above `8 px` or area at least `5000 px²`

## 6. Frontend structure

### `templates/base.html`

Shared layout for all pages.

Responsibilities:

- Sets the document title.
- Loads Bootstrap.
- Loads `static/app.css`.
- Displays the `Crack Detaction` navigation bar.
- Loads `static/app.js`.
- Provides the image lightbox markup.

### `templates/upload.html`

Upload page.

Responsibilities:

- Provides a multi-file image input.
- Allows drag-and-drop selection.
- Shows image previews.
- Submits the upload form through frontend JavaScript.
- Displays upload and processing status.

### `templates/results.html`

Completed analysis page.

Displays:

- Analysis name and status.
- Calibration information.
- Summary values.
- Severity distribution.
- Automated remark.
- Severity thresholds.
- Download buttons for CSV, PDF, and ZIP.
- Original image.
- Annotated image.
- Final segmentation mask.
- Intermediate processing stages.
- Skeleton, distance-transform, and width-estimation images.
- Detailed crack measurements.

### `templates/history.html`

Displays previously persisted analyses from the history route.

Each row includes:

- Analysis name.
- Creation time.
- Image count.
- Detected region count.
- Status.
- Link to the analysis page.

### `templates/reports.html`

Provides a reports landing page and links to analysis history.

### `templates/analysis_not_found.html`

Shown when an analysis ID is unavailable in the active MongoDB or fallback session.

### `static/app.js`

Client-side behavior includes:

- File preview generation.
- Upload form submission.
- Upload status updates.
- Redirecting to the completed analysis page.
- Image preview/lightbox behavior.
- Zoom controls.

### `static/app.css`

Contains project-specific styling for:

- Upload drop zone.
- Result cards.
- Image grids.
- Workflow timing labels.
- Result images.
- Lightbox presentation.

## 7. Backend routes

### Upload routes

Defined in `routes/upload_routes.py`.

| Method | URL | Purpose |
|---|---|---|
| GET | `/upload` | Render upload page |
| POST | `/api/upload` | Validate, save, process, and return an analysis |
| POST | `/api/analyze` | Compatibility endpoint for upload validation/tests |

Upload validation checks:

1. At least one file is present.
2. The file count does not exceed `MAX_FILES_PER_ANALYSIS`.
3. The extension is allowed.
4. The file is not empty.
5. The upload satisfies the configured size constraints.

### Analysis routes

Defined in `routes/analysis_routes.py`.

| Method | URL | Purpose |
|---|---|---|
| GET | `/analysis/<analysis_id>` | Render the result page |
| GET | `/api/analysis/<analysis_id>` | Return serialized analysis JSON |
| GET | `/files/<analysis_id>/<image_id>/original` | Serve the original image |
| GET | `/files/<analysis_id>/<image_id>/annotated` | Serve the annotated image |
| GET | `/files/<analysis_id>/<image_id>/processed/<stage>` | Serve a processed stage |

File routes validate that the requested file remains inside the analysis storage directory. This prevents arbitrary path access through image URLs.

### History routes

Defined in `routes/history_routes.py`.

The history page lists persisted analyses using the model layer. It supports viewing stored analyses when MongoDB is configured and available.

### Report routes

Defined in `routes/report_routes.py`.

| Method | URL | Purpose |
|---|---|---|
| GET | `/reports` | Render reports landing page |
| GET | `/reports/<analysis_id>/csv` | Generate and download CSV |
| GET | `/reports/<analysis_id>/pdf` | Generate and download PDF |
| GET | `/reports/<analysis_id>/zip` | Generate and download complete ZIP |

Reports are generated on demand. The ZIP route first generates CSV and PDF, creates a manifest, then packages the complete analysis directory.

## 8. Complete image-processing workflow

The main processing pipeline is implemented in `routes/upload_routes.py` and delegates individual operations to services.

### Step 1: Create analysis

The server generates a UUID-based analysis ID and creates an analysis record containing:

- Analysis ID.
- Analysis name.
- Created and updated timestamps.
- Status.
- Image count.
- Calibration state.
- Pixels-per-millimeter value.
- Processing configuration.
- Severity thresholds.

### Step 2: Save original images

Each uploaded file is saved using a safe filename. An image record stores:

- Image ID.
- Analysis ID.
- Original filename.
- Stored filename.
- Original path.
- Upload timestamp.
- Processing status.

### Step 3: Load and resize

`services/image_service.py` reads the image with OpenCV and resizes it to the configured maximum dimension while preserving aspect ratio.

### Step 4: Preprocess

`services/preprocessing_service.py` performs:

1. BGR to grayscale conversion.
2. Gaussian blur.
3. CLAHE contrast enhancement.
4. BlackHat morphology to emphasize dark crack-like regions.
5. Otsu binary thresholding.

The generated stages are stored as PNG files.

### Step 5: Detect components

`services/detection_service.py`:

1. Applies morphological opening.
2. Applies morphological closing.
3. Finds connected components.
4. Removes components below the minimum area.
5. Calculates contour and mask data.

### Step 6: Filter crack candidates

Candidate regions are evaluated using:

- Minimum-area filtering.
- Rotated-rectangle aspect ratio.
- Principal-axis ratio using singular value decomposition.

Thin or elongated components are retained as crack candidates. Generic rounded blobs are rejected.

### Step 7: Validate the image

The image is rejected if it does not contain a plausible crack path.

Validation considers:

- Number of components.
- Total crack coverage.
- Component alignment.
- Dominant component area ratio.
- Dominant component aspect ratio.
- Fragmented crack alignment.

### Step 8: Measure cracks

`services/measurement_service.py` calculates:

- Contour area in pixels.
- Skeleton length in pixels.
- Mean crack width.
- Maximum crack width.
- Measurement sample count.
- Measurement points.
- Millimeter values when calibration is enabled.

Each measurement receives a crack ID.

### Step 9: Classify severity

`services/classification_service.py` assigns:

- `Good`
- `Medium`
- `Heavy`

Classification is based on configured width and area thresholds.

### Step 10: Generate visual evidence

For each image, the application saves:

- Resized image.
- Grayscale image.
- Blurred image.
- CLAHE image.
- BlackHat image.
- Binary image.
- Cleaned mask.
- Segmentation mask.
- Skeleton images.
- Distance-transform images.
- Width-estimation images.
- Annotated image.

### Step 11: Store measurements

After all images pass processing, measurements are written to MongoDB or the fallback store.

### Step 12: Complete the analysis

The analysis status changes from:

```text
Uploaded -> Processing -> Completed
```

If an image fails validation or processing, the analysis records and generated storage are removed and an error is returned.

## 9. Data model

### Analysis document

Typical fields:

```text
analysis_id
analysis_name
notes
created_at
updated_at
status
total_images
total_detected_regions
calibration_enabled
pixels_per_mm
processing_configuration
severity_thresholds
error_summary
```

### Image document

Typical fields:

```text
image_id
analysis_id
original_filename
stored_filename
original_path
uploaded_at
processing_status
image_width
image_height
resize_scale
processed_paths
annotated_path
workflow_times
error_message
```

### Measurement document

Typical fields:

```text
analysis_id
image_id
crack_id
contour_area_px
contour_area_mm2
skeleton_length_px
skeleton_length_mm
mean_width_px
mean_width_mm
max_width_px
max_width_mm
width_sample_count
measurement_points
calibration_status
severity
created_at
```

## 10. Database behavior

`models/database.py` attempts to connect to MongoDB during application startup.

When MongoDB is available:

- Analysis records use `analyses`.
- Image records use `images`.
- Measurements use `crack_measurements`.
- Report history indexes use `report_history`.

When MongoDB is unavailable:

- The application does not stop startup.
- Records are kept in `app.extensions["fallback_store"]`.
- Data remains available during the current Flask process.
- Data is lost when the process restarts.

MongoDB indexes include:

- Unique `analysis_id`.
- Analysis/image upload ordering.
- Analysis/image measurement lookup.
- Analysis/report generation lookup.

## 11. Storage layout

Each analysis is stored under:

```text
storage/
└── analyses/
    └── <analysis_id>/
        ├── original_images/
        ├── processed_images/
        ├── annotated_images/
        └── reports/
            ├── <analysis_id>.csv
            ├── <analysis_id>.pdf
            ├── <analysis_id>_manifest.txt
            └── <analysis_id>.zip
```

The ZIP report includes:

- Original images.
- Processed images.
- Annotated images.
- CSV report.
- PDF report.
- Complete package manifest.

The ZIP implementation excludes the ZIP file itself and avoids duplicate report entries.

## 12. Report generation

### CSV report

Generated by `services/csv_service.py`.

The CSV combines:

- Analysis metadata.
- Image metadata.
- Crack measurements.
- Calibration values.
- Severity values.
- Summary counts.
- Summary remark.

### PDF report

Generated by `services/pdf_service.py` using ReportLab.

The PDF contains:

1. Report title and metadata.
2. Analysis date and time.
3. Report generation date and time.
4. Crack analysis summary.
5. Calibration and severity thresholds.
6. Numbered processing workflow.
7. Workflow timings.
8. Crack measurement table.
9. Width measurement table.
10. Numbered standalone image-processing evidence.
11. Assessment notes.

Each evidence item includes:

- Evidence number.
- Processing stage.
- Source filename.
- Large standalone image.

The PDF uses `KeepTogether` for section headings and tables so a page break does not leave a table title separated from its table.

### ZIP report

Generated by `services/zip_service.py` and `routes/report_routes.py`.

The ZIP process:

1. Loads the analysis.
2. Loads all images.
3. Loads all measurements.
4. Generates the CSV.
5. Generates the PDF.
6. Generates a text manifest.
7. Adds all analysis files.
8. Excludes the ZIP currently being created.
9. Removes duplicate archive names.

## 13. Model files

### `models/database.py`

Initializes MongoDB and manages the fallback store.

### `models/analysis_model.py`

Provides analysis creation, lookup, update, listing, timestamps, and deletion.

### `models/image_model.py`

Provides image creation, listing, and updates.

### `models/measurement_model.py`

Provides measurement insertion, listing, and calibration updates.

## 14. Service files

| File | Responsibility |
|---|---|
| `calibration_service.py` | Pixel-to-millimeter calibration helpers |
| `classification_service.py` | Severity classification |
| `csv_service.py` | CSV export |
| `detection_service.py` | Connected components, crack filtering, image validation |
| `image_service.py` | Image loading, resizing, and writing |
| `measurement_service.py` | Skeleton, width, annotation, and measurement calculations |
| `pdf_service.py` | PDF layout, tables, metadata, and evidence |
| `preprocessing_service.py` | Grayscale, blur, CLAHE, BlackHat, and thresholding |
| `storage_service.py` | Analysis directory creation and removal |
| `zip_service.py` | Manifest and ZIP package generation |

## 15. Utility files

### `utils/file_utils.py`

Contains safe filename and path containment helpers.

### `utils/validators.py`

Validates uploaded files and upload constraints.

## 16. Installation

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create the environment file:

```powershell
Copy-Item .env.example .env
```

If `.env.example` is not present, create `.env` manually:

```dotenv
FLASK_SECRET_KEY=replace-with-a-random-secret
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=crack_detection_db
STORAGE_DIR=storage
```

## 17. Running the project

### Manual start

```powershell
.\.venv\Scripts\python.exe app.py
```

Open:

```text
http://127.0.0.1:5000
```

### Windows launcher

Run:

```text
run_crackscope.bat
```

The launcher:

1. Checks for Python.
2. Creates the virtual environment if required.
3. Installs dependencies.
4. Starts Flask.
5. Waits for the server.
6. Opens the browser.

## 18. Testing

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite covers:

- ZIP self-exclusion.
- Duplicate ZIP report prevention.
- Empty upload rejection.
- Invalid extension rejection.
- Image-processing behavior.
- Detection and measurement behavior.

Compile application modules:

```powershell
.\.venv\Scripts\python.exe -m compileall -q app.py routes services models utils
```

## 19. Error handling

The application returns clear errors for:

- Missing files.
- Too many files.
- Unsupported file extensions.
- Oversized requests.
- Missing analyses.
- Unknown report types.
- Failed image processing.
- Images without detectable crack regions.

The upload route reports the affected filename when processing fails.

## 20. Security and reliability notes

- Uploaded filenames are sanitized before storage.
- File-serving routes restrict access to the current analysis directory.
- Report routes only allow `csv`, `pdf`, and `zip`.
- MongoDB connection failures fall back gracefully for the current process.
- The default Flask secret is intended only for development and should be replaced.
- Production deployments should use a production WSGI server.
- Production deployments should configure MongoDB and persistent storage.
- Uploaded image content should be treated as untrusted input.
- Processing limits should be kept enabled to protect memory and CPU resources.

## 21. Known limitations

- The fallback store is not persistent.
- Detection quality depends on lighting, contrast, texture, camera angle, and image quality.
- Pixel-to-millimeter accuracy depends on the configured calibration.
- Automated severity is a software category, not a structural certification.
- The project currently uses synchronous image processing inside the Flask request.
- Large batches may require background workers in a production deployment.

## 22. Recommended production improvements

For a production deployment, consider:

1. Use Gunicorn, Waitress, or another production WSGI server.
2. Move image processing to a background task queue.
3. Store uploaded files in object storage.
4. Add authentication and authorization.
5. Add rate limiting.
6. Add structured logging.
7. Add monitoring and alerting.
8. Add database migrations or versioned schema management.
9. Add automated browser tests for upload and report downloads.
10. Add a configurable timezone for report display.
11. Add retention policies for old analysis directories.
12. Add stronger image integrity and content validation.

## 23. End-to-end request flow

```text
Browser
  |
  | GET /upload
  v
Upload page
  |
  | POST /api/upload
  v
Upload validation
  |
  v
Create analysis and image records
  |
  v
Load and resize image
  |
  v
Preprocess image
  |
  v
Detect and filter crack components
  |
  v
Measure and classify cracks
  |
  v
Write original, processed, and annotated files
  |
  v
Store measurements
  |
  v
Return analysis ID
  |
  v
GET /analysis/<analysis_id>
  |
  v
Results page
  |
  +--> GET /reports/<analysis_id>/csv
  |
  +--> GET /reports/<analysis_id>/pdf
  |
  +--> GET /reports/<analysis_id>/zip
```

## 24. Maintenance checklist

Before changing the project:

- Read the affected route, service, model, and template.
- Preserve the fallback-store behavior.
- Keep uploaded-file validation enabled.
- Keep path containment checks on file-serving routes.
- Run `pytest -q`.
- Run Python compilation.
- Test at least one real PDF and ZIP generation path.
- Check that report files are not duplicated in ZIP archives.
- Check that frontend links match backend routes.
- Update this document when the architecture or file responsibilities change.

