
PATH = r'\receipts'
BASE = r'C:\Users\after\OneDrive\Desktop\code_from_HD\Groceries\Groceries\FLASK\final_versions'
folder = BASE +"\\"+ PATH
folder_path = folder
UPLOAD_FOLDER = os.listdir(folder_path)
len(UPLOAD_FOLDER)

for filenumber, filename in enumerate(UPLOAD_FOLDER):
	file_path = os.path.join(folder_path, filename)
	if os.path.isfile(file_path):
			file_date = filename.split(".")[0]
			print ("Uploading Filename", filename)