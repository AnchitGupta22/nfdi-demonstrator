# Microstructure Thermal Conductivity Simulator API Documentation

## Overview

This FastAPI application provides a web interface and API for simulating thermal conductivity in binary microstructures. It enables users to upload images or draw microstructures and analyze their thermal properties. The application uses a physics-based simulation model and optionally a faster surrogate model for predicting effective thermal conductivity.

## Features

- Load and simulate thermal conductivity on pre-existing microstructure samples
- Upload custom images to use as microstructures for simulation
- Draw custom microstructures directly in the web interface
- Calculate effective thermal properties based on microstructure geometry
- Visualize temperature fields and heat flux
- Compare simulation results with analytical bounds (Reuss and Voigt)

## Technical Details

- **Framework**: FastAPI with Uvicorn server
- **Simulation Models**: PyTorch-based FNO-CG for thermal simulation
- **Optional**: Pre-trained surrogate model for faster predictions
- **Input Processing**: Handles image uploads and base64-encoded drawings
- **Hardware Acceleration**: Utilizes CUDA if available

## API Endpoints

### 1. GET `/api/info`

Returns basic information about the system.

**Response:**
```json
{
  "sample_count": 1000,
  "has_surrogate": true,
  "device": "cuda"
}
```

### 2. POST `/api/simulate`

Runs a thermal conductivity simulation on a microstructure from the pre-loaded dataset.

**Request Body (JSON):**
```json
{
  "ms_id": 42,      // Microstructure ID from dataset
  "kappa1": 10.0,   // Thermal conductivity ratio
  "alpha": 45.0     // Direction angle in degrees
}
```

**Response:** Detailed simulation results including temperature fields, heat flux, and effective properties.

### 3. POST `/api/upload-microstructure`

Processes an uploaded image as a microstructure and runs thermal simulation.

**Form Parameters:**
- `file`: Image file (JPG, PNG, BMP, GIF)
- `kappa1`: Thermal conductivity ratio (float > 0)
- `alpha`: Direction angle in degrees (0-90)

**Response:** Simulation results similar to `/api/simulate`.

### 4. POST `/api/process-drawing`

Processes a drawing from the web interface and runs thermal simulation.

**Form Parameters:**
- `drawing`: Base64-encoded image data
- `kappa1`: Thermal conductivity ratio (float > 0)
- `alpha`: Direction angle in degrees (0-90)

**Response:** Simulation results similar to `/api/simulate`.

## Simulation Parameters

- **kappa1**: Thermal conductivity ratio between phases. This represents how much more conductive the white phase is than the black phase.
- **alpha**: Direction angle in degrees (0-90), controlling the direction of the applied temperature gradient.

## Image Processing

The application processes images as follows:
- Converts to grayscale
- Resizes to 400x400 pixels
- Binarizes (threshold at 128) to create a two-phase microstructure
- Validates phase distribution (rejects completely white or black images)
- Warns if phase distribution is highly imbalanced (<5% or >95% white)

## Output Fields

The simulation results include:
- `image`: Binary microstructure representation
- `param_field`: Conductivity field
- `temp0`, `temp1`: Temperature fields for two loading cases
- `flux_norm0`, `flux_norm1`: Heat flux magnitude fields
- `vol_frac`: Volume fraction of the conductive phase
- `reuss`, `voigt`: Analytical bounds for effective conductivity
- `eig_kappa`: Eigenvalues of the effective conductivity tensor
- `surrogate_results`: Predictions from surrogate model (if available)

## Runtime Requirements

- Python 3.7+
- PyTorch with CUDA (recommended)
- FastAPI and Uvicorn
- Access to simulation models and dataset

## Deployment

The application runs on port 8000 by default and serves an HTML interface at the root path.

To start the server:
```
python main.py
```

## Error Handling

The API provides detailed error messages for:
- Invalid input parameters
- Image processing failures
- Simulation errors
- Invalid microstructures (e.g., single phase)

## Notes

- Simulations may be computationally intensive, especially on CPU
- The surrogate model provides faster predictions but may be less accurate
- For optimal performance, use CUDA-enabled hardware