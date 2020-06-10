from google_connection import Connect 
from mimetypes import MimeTypes
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO

class GoogleDrive():

    # ---------CONSTRUCTOR-------------
    def __init__(self):
        drive_conn = Connect()
        self.drive_service = drive_conn.get_service()

    # ---------PUBLIC------------------
    def guess_mimetype(self, path_to_file):
        mime = MimeTypes()
        return mime.guess_type(path_to_file)[0]

    def list_files_on_folder(self, parent_folder_id):
        files = self.drive_service.files().list(
            q = "'{folderId}' in parents".format(folderId=parent_folder_id),
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=None
        ).execute()
        return files['files']

    def new_folder(self, folder_name, parent_folders_ids = []):
        file_metadata = {'mimeType': 'application/vnd.google-apps.folder'}
        file_metadata['name'] = folder_name
        if len(parent_folders_ids) > 0:
            file_metadata['parents'] = parent_folders_ids
        file = self.drive_service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        return file.get('id')

    def move_file_to_folder(self, file_id, to_folder_id):
        file = self.drive_service.files().get(
            fileId=file_id,
            fields='parents'
        ).execute()
        previous_parents = ",".join(file.get('parents'))

        result = self.drive_service.files().update(
            fileId=file_id,
            addParents=to_folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        return result

    def upload_file(
        self, 
        full_path_to_file,
        drive_file_name=None, 
        mimetype=None,
        parent_folders_ids = []
    ):
        if not drive_file_name:
            drive_file_name = full_path_to_file

        file_metadata = {'name': drive_file_name}

        if len(parent_folders_ids) > 0:
            file_metadata['parents'] = parent_folders_ids
        
        if not mimetype:
            mimetype = self.guess_mimetype(full_path_to_file)

        print(mimetype)

        media = MediaFileUpload(
            full_path_to_file,
            mimetype=mimetype
        )
        
        try:
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            return file.get('id')
        except:
            try:
                # Sometimes it works on the second trial
                file = self.drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                return file.get('id')
            except:
                raise ValueError("Unable to upload file")

    def open_file(self, file_id):
        # Get byte stream
        data = self.open_as_bytes(file_id)
        return data

    def open_as_bytes(self, file_id):
        # Open arbitary file as bytestream
        request = self.drive_service.files().get_media(fileId=file_id)
        stream = BytesIO()
        downloader = MediaIoBaseDownload(stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return stream.getvalue()