#-----------------remove-----------------
import re

def remove_text_by_reg(text, reg_exp): 
    result = re.sub(reg_exp, "", text)
    return result

def replace_text_by_reg(text, reg_exp, replace_txt): 
    result = re.sub(reg_exp, replace_txt, text)
    return result

def find_first_reg(text, reg_exp): 
    #print("text:", text)
    #print("reg_exp:", reg_exp)
    result = re.findall(reg_exp, text)
    
    if(result == []): 
        return None 
    else: 
        return result[0]

def find_all_reg(text, reg_exp): 
    result = re.findall(reg_exp, text)
    return result

def find_if_match_any(text, match_exp_list=[], exclude_exp_list=[]): 
    match_result=None
    
    for reg_exp in match_exp_list: 
        find_result = find_first_reg(text, reg_exp)
#        print("find_result:", find_result)
        
        if(find_result is None): 
#            print("continue")
            continue
        else: 
            match_result = find_result
            
    for reg_exp in exclude_exp_list: 
        find_result = find_first_reg(text, reg_exp)
        if(find_result is None): 
            continue
        else: 
            match_result = None
    
#    print("match_result:", match_result) 
    
    return match_result
    
    