# Microstructure Thermal Simulation Tool Documentation

## Overview

The Microstructure Thermal Simulation Tool is a web-based application that allows users to analyze heat transfer through different microstructures. The tool provides a visual interface for simulating thermal conductivity and heat flux across custom or pre-defined two-phase material structures.

## Table of Contents

1. [Features](#features)
2. [User Guide](#user-guide)
3. [Technical Architecture](#technical-architecture)
4. [API Reference](#api-reference)
5. [Code Structure](#code-structure)
6. [Development Guide](#development-guide)

## Features

- **Multiple Input Methods**: Use preset microstructures, upload custom images, or draw your own designs
- **Interactive Parameter Control**: Adjust thermal conductivity ratio (κ₁) and direction angle (α) in real-time
- **Advanced Drawing Tools**: Comprehensive toolset for creating custom microstructures
- **Visualization**: Interactive heatmaps for temperature fluctuation and heat flux magnitude
- **Data Analysis**: Automatic calculation of effective thermal conductivity tensors
- **Responsive Design**: Works on desktop and mobile devices

## User Guide

### Getting Started

1. Choose your input method from the three tabs: "Preset Microstructures," "Upload Image," or "Draw Custom"
2. Adjust the thermal parameters using the sliders:
   - κ₁: Thermal conductivity ratio between phases (0.1 to 10)
   - α: Direction angle of the thermal gradient (0° to 90°)
3. Process your microstructure using the appropriate button
4. View the simulation results in the right column

### Input Methods

#### Preset Microstructures
- Enter a Microstructure ID (0 to maximum available)
- Click "Load Microstructure" to run the simulation

#### Upload Image
- Upload a PNG, JPEG, or GIF file
- Images are processed as binary (black/white) microstructures
- White represents the conductive phase
- Uploaded images are restricted to 400×400px

#### Draw Custom
The drawing interface includes:
- Drawing tools: Pencil, Line, Eraser
- Canvas operations: Clear, Fill, Invert, Undo/Redo
- Shape tools: Circle, Rectangle, Triangle, Grid, Checkerboard, Random, Cellular
- Save/Load functionality for drawings

### Interpreting Results

The application displays:
- Microstructure visualization
- Temperature fluctuation plots for two load cases
- Heat flux magnitude plots for two load cases
- Calculated information including:
  - Volume fraction
  - Reuss and Voigt bounds
  - Effective thermal conductivity tensor

## Technical Architecture

### Frontend Components

- **HTML/CSS**: Page structure and styling with responsive design
- **JavaScript**: Core application logic and interactivity
- **Plotly.js**: Data visualization library for interactive plots
- **Canvas API**: Used for the drawing interface

### Backend Integration

The application connects to a server-side API with four main endpoints:
- `/api/info`: Retrieves dataset information
- `/api/simulate`: Processes preset microstructures
- `/api/upload-microstructure`: Processes uploaded images
- `/api/process-drawing`: Processes custom drawings

### Data Flow

1. User selects input method and parameters
2. Application sends data to the appropriate API endpoint
3. Server performs thermal simulation calculations
4. Results are returned to the client and visualized
5. Interactive plots allow exploration of the results

## API Reference

### Endpoints

#### GET `/api/info`

Returns information about the available microstructures and system capabilities.

**Response:**
```json
{
  "sample_count": integer,
  "device": string,
  "has_surrogate": boolean
}
```

#### POST `/api/simulate`

Simulates thermal properties for a preset microstructure.

**Request Body:**
```json
{
  "ms_id": integer,
  "kappa1": float,
  "alpha": float
}
```

#### POST `/api/upload-microstructure`

Processes an uploaded image and simulates thermal properties.

**Request Body:** FormData with:
- `file`: Image file
- `kappa1`: float
- `alpha`: float

#### POST `/api/process-drawing`

Processes a canvas drawing and simulates thermal properties.

**Request Body:** FormData with:
- `drawing`: Base64 image data
- `kappa1`: float
- `alpha`: float

### Response Format

All simulation endpoints return JSON with the following structure:
```json
{
  "image": number[][],
  "param_field": number[][],
  "temp0": number[][],
  "temp1": number[][],
  "flux_norm0": number[][],
  "flux_norm1": number[][],
  "vol_frac": float,
  "reuss": float,
  "voigt": float,
  "eig_kappa": [float, float],
  "surrogate_results": object (optional)
}
```

## Code Structure

### HTML Structure

- Container with left/right column layout
- Control panels for each input method
- Information panels for results
- Plot containers for visualizations
- Modal overlay for loading state

### CSS Components

- Responsive grid system
- Control panel styling
- Interactive drawing interface
- Plot styling and layout
- Mobile-responsive adaptations

### JavaScript Modules

#### Core Application

- `initApp()`: Initializes the application and fetches system information
- `runSimulation()`: Main function for processing preset microstructures
- `updateParametersOnly()`: Updates visualization with new parameters without changing the microstructure
- `createVisualizations()`: Renders all plots based on simulation results

#### Drawing Interface

- Canvas initialization and event handling
- Drawing tools implementation (pencil, line, eraser)
- Shape generation functions (circle, rectangle, grid, etc.)
- History tracking for undo/redo functionality
- Save/load system using localStorage

#### Visualization

- `createHeatmap()`: Creates Plotly heatmaps for data visualization
- `toggleDisplayMode()`: Switches between heatmap and contour visualization
- `setupEfficientZoomHandlers()`: Implements efficient plot zooming
- Plot download and reset functionality

## Development Guide

### Adding New Features

#### New Drawing Tools

1. Add a button to the HTML interface in the appropriate section
2. Create a JavaScript function that implements the drawing logic
3. Add an event listener to connect the button to the function
4. Update the active tool tracking system

#### New Visualization Methods

1. Modify or extend the `createHeatmap()` or `toggleDisplayMode()` functions
2. Ensure proper handling of data transformation and plot options
3. Update the plot controls to access the new visualization method

### Performance Considerations

- Use debounced event handlers for slider inputs
- Implement efficient zoom handling for plots
- Consider canvas size limitations on mobile devices
- Handle asynchronous API calls properly with loading indicators

### Browser Compatibility

The application is designed to work with modern browsers that support:
- Canvas API
- ES6+ JavaScript features
- CSS Grid and Flexbox
- Fetch API for network requests

## Key Functions Reference

### Core Application Functions

#### `initApp()`
Initializes the application by fetching information about available microstructures and setting up the UI.

#### `runSimulation()`
Processes a preset microstructure with the current parameters and displays results.

#### `updateParametersOnly()`
Updates the visualization with new thermal parameters without changing the microstructure.

#### `createVisualizations(results)`
Creates all the visualization plots based on simulation results.

#### `updateInfoPanel(results, msId, kappa1, alpha)`
Updates the information panel with calculated thermal properties.

### Drawing Interface Functions

#### `initializeDrawingTools()`
Sets up the drawing interface with all tools and event listeners.

#### `saveCanvasState()`
Saves the current canvas state to the history stack for undo/redo functionality.

#### `drawLine()`, `drawCircle()`, `drawRectangle()`, etc.
Functions for drawing different shapes and patterns on the canvas.

#### `processDrawing()`
Sends the current drawing to the server for thermal simulation.

### Visualization Functions

#### `createHeatmap(container, data, title, colorscale, options)`
Creates a heatmap visualization using Plotly with the provided data.

#### `toggleDisplayMode(plotId)`
Switches between heatmap and contour visualization modes.

#### `setupEfficientZoomHandlers(container)`
Sets up optimized event handlers for zooming and panning in plots.

### Helper Functions

#### `transposeMatrix(matrix)`
Transposes a 2D matrix for correct visualization orientation.

#### `getRotatedImageData(imageData, needsRotation)`
Handles image rotation for consistent processing across different input methods.

#### `debounce(func, wait)`
Creates a debounced version of a function to limit frequent updates.

## Credits

Developed by:
- Julius Herb (herb@mib.uni-stuttgart.de)
- Sanath Keshav (keshav@mib.uni-stuttgart.de)
- Felix Fritzen (fritzen@mib.uni-stuttgart.de)

Affiliation: Heisenberg Professorship Data Analytics in Engineering, Institute of Applied Mechanics, University of Stuttgart
