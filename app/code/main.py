from os import getcwd, remove, path, listdir
from fastapi import FastAPI, Request
from fastapi import File, UploadFile, Body, Form, Depends
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from filesmodels import MongoDB, FilesModel
from typing import Dict

app = FastAPI()
app.mount("/files", StaticFiles(directory="files"))

templates = Jinja2Templates(directory="templates")


@app.get('/files', tags=["Поиск"])
async def get_all_files():
    res = MongoDB().all_files()
    if res == []:
        return {'status' : False, 'msg' : f'Отсутствуют файлы'}
    else:
        return res

@app.get("/file/filename/{filename}", tags=["Поиск"])
async def get_file_by_name(filename: str):
    return MongoDB().search_file_by_name(filename)

@app.get("/file/file_format/{file_format}", tags=["Поиск"])
async def get_file_by_format(file_format : str):
    res = MongoDB().search_file_by_format(file_format)
    if res == []:
        return {'status' : False, 'msg' : f'Формат {file_format} отсутствует'}
    else:
        return res

@app.get("/download_file(en_name_only)", tags=["Операции"])
async def download_file(file_name: str):
    filename, filebyte, filestream = MongoDB().exit_file(file_name)
    return StreamingResponse(filestream, media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={filename}", "Content-Length": str(len(filebyte))})

@app.get("/view_file", tags=["Операции"])
async def view_file(request: Request, filename: str):
    res = MongoDB().file_view(filename)
    return templates.TemplateResponse("index.html", {"request": request, "file_path": res["file_path"]})

@app.post("/upload_file", tags=["Операции"])
async def upload_file(file_inf: FilesModel=Depends(), file: UploadFile=File(...)):
    if not file:
        return {"status" : "No files"}
    else:
        content = await file.read()
        return MongoDB(file, file_inf).write_new_file(content)

@app.delete("/delete_file/{filename}", tags=["Удаление"])
async def delete_file(filename: str):
    return MongoDB().delete_one_file(filename)