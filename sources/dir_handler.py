#-----------------directory handler-----------------
import os 
import sources.reg_exp_util as reg_util 


#def get_curr_dir(): 
#    curr_dir = os.getcwd()
#    curr_dir = cleanse_dir(curr_dir)
#    return curr_dir

#def concat_dir(base_dir, add_dir): 
#    destination_dir = "{0}/{1}".format(base_dir, add_dir)
#    destination_dir = cleanse_dir(destination_dir)
#    return destination_dir

def cleanse_dir(dir_): 
    """Return path with / isntead of \\"""
    dir_ = os.path.abspath(dir_)
    return (dir_).replace('\\','/')

def delete_files(dir_): 
    """Delete all fiels from a certain directory"""
    dir_ = cleanse_dir(dir_)
    
    files = os.listdir(dir_) 
    for file_name in files: 
        os.unlink(dir_+'/'+file_name)
    
    return 1    

def clean_temp_files():
    """Clean all temp files in tmp/decrypted_pdf and tmp/txt"""
    delete_files('tmp/decrypted_pdf')
    delete_files('tmp/txt')
    return 1

def clean_previous_result():
    """Clean previous results (all files in output_csv) and temp files (tmp/decrypted_pdf and tmp/txt)"""
    delete_files('tmp/decrypted_pdf')
    delete_files('tmp/txt')
    delete_files('output')
    return 1


def get_files(source_dir, keep_type): 
    source_files = os.listdir(cleanse_dir(source_dir))
    destination_list = []
    
    for file in source_files: 
        split = file.split('.')
        if(len(split)==1): 
            continue
        elif(split[1]==keep_type): 
            destination_list.append(split[0])
    
    return destination_list
    
def check_file_outcome(source_dir, destination_dir, step, source_type = 'pdf', destination_type = 'pdf'): 
    """Compare input pdf (input_pdf/) and txt files (tmp/txt/) 
        and print message if any of the files in input_pdf is not successfully transferred into txt"""
    source_files = get_files(source_dir, source_type)
    destination_files = get_files(destination_dir, destination_type)
    
    fail_set = set(source_files)-set(destination_files)
    fail_list = list(fail_set)

    if(len(fail_list)==0): 
        print("{} - success. ".format(step))
    else: 
        print("{0} - failure items: {1}".format(step, fail_list))
    
    return fail_list