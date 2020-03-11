#-----------------txt_to_csv-----------------
import pandas as pd 
import os 
import time
import sources.reg_exp_util as reg_util 
import sources.dir_handler as dir_handler
import csv


LOAN_COLUMNS = ["UID","CREATED_TIMESTAMP","DATA_YM","BANK_CODE","BANK_NAME", "CONTRACT_AMT1","LOAN_AMT","ACCOUNT_CODE","LOAN_DEFER_PMT"]
CC_COLUMNS = ["UID","CREATED_TIMESTAMP","ISSUE", "ISSUE_NAME","CARD_NAME","CARD_TYPE","CREDIT_LIMIT",
              "START_DATE","STOP_DATE","STOP_CODE","AB_CODE"]
CC_PAYMENT_COLUMNS = ["UID","CREATED_TIMESTAMP","BILL_DATE","ISSUE", "ISSUE_NAME","PAY_STAT","PAY_CODE",
                      "PERM_LIMIT","CASH_LENT","PAYABLE","PRE_OWED","CLOSE_CODE","DEBT_CODE"]
INQUIRY_COLUMNS = ["UID","CREATED_TIMESTAMP","QUERY_DATE","BANK_CODE","BANK_NAME", "INQ_PURPOSE_1"]
J10_COLUMNS = ["UID","CREATED_TIMESTAMP","J10"]
ID_TIMESTAMP_COLUMNS = ["UID", "CREATED_TIMESTAMP"]



def remove_excessive_info(block): 

    block = reg_util.replace_text_by_reg(block, "(?:[\s]*?[\n])+", "\n")
    block = reg_util.remove_text_by_reg(block, "【.+】.+?\n+?如下：")
    block = reg_util.remove_text_by_reg(block, "【.+】.+?\n")
    block = reg_util.remove_text_by_reg(block, "[-]+?\n")
    block = reg_util.remove_text_by_reg(block, "查詢日期查詢機構查詢理由\n")
    block = reg_util.remove_text_by_reg(block, "發卡機構卡名額度發卡日期停用日期使用狀態\n")
    block = reg_util.remove_text_by_reg(block, "[A-Z]{1}[0-9]{13}\n")
    block = reg_util.remove_text_by_reg(block, "報表編號.+?\n當事人綜合信用報告.+?\n謹慎使用信用報告.+?\n")
    block = reg_util.remove_text_by_reg(block, "金融機構名稱訂約金額[(]千元[)]借款餘額[(]千元[)]科目最近十二個月\n有無延遲還款")
    block = reg_util.remove_text_by_reg(block, "主卡人[:：][A-Z]{1}[0-9]{9}.*")
    block = reg_util.remove_text_by_reg(block, "※(?:.*?[\n]*?)*?仍可能持續報送延遲繳款資料。")
    block = reg_util.remove_text_by_reg(block, "[(].*?[)](?:\n|$)")
    block = reg_util.remove_text_by_reg(block, "欠款結清日期.*?(?:\n|$)")
    block = reg_util.remove_text_by_reg(block, "公司[:].*?(?:\n|$)")
    block = reg_util.replace_text_by_reg(block, "(?:[\s]*?[\n])+", "\n")
    block = reg_util.remove_text_by_reg(block, "[\n]*[=-]+?$")
    block = reg_util.remove_text_by_reg(block, "^(?:[\s]*?\n)+")
    block = reg_util.remove_text_by_reg(block, "(?:[\s]*?\n)+$")

    return block


def remove_excessive_info_spaced(block): 
    
    block = reg_util.remove_text_by_reg(block, "(?:[-][\s])+")
    block = reg_util.replace_text_by_reg(block, "(?:[\s][\n])", "\n")
    block = reg_util.replace_text_by_reg(block, "[\n]+", "\n")
    block = reg_util.remove_text_by_reg(block, "【\s(?:.[\s])+?】.+?\n")
    block = reg_util.remove_text_by_reg(block, "[\s]結[\s]+?帳[\s]+?日[\s]+?(?:.|[\s\n]+)+?債[\s]權[\s]狀[\s]態[\s]+\n")
    block = reg_util.remove_text_by_reg(block, " [(] (?:[*]\s){3}金 額 負 號 代 表 有 溢 繳 (?:[*]\s){3}[)]\n")
    block = reg_util.remove_text_by_reg(block, "\n(?:[=-][\s])+$")
    block = reg_util.remove_text_by_reg(block, "^\n+")
    block = reg_util.remove_text_by_reg(block, "\n\s*?$")
    
    return block






