# visualizer

### New files
- `nfdi.ipynb`: Jupyter notebook for the NFDI demonstrator in a custom layout which was handcrafted to display the visualizer in a more user-friendly way with Voila. This serves as a benchmark.
- `convert.py`: Python script to convert the Jupyter notebook into a Voila-compatible format (Still work in progress).
- `demonstrator_ver2.ipynb`: Jupyter notebook for the NFDI demonstrator, but slightly modified to accomodate for Voila.
- `demonstrator_ver2_converted.ipynb`: Converted version of the `demonstrator_ver2.ipynb` notebook, which is compatible with Voila (Still buggy).
- `captcha_details.txt`: Text file containing details about the captcha implementation for future.

### How to run the visualizer with Voila

To see the `nfdi.ipynb` notebook in a user-friendly format, you can run the following command in your terminal:

```bash
voila nfdi.ipynb --template=material --theme=light
```

To convert the `demonstrator_ver2.ipynb` notebook into a Voila-compatible format, you can run:

```bash
python convert.py demonstrator_ver2.ipynb demonstrator_ver2_converted.ipynb
voila demonstrator_ver2_converted.ipynb --template=material --theme=light
```
