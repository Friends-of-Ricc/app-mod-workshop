#!/usr/bin/env python

'''Documentation:


* Vertex:
* AI Studio: https://ai.google.dev/gemini-api/docs/vision

v0.7 30oct24 Ipsale - Ipsale bugfix.
v0.6 30oct24 ricc - DB with Fantastic 4 ENVs.
v0.5 30oct24 ricc - DB integration seems to work.
v0.4 30oct24 ricc - finally it works! pushing and cleaning up
v0.3 ??oct24 ricc - Public URL changed
'''
GCF_VERSION = '0.7'


VERSION= '0.3'

from google.cloud import storage
from google.cloud import aiplatform
#import base64

import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
import pymysql
import pymysql.cursors



# Replace with your project ID Replace
#PROJECT_ID = "your-project-id"
PROJECT_ID='ricc-demos-386214'
# Replace with your GCP_REGION if you have build for a specific Region
GCP_REGION='us-central1'

GEMINI_MODEL = "gemini-1.5-pro-002"
DEFAULT_PROMPT = "Generate a caption for this image: "
#DEFAULT_PROMPT2 = "What is shown in this image?"

# def gemini_describe_image_from_local_file(base64_image, image_prompt=DEFAULT_PROMPT):
#     '''This is currently broken..'''
#     raise "TODO"

def gemini_describe_image_from_gcs(gcs_url, image_prompt=DEFAULT_PROMPT):
    '''This is currently working great.'''

    # TODO auto-detect project id
    aiplatform.init(project=PROJECT_ID, location=GCP_REGION)
    # Generate a caption using Gemini
    model = GenerativeModel(GEMINI_MODEL) # "gemini-1.5-pro"?

    print(f"Calling {GEMINI_MODEL} for {gcs_url} with this prompt: '''{image_prompt}'''")

    response = model.generate_content([
            Part.from_uri(
                gcs_url,
                mime_type="image/jpeg", # TODO remove or test with PNG..
            ),

            image_prompt,
        ])

    print(f"Gemini spoken: '''{response.text}''' in class today!" )

    # Extract the caption from the response
    return response.text

def update_db_with_description(
        image_filename,
        caption,
        db_user,
        db_pass,
        db_host,
        db_name
        ):
    '''
    '''
    #print(f"update_db_with_description(): Updating DB for img='{image_filename}' with caption '..'. ConnString='{db_conn_string}'")
    # Transforms the image from gs://bucket/my/image.png into /uploads/image.png.
    # Thats because thats how the app does it. Dont ask me why we embed /uploads/ in the app :)

    image_db_filename = f"uploads/{image_filename}"

    conn = None

    try:
        print(f"update_db_with_description(): Connecting to '{db_name}' DB @{db_host}...")
        # Connect to the database
        #import ipdb; ipdb.set_trace()

        conn = pymysql.connect(
                    host=db_host,
                    user=db_user,
                    password=db_pass,
                    database=db_name,)
        #print("update_db_with_description(): Now the cursor...")
        cursor = conn.cursor()
        #print("update_db_with_description(): Now sql..")

        # SQL query to update the database (replace placeholders with actual table and column names)
        sql = 'UPDATE images SET description = %s WHERE filename = %s'
        val = (caption, image_db_filename)

        # Execute the query
        cursor.execute(sql, val)
        conn.commit()

        print(f"[GCFv{GCF_VERSION}] Database updated successfully")

    except Exception as e:
        print(f"[GCFv{GCF_VERSION}] Error updating database: {e}")

    finally:
        # Close the connection
        if conn:
            cursor.close()
            conn.close()


def generate_caption(event, context):
    """
    Cloud Function triggered by a GCS event.
    Args:
        event (dict): The dictionary with data specific to this type of event.
        context (google.cloud.functions.Context): The context parameter contains
                                                event metadata such as event ID
                                                and timestamp.
    """

    # Get the file information from the event
    file_name = event['name']
    bucket_name = event['bucket']
    # not sure they exist!
    #file_size = event['size']
    #content_type = event['contentType']

    print(f"[GCFv{GCF_VERSION}] Bucket: {bucket_name}")
    print(f"Object path: {file_name}")
    print(f"Multifaceted event: {event}")
    #print(f"Size: {file_size} bytes")
    #print(f"Content type: {content_type}")


    # Download the image from GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    print(f"Blob: {blob}")
    public_url = blob.public_url
    print(f"Blob public URL: {public_url}")

    gsutil_object_url = f"gs://{bucket_name}/{file_name}"
    print(f"gsutil_object_url: {gsutil_object_url}")

    # image_bytes = blob.download_as_bytes()

    # # Encode the image in base64
    # base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # prompt = "Generate a caption for this image: "
    # caption = gemini_describe_image(base64_image, prompt)
    caption = gemini_describe_image_from_gcs(gsutil_object_url)

#     # Generate a caption using Gemini
#     aiplatform.init(project=PROJECT_ID, location="us-central1")
#     response = aiplatform.execute_model(
# #        model="gemini-1.5-pro-001",  # Replace with the desired Gemini model
#         model="gemini-1.5-pro",  # Replace with the desired Gemini model
#         instances=[
#             {
#                 "prompt": f"Generate a caption for this image: ",
#                 "images": [
#                     {
#                         "data": base64_image,
#                         "mime_type": "image/jpeg"  # Replace with the actual MIME type
#                     }
#                 ]
#             }
#         ]
#     )

#     # Extract the caption from the response
#     caption = response.predictions[0]['candidates'][0]['content']

    # Print the caption (you can also store it or use it as needed)
    print(f"[GCFv{GCF_VERSION}] Generated caption: {caption}")

    # Construct the connection string (replace placeholders with your actual values)
    # My goodness, pymysql - you could support connection string, bro!

    db_user = os.getenv('DB_USER', None)
    db_pass = os.getenv('DB_PASS', None)
    db_host = os.getenv('DB_HOST', None)
    db_name = os.getenv('DB_NAME', None)
    if db_user is None:
        print("DB_USER is not set. I cant proceed. Please get your ENV back together!")
        return -1
    if db_pass is None:
        print("DB_PASS is not set. I cant proceed. Please get your ENV back together!")
        return -1
    if db_host is None:
        print("DB_HOST is not set. I cant proceed. Please get your ENV back together!")
        return -1
    if db_name is None:
        print("DB_NAME is not set. I cant proceed. Please get your ENV back together!")
        return -1
    update_db_with_description(
        image_filename=file_name,
        caption=caption,
        db_user=db_user,
        db_pass=db_pass,
        db_host=db_host,
        db_name=db_name)
    return True

# def flag_inappropriate():
#     '''TODO(ricc): ask gemini if its inappropriuate and if so, flag it and update DB with TRUE'''
#     pass

    #conn_string = f"mysql+pymysql://{os.environ['MYSQL_USER']}:{os.environ['MYSQL_PASSWORD']}@{os.environ['MYSQL_HOST']}:{os.environ['MYSQL_PORT']}/{os.environ['MYSQL_DATABASE']}"
    #conn_string = os.environ('DB_PYTHON_CONNECTION_STRING')
