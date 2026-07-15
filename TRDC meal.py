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
    from selenium.webdriver.chrome.options import Options
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
url=""

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
#lunch_op=['NA','A','B','Noodle','Louisa','Louisa Veg','Special','Fruit','Vegan']
lunch_op=[]
lunch_box=ttk.Combobox(root,value=lunch_op)
lunch_box.grid(row=3,column=1)
#lunch_box.current(4)

dinner_label=tk.Label(root,text="Dinner : ")
dinner_label.grid(row=4,column=0)
#dinner_op=['NA','D_A','D_B','D_Noodle','D_Vegan']
dinner_op=[]
dinner_box=ttk.Combobox(root,value=dinner_op)
dinner_box.grid(row=4,column=1)
#dinner_box.current(0)

TODAY_MEAL={}

def tk_init(url,weekday):
    WED=''
    tmp_lunch=''
    tmp_dinner=''
    with open(os.path.join(path,'meal.json')) as f:
        MEAL=json.load(f)
    
    if weekday==0: #Monday -> Normal
        tmp_lunch=MEAL['Normal']['Lunch']
        tmp_dinner=MEAL['Normal']['Dinner']
    elif weekday==1 or weekday ==3: #Tuesday Thuresday -> Brunch
        tmp_lunch=MEAL['Brunch']['Lunch']
        tmp_dinner=MEAL['Brunch']['Dinner']      
    elif weekday==2 : # Wednesday
        options=Options()
        options.add_argument("--headless")
        try:
            driver=webdriver.Edge(options=options)
        except Exception:
            driver=webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(1)
        if 'OrderDailyMeals' not in driver.current_url:
            driver.find_element(By.ID,"tEid").send_keys(EMPLOYEE["ID"])
            driver.find_element(By.ID,"tPass").send_keys(EMPLOYEE["PW"])
            driver.find_element(By.CLASS_NAME,"btn").click()
            time.sleep(1)
            driver.get(url)
            time.sleep(1)
        WED=driver.find_elements(By.XPATH,"//div[contains(@class,'mb-0')]")
        if len(WED)==14: ## Car Food
            tmp_lunch=MEAL['Car']['Lunch']
            tmp_dinner=MEAL['Car']['Dinner']  
        else:
            tmp_lunch=MEAL['Normal']['Lunch']
            tmp_dinner=MEAL['Normal']['Dinner']  
    elif weekday==4: #Friday
            tmp_lunch=MEAL['Mos']['Lunch']
            tmp_dinner=MEAL['Mos']['Dinner'] 
    lunch_op=['NA']+list(tmp_lunch.keys())
    lunch_box['values']=lunch_op
    lunch_box.current(4)
    ## 4 = LOUISA

    dinner_op=['NA']+list(tmp_dinner.keys())
    dinner_box['values']=dinner_op
    dinner_box.current(0)
    
    global TODAY_MEAL
    TODAY_MEAL['NA']=-1
    TODAY_MEAL['Breakfast']=1
    TODAY_MEAL.update(tmp_lunch)
    TODAY_MEAL.update(tmp_dinner)
    
    
        
def order(url,lunch="Louisa",breakfast="Breakfast",dinner="NA"):
    #with open(os.path.join(path,'meal.json')) as f:
    #    MEAL=json.load(f)    
    lunch_index=TODAY_MEAL[lunch]
    breakfast_index=TODAY_MEAL[breakfast]
    dinner_index=TODAY_MEAL[dinner]
    try:
        #driver=webdriver.Edge()
        driver=webdriver.Chrome()
    except Exception:
        driver=webdriver.Chrome()
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
        
        LUNCH_flag=TODAY_MEAL['A']-2
        ## [0-1] 早餐 , [2-6] 自助A , [7-11] 自助B , [12-15] 麵食 , [16-17] L葷 , [18]L素
        ## [19-21] 水果 , [22-24] 特餐 , [25-26] 素食

        while(lunch_index>=LUNCH_flag): ##LUNCH
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
                    lunch_index-=1
                elif '訂餐時間已過' in err:
                    break               
                elif 'elementclickinterceptedexception' in err: ## Need to scoll the visable location to click button
                    pageY=driver.execute_script("return window.pageYOffset") 
                    driver.execute_script("window.scrollTo(0,"+str(pageY+350)+")") 
    
    if dinner_index!=-1:
        ##Dinner
        DINNER_flag=TODAY_MEAL['D_A']-2
        while(dinner_index>=DINNER_flag):
            try:
                btn=driver.find_elements(By.XPATH,"//button[contains(@class,'button')]")
                time.sleep(0.5)
                if 'blue' in btn[dinner_index].get_attribute('class') or 'Blue' in btn[dinner_index].get_attribute('class'):
                    btn[dinner_index].click()   
                    time.sleep(0.5)
                    driver.find_element(By.CLASS_NAME,"menu-active")
                    driver.find_element(By.CLASS_NAME,"btn-m").click()
                    time.sleep(1)
                    break
                elif 'Black' in btn[lunch_index].get_attribute('class') or 'Gray' in btn[lunch_index].get_attribute('class'):
                    raise Exception('此餐已訂完')
                else:
                    raise Exception('Wait Page Response...')
            except Exception as e:
                err=str(e)
                if 'elementclickinterceptedexception' in err:
                    pageY=driver.execute_script("return window.pageYOffset") 
                    driver.execute_script("window.scrollTo(0,"+str(pageY+350)+")") 
                elif '此餐已訂完' in err: ## Choose other meal if out of order
                    dinner_index-=1
                elif '訂餐時間已過' in err:
                    break  

    if breakfast_index!=-1:
        ##BREAKFAST
        BREAKFAST_flag=0
        while(breakfast_index>=BREAKFAST_flag):
            try:
                btn=driver.find_elements(By.XPATH,"//button[contains(@class,'button')]")
                time.sleep(0.5)
                if 'blue' in btn[breakfast_index].get_attribute('class') or 'Blue' in btn[breakfast_index].get_attribute('class'):
                    btn[breakfast_index].click()   
                    time.sleep(0.5)
                    driver.find_element(By.CLASS_NAME,"menu-active")
                    driver.find_element(By.CLASS_NAME,"btn-m").click()
                    break
                elif 'Black' in btn[lunch_index].get_attribute('class') or 'Gray' in btn[lunch_index].get_attribute('class'):
                    raise Exception('此餐已訂完')
                else:
                    raise Exception('Wait Page Response...')       
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
    global date_flag,today_flag,des_dt,url
    now=datetime.datetime.now()
    #now-=datetime.timedelta(days=1)
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
            url="https://app.inventec.com/iservicepwa/OrderDailyMeals.html?dt="+des_dt+"&site=TRDC"
            date_label.config(text="Next Order : "+des_dt)
            tk_init(url,delt_dt.weekday())
            root.update()
            date_flag=today
            
        elif today_flag!=today and datetime.time(20,2,00)>now.time()>datetime.time(19,58,00): ## Only Work at 19:58~20:02           
            #des_dt="2026-07-09"
            #url="https://app.inventec.com/iservicepwa/OrderDailyMeals.html?dt="+des_dt+"&site=TRDC"
            lunch=lunch_box.get()
            breakfast=breakfast_box.get()
            dinner=dinner_box.get()
            if not(lunch=='NA' and breakfast=='NA' and dinner =='NA'):
                order(url,lunch,breakfast,dinner)
            today_flag=today ## flag for order done
            lunch_box.current(4)
            breakfast_box.current(1)
            dinner_box.current(0)
    root.after(1000,check_time) ## instead of while loop
    

if __name__ == "__main__":
    check_time()
    root.mainloop()
