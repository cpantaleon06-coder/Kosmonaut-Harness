import db

db.upload_archive("test/hello.txt", b"hello")
print("bucket:", db.download_archive("test/hello.txt"))

project_id = db.save_project("test task", "test reply", "test/hello.txt")
print("project id:", project_id)
print("row:", db.get_project(project_id))
