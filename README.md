# jcic_pdf2csv
Transforming standard Taiwan's <JCIC customer credit report> (pdf files) to formatted data (*.csv)

本專案可將制式《聯徵中心個人信用報告》(pdf檔)轉為結構型資料(.csv檔)形式

## How to Install 

This project runs on the following platform: 

- OS: Windows 7+
- Python 3.7.0
- Packages: 
    * pandas==0.24.2
    * PyPDF2==1.26.0
    * pdfminer3k==1.3.1
    

## How to use 

### [Run] python pdf_to_csv.py run
1. Put the input pdf files to "input_pdf" folder 
2. Run "python pdf_to_csv.py run" in command line
3. Check result 
	1) Find output csv files at output_csv/ folder 
	2) Check the printed output, results could be either one of below: 
  
		 - "Failed to read file: (file_name)" 
		 - "All files read. " 

### [Clean Previous Results] python pdf_to_csv.py clean_all
1. Run "python pdf_to_csv.py clean_all" in command line
2. All contents in temp & output folders should be removed: output_csv/, tmp/txt, tmp/decrypted_pdf
    
### [Clean Temp Files] python pdf_to_csv.py clean_temp
1. Run "python pdf_to_csv.py clean_temp" in command line
2. All contents in temp folders should be removed: tmp/txt, tmp/decrypted_pdf
