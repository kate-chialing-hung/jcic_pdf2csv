#!/usr/bin/env python
# coding: utf-8

# <codecell> run 

import sources.pdf_decryptor as pdf_decryptor
import sources.pdf_to_txt as pdf_to_txt
import sources.txt_to_csv as txt_to_csv
import sources.dir_handler as dir_handler 
import sys

if __name__ == '__main__':
       
    if len(sys.argv) == 1: #未傳入參數
        print("input command: run, clean_all, or clean_temp")

    elif sys.argv[1] == 'run': 
        pdf_decryptor.decrypt_dir("input", "tmp/decrypted_pdf", "install")
        pdf_to_txt.dir_to_txt("tmp/decrypted_pdf", "tmp/txt")
        txt_to_csv.dir_to_csv('tmp/txt', 'output') 

    elif sys.argv[1] == 'clean_all': 
        result = dir_handler.clean_previous_result() 
        if result==1: 
            print("clean_all success")

    elif sys.argv[1] == 'clean_temp': 
        result = dir_handler.clean_temp_files() 
        if result==1: 
            print("clean_temp success")
            
