import os
import vertexai

vertexai.init(
    project=os.environ.get("PROJECT_NAME", None),
    location=os.environ.get("CLOUD_LOCATION", None),
)