def parse_id_timestamp(file_name, text): 
    inquiry_date = reg_util.find_first_reg(text, "報表編號:.*?((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})").replace('/','')
    idn = file_name
#    idn = reg_util.find_first_reg(text, "身分證號：([A-Za-z][0-9]{9})") 
    columns = ID_TIMESTAMP_COLUMNS
    data = pd.DataFrame([['{}'.format(idn), inquiry_date]], columns=columns)
    return data



def parse_j10_info(file_name, text): 
    
    inquiry_date = reg_util.find_first_reg(text, "報表編號:.*?((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})").replace('/','')
    idn = file_name
#    idn = reg_util.find_first_reg(text, "身分證號：([A-Za-z][0-9]{9})") 
    
    block = reg_util.find_first_reg(text, "(【信用評分】[\s\S\n]*?)$") 
    #print("block:", block)
    
    columns = J10_COLUMNS
    data_set = pd.DataFrame(columns=columns)
    
    if(block != None): 
        j10 = reg_util.find_first_reg(block, "信用評分[:：]([0-9]+)分") 
        #print(j10)
        data = pd.DataFrame([[idn, inquiry_date, j10]], columns=columns)
        data_set = data_set.append(data, ignore_index=True, sort=False)
   
    return data_set


def parse_bank_code(text): 
    bank_code = ''
    bank_pattern= "(?:銀行|商業銀行|商銀)"
    credit_union_pattern="(?:信用合作社|信用合社)"
    association_pattern="(?:農會|漁會|郵局)"
    
    match = []
    
    if(reg_util.find_if_match_any(text, ["臺灣{}".format(bank_pattern)]) is not None): bank_code='004'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["土地"]) is not None): bank_code='005'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["合作金庫"], ["合作金庫票券"]) is not None): bank_code='006'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["第一.*?{}".format(bank_pattern)]) is not None): bank_code='007'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["華南.*?"]) is not None): bank_code='008'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["彰化.*?{}".format(bank_pattern)]) is not None): bank_code='009'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["上海", "上海商業儲蓄銀行"]) is not None): bank_code='011'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["富邦"]) is not None): bank_code='012'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["國泰世華"]) is not None): bank_code='013'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["中國輸出入"]) is not None): bank_code='015'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["高雄{}".format(bank_pattern)]) is not None): bank_code='016'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["兆豐.*?"]) is not None): bank_code='017'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["全國農業金庫"]) is not None): bank_code='018'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["瑞穗"]) is not None): bank_code='020'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["花旗"]) is not None): bank_code='021'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["泰國盤谷"]) is not None): bank_code='023'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["新加坡大華"]) is not None): bank_code='029'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["澳盛.*?"]) is not None): bank_code='039'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["王道"]) is not None): bank_code='048'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["臺灣中小企業", "[台臺]灣企銀"]) is not None): bank_code='050'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["渣打"]) is not None): bank_code='052'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["台中{}".format(bank_pattern)]) is not None): bank_code='053'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["京城"]) is not None): bank_code='054'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["兆豐票券"]) is not None): bank_code='060'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["中華票券"]) is not None): bank_code='061'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["國際票券"]) is not None): bank_code='062'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["大中票券"]) is not None): bank_code='063'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["台灣票券"]) is not None): bank_code='065'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["萬通票券"]) is not None): bank_code='066'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["香港商東亞"]) is not None): bank_code='075'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["匯豐", "匯豐[(（]?台灣[)）]?"]) is not None): bank_code='081'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["法商法國巴黎"]) is not None): bank_code='082'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["新加坡商新加坡華僑"]) is not None): bank_code='085'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["法商東方匯理"]) is not None): bank_code='086'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["瑞士商瑞士"]) is not None): bank_code='092'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["日商三菱日聯"]) is not None): bank_code='098'; match.append(bank_code);    
    if(reg_util.find_if_match_any(text, ["瑞興"]) is not None): bank_code='101'; match.append(bank_code);    
    if(reg_util.find_if_match_any(text, ["華泰"]) is not None): bank_code='102'; match.append(bank_code);    
    if(reg_util.find_if_match_any(text, ["臺灣新光"]) is not None): bank_code='103'; match.append(bank_code);    
    if(reg_util.find_if_match_any(text, ["陽信"]) is not None): bank_code='108'; match.append(bank_code);    
    if(reg_util.find_if_match_any(text, ["聯邦"]) is not None): bank_code='803'; match.append(bank_code);    
    if(reg_util.find_if_match_any(text, ["遠東.*?"]) is not None): bank_code='805'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["元大","大眾"], ["元大證券"]) is not None): bank_code='806'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["永豐"]) is not None): bank_code='807'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["玉山"]) is not None): bank_code='808'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["凱基"]) is not None): bank_code='809'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["星展", "星展[(（]?台灣[）)]?"]) is not None): bank_code='810'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["台新.*?"]) is not None): bank_code='812'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["日盛.*?"]) is not None): bank_code='815'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["安泰.*?"]) is not None): bank_code='816'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["中信銀", "中國信託"]) is not None): bank_code='822'; match.append(bank_code);
    
    if(reg_util.find_if_match_any(text, ["財團法人聯合信用卡處理中心"]) is not None): bank_code='956'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['樂天(?:信用卡)?']) is not None): bank_code='960'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["永旺信用[卡]?"]) is not None): bank_code='978'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["元大證券"]) is not None): bank_code='995'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ["美國運通"]) is not None): bank_code='A82'; match.append(bank_code);
    
    if(reg_util.find_if_match_any(text, ['台北市第五{}'.format(credit_union_pattern)]) is not None): bank_code='104'; match.append(bank_code);    
    if(reg_util.find_if_match_any(text, ['基隆第一{}'.format(credit_union_pattern)]) is not None): bank_code='114'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['基隆市第二{}'.format(credit_union_pattern)]) is not None): bank_code='115'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['板信{}'.format(bank_pattern)]) is not None): bank_code='118'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['淡水第一{}'.format(credit_union_pattern)]) is not None): bank_code='119'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['淡水{}'.format(credit_union_pattern)]) is not None): bank_code='120'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['宜蘭{}'.format(credit_union_pattern)]) is not None): bank_code='124'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['桃園{}'.format(credit_union_pattern)]) is not None): bank_code='127'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['新竹第一{}'.format(credit_union_pattern)]) is not None): bank_code='130'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['新竹三信', '新竹第三{}'.format(credit_union_pattern)]) is not None): bank_code='132'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['台中市第二{}'.format(credit_union_pattern)]) is not None): bank_code='146'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['三信{}'.format(bank_pattern)]) is not None): bank_code='147'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['彰化第一{}'.format(credit_union_pattern)]) is not None): bank_code='158'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['彰化第五{}'.format(credit_union_pattern)]) is not None): bank_code='161'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['彰化第六{}'.format(credit_union_pattern)]) is not None): bank_code='162'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['彰化第十{}'.format(credit_union_pattern)]) is not None): bank_code='163'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['彰化縣鹿港{}'.format(credit_union_pattern)]) is not None): bank_code='165'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['嘉義市第三{}'.format(credit_union_pattern)]) is not None): bank_code='178'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['臺南第三{}'.format(credit_union_pattern)]) is not None): bank_code='188'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['臺南第三{}'.format(credit_union_pattern)]) is not None): bank_code='188'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['高雄市第三{}'.format(credit_union_pattern)]) is not None): bank_code='204'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['花蓮第一{}'.format(credit_union_pattern)]) is not None): bank_code='215'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['花蓮第二{}'.format(credit_union_pattern)]) is not None): bank_code='216'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['澎湖縣第一{}'.format(credit_union_pattern)]) is not None): bank_code='222'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['澎湖第二{}'.format(credit_union_pattern)]) is not None): bank_code='223'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['金門縣{}'.format(credit_union_pattern)]) is not None): bank_code='224'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['日商三井住友{}'.format(bank_pattern)]) is not None): bank_code='321'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['大慶票券']) is not None): bank_code='372'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['合作金庫票券']) is not None): bank_code='375'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['國泰世紀產物保險公司']) is not None): bank_code='415'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['臺銀人壽']) is not None): bank_code='451'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['台灣人壽']) is not None): bank_code='452'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['保誠人壽']) is not None): bank_code='453'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['國泰人壽']) is not None): bank_code='454'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['中國人壽']) is not None): bank_code='455'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['南山人壽']) is not None): bank_code='456'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['新光人壽']) is not None): bank_code='458'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['三商美邦人壽']) is not None): bank_code='473'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['遠雄人壽']) is not None): bank_code='479'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['宏泰人壽']) is not None): bank_code='480'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['全球人壽']) is not None): bank_code='489'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['富邦人壽']) is not None): bank_code='495'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['香港商台灣環匯亞太信用卡']) is not None): bank_code='979'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['環華證券']) is not None): bank_code='981'; match.append(bank_code);
    if(reg_util.find_if_match_any(text, ['.*{}'.format(association_pattern)]) is not None): bank_code=reg_util.find_if_match_any(text, ['.*{}'.format(association_pattern)]); match.append(bank_code);
    
    if(len(match)!=1): 
        print("Unable to map unique bank code: {}, matches: {}".format(text, match))
        bank_code = text 
    
