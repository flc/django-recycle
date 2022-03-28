from django.core.files.uploadhandler import FileUploadHandler, StopUpload


class QuotaUploadHandler(FileUploadHandler):
    """
    This test upload handler terminates the connection if more than a quota
    (QUOTA) is uploaded.
    """

    QUOTA = 10 * 2**20  # 10 MB

    def __init__(self, request=None):
        super().__init__(request)

        self.total_upload = 0

    # def handle_raw_input(self, input_data, META, content_length,
    #                      boundary, encoding=None):
    #     if content_length > self.QUOTA:
    #         #raise StopUpload(connection_reset=True)
    #         return QueryDict(MultiValueDict(), encoding=encoding), MultiValueDict()

    def receive_data_chunk(self, raw_data, start):
        self.total_upload += len(raw_data)
        if self.total_upload >= self.QUOTA:
            raise StopUpload(connection_reset=True)
        return raw_data

    def file_complete(self, file_size):
        return None
