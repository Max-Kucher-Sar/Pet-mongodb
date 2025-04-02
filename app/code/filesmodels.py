from pymongo import MongoClient
import os
from os import getcwd, remove, path, listdir
from dotenv import load_dotenv
from pydantic import BaseModel

from io import BytesIO

load_dotenv()

user = os.getenv('user')
pswd = os.getenv('pswd')

# client = MongoClient(f'mongodb://{user}:{pswd}@mongodb:27017/')
client = MongoClient(
    host="mongodb",
    port=27017,
    username=user,
    password=pswd,
    authSource="admin"
)

client.admin.command('ismaster')


db = client['filesDB']



if 'files' in db.list_collection_names():
    collection = db['files']
else:
    collection = db.create_collection('files')


class FilesModel(BaseModel):
    name : str
    description : str


class MongoDB:
    def __init__(self, file=None, file_inf=None):
        self.file = file
        self.file_inf = file_inf
        

    def all_files(self):
        search = []

        for elements in collection.find():
            elements['_id'] = str(elements['_id'])
            elements['file_byte'] = str(elements['file_byte']).__len__()
            search.append(elements)
        return search
        
            
    def search_file_by_name(self, filename):
        try: 
            search = collection.find_one({'name' : filename})
            search['_id'] = str(search['_id'])
            search['file_byte'] = str(search['file_byte']).__len__()
            return [search]
        except:
            return {'status' : False, 'msg' : f'Файл с именем {filename} отсутствует'}

    def search_file_by_format(self, file_format):
        search = []
        try:
            for elements in collection.find():
                if elements['format'] == file_format:
                    elements['_id'] = str(elements['_id'])
                    elements['file_byte'] = str(elements['file_byte']).__len__()
                    search.append(elements)
                else:
                    pass
            return search
        except:
            return {'status' : False, 'msg' : f'Формат {file_format} отсутствует'}

    def write_new_file(self, content):
        format_file_test = self.file.filename.split('.')[-1]
        format_file = '.' + format_file_test
        
        work_path = os.path.join('files', self.file.filename)
        with open(work_path, 'wb') as buffer:
            buffer.write(content)
        file_to_add = {'name': self.file_inf.name, 'description': self.file_inf.description, 'format': format_file, 'path' : work_path, 'file_byte': content}
        collection.insert_one(file_to_add)

        return {'status': True}

    def exit_file(self, filename):
        try:
            search = collection.find_one({'name' : filename})
            file_byte = search['file_byte']
            file_name = search['name']
            file_format = search['format']
            true_file_name = file_name + file_format
            file_stream = BytesIO(file_byte)
            return true_file_name, file_byte, file_stream
        except:
            return {'status' : False, 'msg' : f'Файл с именем {filename} отсутствует'}

    def file_view(self, filename):
        try:
            search = collection.find_one({'name' : filename})
            file_path = '/' + search['path']
            return {"file_path": file_path}
        except:
            return {'status' : False, 'msg' : f'Файл с именем {filename} отсутствует'}

    def delete_one_file(self, filename):
        try:
            search = collection.find_one({'name': filename})
            file_path = search['path']
            search_to_delete = collection.delete_one({'name': filename})
            os.remove(file_path)
            return {'status' : True, 'msg' : f'Файл {filename} удален'}
        except:
            return {'status' : False, 'msg' : f'Файл с именем {filename} отсутствует'}



        