#    print(text, bank_code)

    return bank_code 


def parse_inquiry_info(file_name, text): 
    
    inquiry_date = reg_util.find_first_reg(text, "報表編號:.*?((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})").replace('/','')
    idn = file_name
#    idn = reg_util.find_first_reg(text, "身分證號：([A-Za-z][0-9]{9})") 
    block = reg_util.find_first_reg(text, "(【被查詢紀錄】[\s\S\n]*?)【(?:被電子支付機構查詢紀錄|被電子支付機構及電子票證發行機構查詢紀錄)】") 
#    print(block)

    block = remove_excessive_info(block) 
#    print("*"*20)
#    print(block)
#    print("*"*20)
    
    all_info = reg_util.find_all_reg(block, "([1]?[0-9]{2}/[0-9]{2}/[0-9]{2})([\u4e00-\u9fa5（）()－]+?)((?:(?:帳戶管理|新業務|原業務|其他[/][\u4e00-\u9fa5（）()]*?)[/]?)+)(?:\n|$)")
    
    
    if(check_line_cnt(block, all_info)==False): 
        raise ValueError('{0}: Failed to gain full information in {1}'.format(file_name, "【被查詢紀錄】"))

    
    columns = INQUIRY_COLUMNS
    data_set = pd.DataFrame(columns=columns)

    for i in range(len(all_info)): 
        info = all_info[i] 

        record_inquiry_date = info[0].replace('/','')
        bank_name = info[1]
        bank_code = "'"+parse_bank_code(bank_name)
        
        reason = info[2]

        data = pd.DataFrame([[idn, inquiry_date, record_inquiry_date, bank_code, bank_name, reason]], columns=columns)
        data_set = data_set.append(data, ignore_index=True, sort=False)
   
    return data_set




