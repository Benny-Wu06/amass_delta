from mangum import Mangum
from app.main import app

# This is the "Entry Point" for AWS
# Mangum takes the API Gateway event and converts it into a 
# format that FastAPI (Starlette) understands.
auth_lambda = Mangum(app, lifespan="off")