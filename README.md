# API Doctor

API Doctor is designed to manage and interact with various REST APIs and comes with some public APIs. It comes with a GUI to add, view, edit, and send API requests.

## Features

- **Add New APIs**: Easily add new APIs by providing the API name, description, request format, and endpoint URL.
- **View API Information**: View detailed information about each API, including the help text and request format.
- **Edit Existing APIs**: Edit the details of existing APIs with pre-populated fields.
- **Send API Requests**: Send requests to APIs with or without parameters and view the responses in a separate window.
- **Save and Open Responses**: Save responses to a file or open them in your default web browser.
- **Clickable Links in Responses**: Links in API responses are clickable and open in the default web browser.

## Prerequisites

- Python 3.x
- `requests` library

Install the required library using pip:
```bash
pip install requests
```

## Getting Started

### Step 1: Download and Run SNT API Doctor

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/SoupNet-Technologies/apidr.git
   cd apidr
   ```

2. **Run the Script:**
   ```bash
   python sntapidr.py
   ```

### Step 2: Adding a New API

When you first run the application, if no APIs are available, it will prompt you to add a new API.

1. **Open Add API View:**
   Click on the "Add API" button if the application doesn't automatically open the Add API view.

2. **Fill in the API Details:**
   - **API Name:** Enter a unique name for the API (e.g., `example-api`).
   - **API Help:** Provide a description or help text for the API (e.g., `This API retrieves example data.`).
   - **API Request Format:** Enter the request format in JSON (e.g., `{"param1": "value1"}`). Leave it empty if no parameters are required.
   - **API URL:** Enter the URL for the API endpoint (e.g., `https://api.example.com/data`).

3. **Save the API:**
   Click the "Save" button to save the API details. The Add API view will close, and the newly added API will appear in the dropdown menu.

### Step 3: Using the API

1. **Select the API:**
   Choose the API from the dropdown menu at the top of the main view.

2. **View API Information:**
   The help text for the selected API will appear in the non-editable text widget below the dropdown. This provides information about what the API does and how to use it.

3. **Enter Request Data:**
   In the API Request Format entry field, enter the JSON formatted request data as per the API's requirements. If no parameters are required, leave it empty.

   Example:
   ```json
   {"key": "your-api-key"}
   ```

4. **Send API Request:**
   Click the "Send" button to send the API request. The response will be displayed in a new window.

### Step 4: Viewing and Saving the Response

1. **View API Response:**
   A new window will open displaying the prettified response from the API, with clickable links.

2. **Save the Response:**
   Click the "Save" button to save the response to a file.

3. **Open in Browser:**
   Click the "Open in Browser" button to view the response in your default web browser.

### Step 5: Editing an Existing API

1. **Select the API:**
   Choose the API from the dropdown menu.

2. **Open Edit API View:**
   Click the "Edit API" button to open the Edit API view with pre-populated fields.

3. **Edit API Details:**
   Update the API details as needed and click the "Save" button to save the changes.

## Troubleshooting Common Issues

If you encounter an error such as `{"success": false, "message": "Parameter key is required"}`, it usually means that the API expects a specific parameter that wasn't included or wasn't formatted correctly. Ensure that you:
- Use the exact parameter names required by the API.
- Format the request data as JSON.
- Provide all mandatory parameters.