def parse_loan_info(file_name, text): 
    inquiry_date = reg_util.find_first_reg(text, "報表編號:.*?((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})").replace('/','')
    idn = file_name
#    idn = reg_util.find_first_reg(text, "身分證號：([A-Za-z][0-9]{9})") 
    block = reg_util.find_first_reg(text, "(【銀行借款資訊】[\s\S\n]*?)【逾期、催收或呆帳資訊】")
    #print(block)

    #data_ym
    data_info = reg_util.find_first_reg(block, "【銀行借款資訊】.*?\n*?((?:10|11|[0-9])[0-9]{1})年([0-9]{2})月底") 
    data_ym = data_info[0]+data_info[1]
    #print(data_ym)

    block = remove_excessive_info(block) 
    
    #loan_info
    all_info = reg_util.find_all_reg(block, "([\u4e00-\u9fa5]+).+?([-]?[0-9,]+)[*]+([-]?[0-9,]+)([\u4e00-\u9fa5]+)([有無])")
    #print(loan_info)
    
    if(check_line_cnt(block, all_info)==False): 
        raise ValueError('{0}: Failed to gain full information in {1}'.format(file_name, "【銀行借款資訊】"))

    #df: loan_data
    columns = LOAN_COLUMNS
    data_set = pd.DataFrame(columns=columns)

    for i in range(len(all_info)): 
        info = all_info[i] 

        bank_name = info[0] 
        bank_code = "'"+parse_bank_code(bank_name)
