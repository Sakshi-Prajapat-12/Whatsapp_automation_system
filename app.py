import pandas as pd
import pywhatkit
import time
from flask import Flask , request,render_template
import os
import uuid
from werkzeug.utils import secure_filename
import mysql.connector

import random
# backend logic 
app=Flask(__name__)
app.config['Upload_Folder']='uploads' 

# database connection 
db=mysql.connector.connect(
host="",#use your system sql host
user="", # user name
password="", #password
database="" # schema



)
cursor=db.cursor()

# home page 
@app.route('/')
def index():
    return render_template("index.html")

# send route 
@app.route('/send',methods=['POST'])
def send():
     # get message and  file
     message=request.form.get('message')

     file=request.files.get('file')


     if not file or file.filename == "":
        return " No file Uploaded"
     
     
     # session id 
     session_id=str(uuid.uuid4())

     # save file securely
     filename=secure_filename(file.filename)
     filepath=os.path.join(app.config['Upload_Folder'],f"{session_id}_{filename}")
     file.save(filepath)
# for image sending 
     img_file=request.files.get('image')
     img_path=None
     if img_file is not None and  img_file.filename != "":
         img_filename=secure_filename(img_file.filename)
         img_path=os.path.join(app.config['Upload_Folder'],f"{session_id}_{img_filename}")
         img_file.save(img_path)

     # read excel file 
     
     filename=file.filename.lower()

     if filename.endswith('.xlsx'):
         df=pd.read_excel(filepath,engine='openpyxl',dtype=str)

     elif filename.endswith('.csv'):
         df=pd.read_csv(filepath,dtype=str)

     elif filename.endswith('.json'):
         df=pd.read_json(filepath,dtype=str)
     
     if 'Contact_number' not in df.columns:
         return "Excel must have 'Contact_number' column"
    
    
     count=0
     
     numbers=list(df['Contact_number'])
     for  number in numbers:
         number=str(number).strip()

         if len(number) == 10:
             number="+91"+number
         
          
         
         if img_path:
                pywhatkit.sendwhats_image(
                receiver=number,
                #caption=message,
                 img_path=img_path,
                 wait_time=20,
                 tab_close=True,
                close_time=20
           )
                time.sleep(10)
                 
         if message:
                

              pywhatkit.sendwhatmsg_instantly(
               phone_no=number,
               message=message,
    
               wait_time=20,     
               tab_close=True,
              close_time=20
         )
              
         
        
         time.sleep(random.randint(20,40))

             
         cursor.execute( 
             "Insert into Whatsapp_contacts(session_id) values (%s)",
             (session_id)
         )
         count+=1
        
     db.commit()
    
    # os remove temporary file after sending msg
     os.remove(filepath)
     os.remove(img_path)
     
     return f"""
        <h3>success</h3>
        <p>Session Id :{session_id}</p>
        <p>Total Uploaded:{count}</p>
          """
if __name__== "__main__":
    os.makedirs('uploads',exist_ok=True)
    app.run(debug=True)







