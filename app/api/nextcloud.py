from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import tempfile
from nc_py_api import Nextcloud
from app.services import AnythingLLM

router = APIRouter()

nc = Nextcloud(nextcloud_url=os.getenv('NC_HOST'), nc_auth_user=os.getenv('NC_AUTH_USER'), nc_auth_pass=os.getenv('NC_AUTH_PASS'))

class FileSync(BaseModel):
    user: str
    path: str

@router.post("/nextcloud/files/sync")
async def fileSync(file_sync: FileSync):
    try:
        # Ensure the tmp directory exists
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, dir=tmp_dir) as temp_file:
            temp_file_path = temp_file.name
            # Download the file to the temporary file
            nc.files.download2stream(path=file_sync.path, fp=temp_file)

        file_name = os.path.basename(file_sync.path)

        # Upload the file and get the response
        upload_response = await AnythingLLM.uploadFile(file_name=file_name, file_path=temp_file_path)

        # Extract file_location from the response
        documents = upload_response.get('documents', [])
        if not documents:
            raise HTTPException(status_code=500, detail="Documents not found in upload response")

        file_location = documents[0].get('location')
        if not file_location:
            raise HTTPException(status_code=500, detail="File location not found in upload response")

        # Add embeddings
        await AnythingLLM.addEmbedding(file_location=file_location, workspace=file_sync.user)

        return {"message": f"File {file_name} synced!"}
        #def iterfile(file_path: str):
        #    with open(file_path, mode="rb") as file_like:
        #        yield from file_like

        # Return the file as a streaming response
        #return StreamingResponse(iterfile(temp_file_path), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"})
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"File sync failed: {e}")
    finally:
        # Clean up the temporary file
        #if os.path.exists(temp_file_path):
        #    os.remove(temp_file_path)
        print('Clean up files!')