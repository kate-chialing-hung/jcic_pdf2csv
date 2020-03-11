#-----------------pdf_to_txt-----------------
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal,LAParams
import os
import sources.dir_handler as dir_handler

def file_to_txt(source_dir, destination_dir, file_name, password):
    if(True):
        source_file = source_dir+'/'+file_name
        
        destination_file=file_name.split('.')[0]        
        destination_file = destination_file + ".txt"
        destination_file = os.path.join(destination_dir, destination_file)
        
        source_fn = open(source_file, 'rb')
        
        # 创建一个PDF文档分析器：PDFParser
        parser = PDFParser(source_fn)
        # 创建一个PDF文档：PDFDocument
        doc = PDFDocument()
        # 连接分析器与文档
        parser.set_document(doc)
        doc.set_parser(parser)
        # 提供初始化密码，如果无密码，输入空字符串
        doc.initialize("") 
        
        # 检测文档是否提供txt转换，不提供就忽略
        if not doc.is_extractable:
            print("pdf text extraction not allowed")
            return -1
        else:
            # 创建PDF资源管理器：PDFResourceManager
            resource = PDFResourceManager()
            # 创建一个PDF参数分析器：LAParams
            laparams = LAParams()
            # 创建聚合器,用于读取文档的对象：PDFPageAggregator
            device = PDFPageAggregator(resource, laparams=laparams)
            # 创建解释器，对文档编码，解释成Python能够识别的格式：PDFPageInterpreter
            interpreter = PDFPageInterpreter(resource, device)

            #Exception Handling
            try: 
                for page in doc.get_pages(): 1
            except: 
                return -2
            
            for page in doc.get_pages():
                # 利用解释器的process_page()方法解析读取单独页数
                interpreter.process_page(page)
                # 这里layout是一个LTPage对象,里面存放着这个page解析出的各种对象,
                # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal等等,想要获取文本就获得对象的text属性，
                # 使用聚合器get_result()方法获取页面内容
                layout = device.get_result()
                
                sucess=False
                output_list = [content for content in layout if isinstance(content, LTTextBoxHorizontal)]
                
                for content in output_list:
                    with open(destination_file, 'a',encoding='utf-8') as destination_fn:
                        destination_fn.write(content.get_text() + '\n')
                        sucess=True
                
                if(sucess==False): 
                    return -3
                
        source_fn.close()
        
        return 1

   
def dir_to_txt(source_dir = 'tmp/decrypted_pdf', destination_dir = 'tmp/txt'):
    dir_handler.delete_files(destination_dir)

    destination_dir = dir_handler.cleanse_dir(destination_dir)
    source_dir = dir_handler.cleanse_dir(source_dir)
        
    files = os.listdir(source_dir)
    pdf_files = [f for f in files if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        file_to_txt(source_dir, destination_dir, pdf_file, "")
#        result = file_to_txt(source_dir, destination_dir, pdf_file, "")
#        if(result!=1): 
#            print("{0}: {1}".format(pdf_file, result))
    
    dir_handler.check_file_outcome(source_dir, destination_dir, "pdf2txt", source_type = "pdf", destination_type = "txt") 