from work3_Analytics import work3

if __name__=="__main__":
    while True:
        pattern = work3.first_pattern()
        print(f"あなたが選択したもの:{pattern}")

        if pattern == None:
            break
        mra_out , data_mediRE, result, tps_out , data_medi , result , data_medi_new_except_criterion = work3.financial_pointer_analyzer(pattern,work3.total_power_survey,work3.multiple_regression_analysis)
        if  mra_out is None or tps_out is None:
            print("操作を終了します")
            break
        if type(mra_out) == int:
            print(tps_out)
        if type(tps_out) == int:
            print(mra_out)

        while True :
            c_flag = work3.check_enterprize(pattern, mra_out , data_mediRE, tps_out , data_medi , result , data_medi_new_except_criterion) 
            if type(c_flag) == bool:
                break
            print(c_flag)
            
            



        