#        print(issue_name, bank_code)
        
        contract_amt = info[1].replace(',','') 
        current_bal = info[2].replace(',','') 
        loan_type = info[3] 
        dlq_status = info[4] 

        data = pd.DataFrame([[idn, inquiry_date, data_ym, bank_code, bank_name, contract_amt, current_bal, loan_type, dlq_status]], columns=columns)
        data_set = data_set.append(data, ignore_index=True, sort=False)

    return data_set


def check_line_cnt(block, all_info): 
    result = True
    lines = reg_util.find_all_reg(block, "\n")
    
    if(block==""): 
        result = True
    elif(len(all_info)!=len(lines)+1): 
        result = False
#        print("block:\n****************\n{}\n****************\n".format(block))
#        print("lines cnt: {}".format(len(lines)))
#        print("information captured: {}".format(len(all_info)))
        
    return result


def check_line_cnt_cc_payment(block, all_info): 
    result = True
    lines = reg_util.find_all_reg(block, "\n")
    
    if(block==""): 
        result = True 
    elif(len(all_info)!=((len(lines)+1)/2)): 
        result = False
#        print("block:\n****************\n{}\n****************\n".format(block))
#        print(len(lines))
#        print("information captured: {}".format(len(all_info)))
        
    return result


def parse_cc_info(file_name, text): 
    
    inquiry_date = reg_util.find_first_reg(text, "報表編號:.*?((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})").replace('/','')
    idn = file_name 
#    idn = reg_util.find_first_reg(text, "身分證號：([A-Za-z][0-9]{9})") 
    block = reg_util.find_first_reg(text, "(【信用卡資訊】[\s\S\n]*?)【信用卡戶帳款資訊】") 
#    print(block)
    
    block = remove_excessive_info(block)
#    print("*"*20)
#    print(block)
#    print("*"*20)
    
    all_info = reg_util.find_all_reg(block, "([\u4e00-\u9fa5（）()]+)(美國運通[A-Za-z\u4e00-\u9fa5　─]*|運通簽帳[A-Za-z\u4e00-\u9fa5　─]*|大　　[A-Za-z\u4e00-\u9fa5　─]*|[A-Za-z]+[\u4e00-\u9fa5　─]+|[A-Za-z]+[\u4e00-\u9fa5　─]+)[(]([正附])[)]([0-9]*?)((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})?([\u4e00-\u9fa5]+):?([\u4e00-\u9fa5]+)?")
    
    if(check_line_cnt(block, all_info)==False): 
        raise ValueError('{0}: Failed to gain full information in {1}'.format(file_name, "【信用卡資訊】"))
    
    
    columns = CC_COLUMNS
    data_set = pd.DataFrame(columns=columns)

    for i in range(len(all_info)): 
        info = all_info[i] 

        issue_name = info[0] #[0:2] 
        issue = "'"+parse_bank_code(issue_name)
        
        card_name = info[1] 
        card_type = info[2]+'卡'
        limit = info[3]
        start_date = reg_util.remove_text_by_reg(info[4],'/') 
        stop_date = reg_util.remove_text_by_reg(info[5],'/') 
        stop_code = info[6] 
        ab_code = info[7]

        data = pd.DataFrame([[idn, inquiry_date, issue, issue_name, card_name, card_type, limit, start_date, stop_date, stop_code, ab_code]], columns=columns)
        
        data_set = data_set.append(data, ignore_index=True, sort=False)
   
    return data_set


def parse_cc_payment_info(file_name, text): 
    inquiry_date = reg_util.find_first_reg(text.replace(' ',''), "報表編號:.*?((?:10|11|[0-9])[0-9]{1}/[0-9]{2}/[0-9]{2})").replace('/','')
    idn = file_name
