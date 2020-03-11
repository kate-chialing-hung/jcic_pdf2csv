#-----------------pdf_decrypt-----------------

import subprocess
import os
import sources.dir_handler as dir_handler
import PyPDF2
from shutil import copyfile


def decrypt_dir(source_dir = 'input_pdf', destination_dir = 'tmp/decrypted_pdf', install_dir = 'install'): #qpdf.exe位置, 初始pdf位置, 破解pdf位置
    source_dir = dir_handler.cleanse_dir(source_dir)
    destination_dir = dir_handler.cleanse_dir(destination_dir)
    install_dir = dir_handler.cleanse_dir(install_dir)
    
    dir_handler.delete_files(destination_dir)
    
    files = os.listdir(source_dir) 
    files = [file for file in files if file.endswith(".pdf")]
    
    for file_name in files: 
        source_file = os.path.join(source_dir, file_name) 
        destination_file = os.path.join(destination_dir, file_name) 
        
        pdf_reader = PyPDF2.PdfFileReader(open(source_file, 'rb'))
        is_encrypted = pdf_reader.isEncrypted
        
        if(is_encrypted == False): 
            print("decryptor: skip {}".format(file_name))
            copyfile(source_file, destination_file)
        else: 
            cmd = ["qpdf.exe", "--decrypt", source_file, destination_file]  #命令行终端命令
            sub = subprocess.Popen(args=cmd,cwd=install_dir,shell=True)   #不要忘记cwd
            sub.wait()   #最好加上，否则可能由于多个进程同时执行带来机器瘫痪
    
    dir_handler.check_file_outcome(source_dir, destination_dir, "decrypt_pdf") 
    
    return 1
