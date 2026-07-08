import time
import datetime
import holidays
import tkinter as tk
from tkinter import ttk
import os
import json
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
except ImportError:  
    import sys
    import subprocess
    subprocess.check_call([sys.executable,"-m","pip","install","selenuium"])
try:
    import holidays
except ImportError:  
    import sys
    import subprocess
    subprocess.check_call([sys.executable,"-m","pip","install","holidays"])


path=os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(path,'login.json')) as f:
    EMPLOYEE=json.load(f)    
tw_holidays=holidays.TW()
root=tk.Tk()
today_flag=-1
date_flag=-1
des_dt=""

root.title("TRDC ORDER")
id_label=tk.Label(root,text=EMPLOYEE["ID"][:3]+"*"*3+EMPLOYEE["ID"][-3:])
id_label.grid(row=0,column=0)
date_label=tk.Label(root,text="")
date_label.grid(row=1,column=0)
date_label.config(text="Next Order : ")
breakfast_label=tk.Label(root,text="Breakfast : ")
breakfast_label.grid(row=2,column=0)
breakfast_op=['NA','Breakfast']
breakfast_box=ttk.Combobox(root,value=breakfast_op)
breakfast_box.grid(row=2,column=1)
breakfast_box.current(1)

lunch_label=tk.Label(root,text="Lunch : ")
lunch_label.grid(row=3,column=0)
lunch_op=['NA','A','B','Noodle','Louisa','Louisa Veg','Special','Fruit','Vegan']
lunch_box=ttk.Combobox(root,value=lunch_op)
lunch_box.grid(row=3,column=1)
lunch_box.current(4)




class ORDER:
    def __init__(self,lunch_index=17,url=0):
        self.lunch_index=lunch_index
        self.url=url
        self.ID="IEC020337"
        self.PW="Iec_0987654321234567890"
        
def order(url,lunch="Louisa",breakfast="Breakfast"):
    with open(os.path.join(path,'meal.json')) as f:
        MEAL=json.load(f)    
    lunch_index=MEAL[lunch]
    breakfast_index=MEAL[breakfast]
    driver=webdriver.Edge()
    ##driver=webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    if 'OrderDailyMeals' not in driver.current_url:
        driver.find_element(By.ID,"tEid").send_keys(EMPLOYEE["ID"])
        driver.find_element(By.ID,"tPass").send_keys(EMPLOYEE["PW"])
        driver.find_element(By.CLASS_NAME,"btn").click()
        time.sleep(1)
        driver.get(url)
        time.sleep(1)


    if lunch_index!=-1:
        #btn=driver.find_elements(By.CLASS_NAME,"button")
        btn=driver.find_elements(By.XPATH,"//button[contains(@class,'button')]") ## find all clickable buttons
        time.sleep(0.5)
        
        LUNCH=2
        ## [0-1] 早餐 , [2-6] 自助A , [7-11] 自助B , [12-15] 麵食 , [16-17] L葷 , [18]L素
        ## [19-21] 水果 , [22-24] 特餐 , [25-26] 素食

        while(True): ##LUNCH
            try:
                if 'Black' in btn[lunch_index].get_attribute('class') or 'Gray' in btn[lunch_index].get_attribute('class'):
                    raise Exception('此餐已訂完') ### Un-clickable button marks as Black or Gray, raise to exception
                else:
                    btn[lunch_index].click()
                    time.sleep(0.5)
                    driver.find_element(By.CLASS_NAME,"menu-active") ## deal with the pop of confirmation
                    driver.find_element(By.CLASS_NAME,"btn-m").click()
                    time.sleep(1)
                    break
            except Exception as e:
                err=str(e)
                
                #if '20:00後預訂' in err:
                #    print('20:00後預訂')
                if '此餐已訂完' in err: ## Choose other meal if out of order
                    if lunch_index==LUNCH:
                        break
                    else:
                        lunch_index-=1
                elif '訂餐時間已過' in err:
                    break               
                elif 'elementclickinterceptedexception' in err: ## Need to scoll the visable location to click button
                    pageY=driver.execute_script("return window.pageYOffset") 
                    driver.execute_script("window.scrollTo(0,"+str(pageY+350)+")") 
    
    if breakfast_index!=-1:
        ##BREAKFAST
        btn=driver.find_elements(By.XPATH,"//button[contains(@class,'button')]")
        time.sleep(0.5)
        while(breakfast_index>-1):
            try:
                if 'blue' in btn[breakfast_index].get_attribute('class') or 'Blue' in btn[breakfast_index].get_attribute('class'):
                    btn[breakfast_index].click()   
                    time.sleep(0.5)
                    driver.find_element(By.CLASS_NAME,"menu-active")
                    driver.find_element(By.CLASS_NAME,"btn-m").click()
                    break
                else:
                    raise Exception('此餐已訂完')          
            except Exception as e:
                err=str(e)
                if 'elementclickinterceptedexception' in err:
                    driver.execute_script("window.scrollTo(0,0)")
                elif '此餐已訂完' in err: ## Choose other meal if out of order
                    breakfast_index-=1
                elif '訂餐時間已過' in err:
                    break  
        #driver.quit()
    driver.close()
   

def check_time():
    global date_flag,today_flag,des_dt
    now=datetime.datetime.now()
    today=now.weekday() # 0=Mon , 6=Sun
    if tw_holidays.is_working_day(now.date()): ## Only Work at working days
        if date_flag!=today: ## Do one time only
            wd=0
            delt_dt=now.date()
            while(wd<2): ## Check D+2 is working day, or D+2+N
                delt_dt+=datetime.timedelta(days=1)
                if tw_holidays.is_working_day(delt_dt):
                    wd+=1      
            des_dt=delt_dt.strftime("%Y-%m-%d")
            date_label.config(text="Next Order : "+des_dt)
            root.update()
            date_flag=today
            
        elif today_flag!=today and datetime.time(20,2,00)>now.time()>datetime.time(19,58,00): ## Only Work at 19:58~20:02           
            #des_dt="2026-07-08"
            url="https://app.inventec.com/iservicepwa/OrderDailyMeals.html?dt="+des_dt+"&site=TRDC"
            lunch=lunch_box.get()
            breakfast=breakfast_box.get()
            
            if not(lunch=='NA' and breakfast=='NA'):
                order(url,lunch,breakfast)
            today_flag=today ## flag for order done
            lunch_box.current(4)
            breakfast_box.current(1)
    root.after(1000,check_time) ## instead of while loop
    

if __name__ == "__main__":
    
    check_time()
    root.mainloop()