#    idn = reg_util.find_first_reg(text.replace(' ',''), "身分證號：([A-Za-z][0-9]{9})") 

    revised_text = reg_util.remove_text_by_reg(text, "報[\s]?表[\s]?編[\s]?號[\s]?:[\s]?[\S\s\n]*?保[\s]?障[\s]?良[\s]?好[\s]?信[\s]?用")
    revised_text = reg_util.remove_text_by_reg(revised_text, "[A-Z][0-9]{13}\n*")
    revised_text = reg_util.remove_text_by_reg(revised_text, "^\s*?[\n]")
    #print(revised_text)
    
    block = reg_util.find_first_reg(revised_text, "(【\s?信\s?用\s?卡\s?戶\s?帳\s?款\s?資\s?訊\s?】\s?[\s\S\n]*?)【\s?信\s?用\s?卡\s?債\s?權\s?再\s?轉\s?讓\s?及\s?清\s?償\s?資\s?訊\s?") 
    
    block = remove_excessive_info_spaced(block)
    
    all_info = reg_util.find_all_reg(block, "((?:(?:1\s?0\s?)|(?:1\s?1\s?)|(?:[0-9]\s?))(?:[0-9]\s?){1}/\s?(?:[0-9]\s?){2}/\s?(?:[0-9]\s?){2})\s*?((?:[\u4e00-\u9fa5（）()─]\s?)+)\s*?(?:[A-Za-z,()]\s?)*?\s{2,}((?:[-]\s?)?(?:[0-9]\s?)*?)\s*([有無])\s*?((?:[\u4e00-\u9fa5]\s?)*?)(?:\s*?\n)+\s*((?:[\u4e00-\u9fa5]\s?)*)\s*((?:[\u4e00-\u9fa5０-９]\s?)*)\s*((?:(?:[-]\s?)?[0-9]\s?)*)\s*((?:[-]\s?)?(?:[0-9]\s?)*)((?:[\u4e00-\u9fa5]\s?)*)")
    #print(all_info)
    
    if(check_line_cnt_cc_payment(block, all_info)==False): 
        raise ValueError('{0}: Failed to gain full information in {1}'.format(file_name, "【信用卡戶帳款資訊】"))
    
    columns = CC_PAYMENT_COLUMNS
    data_set = pd.DataFrame(columns=columns)


    for i in range(len(all_info)): 
        info = all_info[i] #print(info) 
        
        bill_date = reg_util.remove_text_by_reg(reg_util.remove_text_by_reg(info[0], ' '), '/') #print(bill_date)
        issue_name = reg_util.remove_text_by_reg(info[1], ' ') #print(issue_name)
        issue = "'"+parse_bank_code(issue_name)
        
        perm_limit = reg_util.remove_text_by_reg(info[2], ' ') #print(perm_limit)
        cash_lent = reg_util.remove_text_by_reg(info[3], ' ') #print(cash_lent)
        
        close_code = reg_util.remove_text_by_reg(info[4], ' ') #print(close_code)
        
        pay_stat = reg_util.remove_text_by_reg(info[5], ' ') #print(pay_stat) 
        pay_code = reg_util.remove_text_by_reg(info[6], ' ') #print(pay_code)
        
        payable = reg_util.remove_text_by_reg(info[7],' ') #print(payable)
        pre_owed = reg_util.remove_text_by_reg(info[8],' ') #print(pre_owed) 
        
        debt_code = reg_util.remove_text_by_reg(info[9],'\s') 
        debt_code = reg_util.remove_text_by_reg(debt_code,'\n')
		
        data = pd.DataFrame([[idn, inquiry_date, bill_date, issue, issue_name, pay_stat, pay_code, perm_limit, cash_lent, payable, pre_owed, close_code, debt_code]], 
                            columns=columns)
        data_set = data_set.append(data, ignore_index=True, sort=False)
	
    return data_set


def parse_jcic_data(text, file_name, data_type): 	
    if(data_type == 'loan'): 
        return parse_loan_info(file_name, reg_util.remove_text_by_reg(text, ' ')) 
    if(data_type == 'cc'): 
        return parse_cc_info(file_name, reg_util.remove_text_by_reg(text, ' ')) 
    if(data_type == 'cc_payment'): 
        return parse_cc_payment_info(file_name, text) 
	
    if(data_type == 'inquiry'): 
        return parse_inquiry_info(file_name, reg_util.remove_text_by_reg(text, ' '))#print(inquiry_info)
    if(data_type == 'j10'): 
        return parse_j10_info(file_name, reg_util.remove_text_by_reg(text, ' '))#print(j10_info)
    if(data_type == 'id_timestamp'): 
        return parse_id_timestamp(file_name, reg_util.remove_text_by_reg(text, ' '))
    
    return []

def get_file_content(path_name): 
    f = open(path_name,'r',encoding='utf-8')
    text = f.read()
    f.close()
    
    return text


