import pandas as pd 
import html5lib
from bs4 import BeautifulSoup
import requests
import os 
import argparse


## 참고 : https://excelsior-cjh.tistory.com/109

def get_url(item_name, code_df):

    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    code=code.strip(' ')
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    print("요청 URL = {}".format(url)) 
    return url, code


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--item_name', type=str,required=True)

    args = parser.parse_args()

    if not os.path.isfile('./data/code_list.csv'):
        code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
        code_df.to_csv('./data/code_list.csv',index=False)

    code_df=pd.read_csv('./data/code_list.csv')
    
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    
    if not os.path.isfile('./code_name.csv'): 
        code_df.to_csv('./code_name.csv')


    url,code=get_url(args.item_name,code_df)
    df=pd.DataFrame()
   
    page=1
    r=requests.get('https://finance.naver.com/item/sise_day.nhn?code='+code+'&page=1')
    soup = BeautifulSoup(r.text, 'html.parser')
    end=1
    
    for i in soup.findAll('a'):
        if '맨뒤' in i.text:
            end=int(i.attrs['href'].split('=')[-1])

    for i in range(end):
        if page%100==0:
            print('현 page:',page)
        pg_url = '{url}&page={page}'.format(url=url, page=page) 
        
        
        df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True)
        page+=1

  
    df.dropna(inplace=True)
    df = df.rename(columns= {'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'}) 
    df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int) 
    df = df.sort_values(by=['date'], ascending=True)

    df.to_csv("./data/"+code+'.csv') 

    print('저장완료!')