from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routers.resume import router as resume_router
from app.routers.jd import router as jd_router
from app.routers.matching import router as matching_router


app = FastAPI(
    title="AI Resume Matching System",
    description="AI-based Resume Matching and Candidate Ranking API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router)
app.include_router(jd_router)
app.include_router(matching_router)


@app.get("/")
def home():
    return {
        "message": "AI Resume Matching System is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Convert uploaded file schemas to Swagger-compatible format
def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )

    def fix_file_schema(node):
        if isinstance(node, dict):

            if (
                node.get("type") == "string"
                and node.get("contentMediaType") == "application/octet-stream"
            ):
                node.pop("contentMediaType", None)
                node["format"] = "binary"

            for value in node.values():
                fix_file_schema(value)

        elif isinstance(node, list):
            for item in node:
                fix_file_schema(item)

    fix_file_schema(schema)

    app.openapi_schema = schema

    return app.openapi_schema


app.openapi = custom_openapi