def dir_to_csv(source_dir = 'tmp/txt', destination_dir = 'output_csv'): 
    source_dir = dir_handler.cleanse_dir(source_dir)
    destination_dir = dir_handler.cleanse_dir(destination_dir)
    
    #create dataframe
    loans = pd.DataFrame(columns=LOAN_COLUMNS)
    cc = pd.DataFrame(columns=CC_COLUMNS)
    cc_payment = pd.DataFrame(columns=CC_PAYMENT_COLUMNS)
    inquiry = pd.DataFrame(columns=INQUIRY_COLUMNS)
    j10 = pd.DataFrame(columns=J10_COLUMNS)
    id_timestamp = pd.DataFrame(columns=ID_TIMESTAMP_COLUMNS)

    #get jcic info from txt files (into dataframe)
    files = dir_handler.get_files(source_dir, "txt")
    files = ['{}.txt'.format(file) for file in files]
    known_issue = ["24580.txt", "27487.txt", "27721.txt", "27834.txt","27844.txt", "28426.txt","28551.txt"
                   ,"28143.txt"]
    
#    files = [files[0], files[1], files[2]]
    for i in range(len(files)): 
        file_name = files[i]
        try: 
            if(reg_util.find_first_reg(file_name, ".txt")==[]): 
                continue
            elif(file_name in known_issue): 
                print("known issue: {}".format(file_name))
            else: 
                file_path = source_dir+'/'+file_name #print(file_name)
                text = get_file_content(file_path)
                
                file_id = file_name.replace('.txt', '')
                
                loans = loans.append(parse_jcic_data(text, file_id, 'loan'), ignore_index=True, sort=False)
                cc = cc.append(parse_jcic_data(text, file_id, 'cc'), ignore_index=True, sort=False)
                cc_payment = cc_payment.append(parse_jcic_data(text, file_id, 'cc_payment'), ignore_index=True, sort=False)
                inquiry = inquiry.append(parse_jcic_data(text, file_id, 'inquiry'), ignore_index=True, sort=False)
                j10 = j10.append(parse_jcic_data(text, file_id, 'j10'), ignore_index=True, sort=False)
                id_timestamp = id_timestamp.append(parse_jcic_data(text, file_id, 'id_timestamp'), ignore_index=True, sort=False)
        except Exception as e: 
            print(e)


    #extract dataframe to csv
    timestamp = '' #time.strftime("_%y%m%d_%H%M") #西元年後二碼+月份+日期_小時+分鐘
    
    dir_handler.delete_files(destination_dir)

    loans.to_csv(destination_dir+'/BAM095'+timestamp+'.csv', index=False, encoding='big5')
    cc.to_csv(destination_dir+'/KRM046'+timestamp+'.csv', index=False, encoding='big5')
    cc_payment.to_csv(destination_dir+'/KRM040'+timestamp+'.csv', index=False, encoding='big5')
    inquiry.to_csv(destination_dir+'/STM007'+timestamp+'.csv', index=False, encoding='big5')
    j10.to_csv(destination_dir+'/j10'+timestamp+'.csv', index=False, encoding='big5')
    id_timestamp.to_csv(destination_dir+'/id_timestamp'+timestamp+'.csv', index=False, encoding='utf-8', sep=',', quotechar='"', doublequote=True, quoting = csv.QUOTE_NONNUMERIC)
    
    check_result(source_dir, destination_dir+'/id_timestamp.csv', "txt2csv", source_type="txt", known_issue=known_issue) 

    return 1


def check_result(source_dir = "tmp/txt", destination_file = "output_csv/id_timestamp.csv", step = "txt2csv", source_type="txt", known_issue=None): 
    source_files = dir_handler.get_files(source_dir, source_type)
    source_files = [file.replace(" ", "") for file in source_files]

    destination_file = dir_handler.cleanse_dir(destination_file)
    destination_df = pd.read_csv(destination_file, encoding='utf-8', sep=',', quotechar='"', doublequote=True)
    
    destination_list = destination_df.UID.to_list()
    destination_list = ['{}'.format(file) for file in destination_list]
    
    fail_set = set(source_files)-set(destination_list)
    fail_list = list(fail_set)
    
    if(len(fail_list)!=0): 
        known_issue = [x.replace('.txt','') for x in known_issue]
        print("known issue:", known_issue)
        print("{0} failure items: {1}".format(step, set(fail_list)-set(known_issue)))
    else: 
        print("{} - success. ".format(step))
        
    return fail_list
            
    
