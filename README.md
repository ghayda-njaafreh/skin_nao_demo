# Skin NAO Demo

An educational demonstration project that integrates a pre-trained skin lesion classification model with a NAO robot interaction workflow and a simple web interface.

This project was built for **educational, research demonstration, and presentation purposes only**. It is **not** intended for medical diagnosis, treatment, or clinical decision-making.

## Project Overview

The system combines three main parts:

- **Inference backend** for skin lesion image classification
- **NAO robot integration** for speech and interaction
- **Web interface** for image upload and result display

The demonstration workflow allows the system to:

1. Receive an uploaded skin image or capture one through the NAO camera workflow
2. Run inference using a pre-trained skin lesion classification model
3. Return the predicted class and confidence values
4. Generate a spoken explanation for the NAO robot

## Project Structure

```text
skin_nao_demo/
├── nao.py
├── nao_camera_server/
│   └── server.py
├── skin_nao_demo/
│   ├── inference.py
│   ├── labels.json
│   ├── main.py
│   ├── model.py
│   ├── nao_speaker.py
│   ├── predictor.py
│   └── test_predictor.py
└── skinnaoweb/
    ├── index.html
    ├── *.html
    ├── *.css
    └── images
```

## Model Attribution

This project uses a pre-trained skin lesion classification model from the following Hugging Face repository:

**iamhmh / derm-cnn-ham10000**  
<https://huggingface.co/iamhmh/derm-cnn-ham10000>

We used the published trained model as part of our educational NAO-based demonstration workflow.

## Important License Notice

According to the original model page:

- **Model weights:** CC BY-NC 4.0
- **Code:** MIT License

For that reason:

- this repository is shared for **non-commercial educational and demonstration purposes only**
- users should review the **original source and license terms** before downloading, reusing, or redistributing the model weights
- the model weights are **not included in this repository**; they should be obtained from the original source

## Medical Disclaimer

This project is for **educational and demonstration purposes only**.

It is **not** a medical device and must **not** be used for diagnosis, treatment, screening, or clinical decision-making.

## What Is Included in This Repository

This repository includes:

- backend inference and API code
- NAO interaction scripts
- web UI files
- label mapping file
- test/integration helper files

This repository does **not** include:

- the external pre-trained model weights file (`model.pth`)
- runtime logs
- generated uploads or captured images
- machine-specific secrets, credentials, or local environment paths

## Setup

## 1) Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/skin-nao-demo.git
cd skin-nao-demo
```

## 2) Create and activate a Python environment

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

## 3) Install dependencies

```bash
pip install -r requirements.txt
```

## 4) Download the model weights separately

Download the trained model weights from the original Hugging Face source and place the file in:

```text
skin_nao_demo/model.pth
```

## 5) Update local configuration if needed

Before running the project, review local machine-specific settings such as:

- NAO robot IP address
- NAO camera server URL
- Python 2 interpreter path used for NAO SDK integration
- any local file paths

## Running the Backend API

From the backend folder:

```bash
cd skin_nao_demo
uvicorn main:app --reload
```

## Example Endpoints

- `GET /` → API health message
- `POST /predict` → predict from uploaded image
- `POST /predict_from_nao` → capture from NAO camera workflow and predict

## Recommended Repository Hygiene

Before publishing publicly, make sure you do **not** commit:

- `model.pth`
- `nao_speech_log.txt`
- `uploads/`
- `captured_images/`
- `.venv/`
- `__pycache__/`
- any local credentials or private IP-sensitive files

## Suggested Citation / Acknowledgment

If you present or document this project, include an acknowledgment such as:

> This project uses a pre-trained skin lesion classification model from the Hugging Face repository `iamhmh/derm-cnn-ham10000`, used here for non-commercial educational demonstration purposes.

## Authors

Developed as a collaborative educational project.
