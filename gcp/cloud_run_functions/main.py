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


def generate_image(prompt: str) -> bytes | None:
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
            raise Exception("No images generated")
        return response.generated_images[0].image.image_bytes
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None


def upload_to_storage(image_bytes: bytes, filename: str) -> None:
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{BUCKET_IMAGES_PATH}/{filename}")
        blob.upload_from_string(image_bytes, content_type="image/png")
    except Exception as e:
        print(f"Error uploading image to storage: {str(e)}")


def store_to_firestore(prompt: str, filename: str) -> None:
    try:
        doc_ref = firestore_client.collection(FIRESTORE_COLLECTION).document()
        doc_ref.set(
            {
                "prompt": prompt,
                "image": f"https://storage.cloud.google.com/{BUCKET_NAME}/{BUCKET_IMAGES_PATH}/{filename}",
                "timestamp": SERVER_TIMESTAMP,
            }
        )
    except Exception as e:
        print(f"Error storing image to Firestore: {str(e)}")


@app.route("/generate", methods=["POST", "OPTIONS"])
def generate_and_store_image(request: flask.Request):
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
        image: bytes | None = generate_image(prompt)
        if not image:
            return (
                json.dumps({"success": False, "error": "Error generating image"}),
                500,
                headers,
            )
        filename: str = f"{str(uuid.uuid4())}.png"
        upload_to_storage(image, filename)
        store_to_firestore(prompt, filename)
        return (
            json.dumps({"success": True, "prompt": prompt, "filename": filename}),
            200,
            headers,
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        return json.dumps({"success": False, "error": str(e)}), 500, headers


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
