#!/bin/bash

gcloud functions deploy generate_and_store_image \
  --runtime python312 \
  --trigger-http \
  --memory 256MB \
  --allow-unauthenticated
