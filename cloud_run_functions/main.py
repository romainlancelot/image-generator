import json
import os
import uuid

import flask
from google import genai
from google.cloud import storage
from google.genai import types
from google.cloud.firestore import Client, SERVER_TIMESTAMP

PROJECT_ID: str = os.getenv("GCLOUD_PROJECT")
LOCATION: str = os.getenv("LOCATION", "us-central1")
BUCKET_NAME: str = "gcp-project-image-generator"
BUCKET_IMAGES_PATH: str = "generated-images"
FIRESTORE_DATABASE: str = "gcp-project-image-generator"
FIRESTORE_COLLECTION: str = "generated-images"
GENERATION_MODEL: str = "imagen-3.0-generate-002"

app = flask.Flask(__name__)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client()
firestore_client = Client(database=FIRESTORE_DATABASE)


def generate_image(prompt: str) -> bytes:
    """
    Generates an image based on the given prompt using the specified generation model.

    Args:
        prompt (str): The text prompt to generate the image from.

    Returns:
        bytes: The generated image in bytes format.

    Raises:
        ValueError: If no images are generated.
        RuntimeError: If there is an error during image generation.
    """
    try:
        response = genai_client.models.generate_images(
            model=GENERATION_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="3:4",
                safety_filter_level="BLOCK_ONLY_HIGH",
                person_generation="ALLOW_ADULT",
            ),
        )
        if not response.generated_images:
            raise ValueError("No images generated")
        return response.generated_images[0].image.image_bytes
    except Exception as e:
        raise RuntimeError(f"Error generating image: {str(e)}") from e


def upload_to_storage(image_bytes: bytes) -> str:
    """
    Uploads an image to Google Cloud Storage.

    Args:
        image_bytes (bytes): The image data in bytes.
        filename (str): The name of the file to be saved in the storage.

    Returns:
        str: The URL of the uploaded image.

    Raises:
        RuntimeError: If there is an error during the upload process.
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        filename: str = f"{str(uuid.uuid4())}.png"
        blob = bucket.blob(f"{BUCKET_IMAGES_PATH}/{filename}")
        blob.upload_from_string(image_bytes, content_type="image/png")
        return f"https://storage.googleapis.com/{BUCKET_NAME}/{BUCKET_IMAGES_PATH}/{filename}"
    except Exception as e:
        raise RuntimeError(f"Error uploading image to storage: {str(e)}") from e


def store_to_firestore(prompt: str, url: str) -> None:
    """
    Stores the given prompt and image URL to a Firestore collection with a timestamp.

    Args:
        prompt (str): The prompt associated with the image.
        url (str): The URL of the image to be stored.

    Raises:
        RuntimeError: If there is an error storing the image to Firestore.
    """
    try:
        doc_ref = firestore_client.collection(FIRESTORE_COLLECTION).document()
        doc_ref.set(
            {
                "prompt": prompt,
                "image": url,
                "timestamp": SERVER_TIMESTAMP,
            }
        )
    except Exception as e:
        raise RuntimeError(f"Error storing image to Firestore: {str(e)}") from e


@app.route("/generate", methods=["POST", "OPTIONS"])
def generate_and_store_image(request: flask.Request):
    """
    Handles HTTP requests to generate an image based on a prompt and store it.

    This function supports CORS preflight requests and processes POST requests
    containing a JSON payload with a "prompt" key. It generates an image based
    on the prompt, uploads the image to cloud storage, and stores the prompt
    and image URL in Firestore.

    Args:
        request (flask.Request): The HTTP request object containing the JSON payload.

    Returns:
        tuple: A tuple containing the response body, status code, and headers.
            - On success: (JSON string with success status, 200, headers)
            - On failure: (JSON string with error message, 500, headers)
            - On missing prompt: ("No prompt provided", 400, headers)
            - On CORS preflight: ("", 204, headers)
    """
    headers = {"Access-Control-Allow-Origin": "*"}
    if request.method == "OPTIONS":
        headers.update(
            {
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
            }
        )
        return "", 204, headers
    try:
        request_json = request.get_json()
        if not request_json or "prompt" not in request_json:
            return "No prompt provided", 400, headers
        prompt: str = request_json["prompt"]
        image: bytes = generate_image(prompt)
        url: str = upload_to_storage(image)
        store_to_firestore(prompt, url)
        return (
            json.dumps({"success": True, "prompt": prompt, "url": url}),
            200,
            headers,
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        return json.dumps({"success": False, "error": str(e)}), 500, headers


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
