import datetime
from pprint import pprint
import pickle
import json
import csv
import os
import re

class DataUtil:

    def __init__(self):
        pass

    def __getTmpName(self,ext:str=".txt") -> str:
        """一時的なファイル名の作成

        DataUtilが実行された階層のファイル名を確認してtmp<数字>のファイル名を作成

        Args:
            ext (str): 拡張子
        
        Returns:
            tmpName (str): tmp<数字>.<拡張子>
        
        """
        re_obj = re.compile(r"tmp\d{1,}")
        re_obj2 = re.compile(r"\D")

        #tmp+数字のファイルリストを抽出して、なおかつそこから数字を取り出し、最も大きい数字から一つ足したものを新しいテキストファイルの追加数字とする
        tmp_num_list = [int(re_obj2.sub("",re_obj.search(v).group())) for v in os.listdir(os.getcwd()) if re_obj.search(v)]
        return f"tmp{max([0] if tmp_num_list == [] else tmp_num_list)+1}{ext}"

    def __getFileNameHelper(self,order_file_name,ext=".txt"):
        """適切なファイル名を取得する関数

        ・ファイル名の指定が無ければ、tmpファイル名を取得
        ・ファイル名がの指定があれば、適切なファイル名かチェックして取得
        ・パス名の指定があれば、パスをチェックして適切なファイル名を取得

        Args:
            order_file_name (str): 空文字またはパス名またはファイル名
            ext (str): 指定の拡張子
        
        Returns:
            file_name (str): ファイル(パス)名
        
        """

        file_name = order_file_name
        file_name_head,order_ext = os.path.splitext(file_name)

        if type(order_file_name) != str:
            raise ValueError("ファイル名は文字列である必要があります")

        if "" == order_file_name:
            return self.__getTmpName(ext)

        if os.path.isdir(file_name):
            raise ValueError("フォルダパスを含める場合はファイル名も指定してください")
        
        if os.path.exists(os.path.dirname(file_name)):
            if order_ext:
                if ext != order_ext:
                    raise ValueError(f"有効な拡張子ではありません。{os.path.basename(file_name)}")
            else:
                file_name = f"{file_name}{ext}"

        else:
            if "" == os.path.dirname(file_name):
                if order_ext:
                    return file_name
                else:
                    file_name = f"{file_name_head}{ext}"
            else:
                raise ValueError("存在するフォルダを指定してください。")
        
        return file_name
    
    def __isTSV(self,path):
        """TSVのパスを読み込んでTSVかどうかを判断する

        Args:
            path (str): パス名 

        Returns:
            bool
        """
        with open(path,mode='r',encoding='utf-8') as f:
            if "\t" in f.readline():
                return True
            else:
                return False
    
    def __isSameContentLength_2dList(self,content_list):

        """2次元Listの中身のListの個数が揃っているかのチェック
        
        ・List型のデータが全てList型として入っている場合は、それぞれの個数が合っているかの確認
        ・List型のデータが全てList型として入っていない場合で、List型が含まれる場合はエラーとする

        Args:
            content_list (list): チェックデータ

        Returns:
            bool
        """

        if type(content_list) != list:
            raise ValueError("引数:content_listはlist型である必要があります。")
        
        content_list_len = len(content_list)

        if content_list_len > 0:

            #リストの中身がリストである数を数える
            list_in_list_len = len([v for v in content_list if type(v) == list ])

            #リスト型の中身が全てリスト型である場合
            if list_in_list_len == content_list_len:
                
                item_len = len(content_list[0])
                item_len_index = 1

                for index,v in enumerate(content_list,start=1):
                    
                    if item_len != len(v):
                        raise ValueError(f"一致しないデータ数 {item_len_index}行目:{item_len}個,{index}行目:{len(v)}個")
                
                    item_len_index = index

            else:
                #elseに落ちた場合で、0個以上リスト型がある場合は、型混在パターンとなるので許容しない。
                if list_in_list_len > 0:
                    raise ValueError(f"list型の中にList型とそれ以外を混在させることできません。")
                
        return True

    
    def r_txt(self,path):
        """テキストファイルのパスから中身の文字列を返す

        Args:
            path (str): パス名 

        Returns:
            content (str): 文字列
        """
        with open(path,mode='r',encoding='utf-8') as f:
            return f.read()

    def r_csv(self,path) -> list:
        """CSVのパスを読み込んでリストにして返す

        Args:
            path (str): パス名 

        Returns:
            list (list): リスト
        """
        with open(path,mode='r',encoding='utf-8') as f:
            return [v for v in csv.reader(f)]

    def r_tsv(self,path) -> list:
        """TSVのパスを読み込んでリストにして返す

        Args:
            path (str): パス名 

        Returns:
            list (list): リスト
        """
        with open(path,mode='r',encoding='utf-8') as f:
            return [v for v in csv.reader(f,delimiter="\t")]

    def r_json(self,json_path):
        """JSONのパスを読み込んで辞書型にして返す

        Args:
            path (str): パス名 

        Returns:
            dict (dict): 辞書型
        """
        with open(json_path,mode='r',encoding='utf-8') as f:
            return json.load(f)

    def r_pickle(self,pickle_path):
        """Pickleファイルのパスを読み込んで辞書型にして返す

        Args:
            path (str): パス名 

        Returns:
            dict (dict): 辞書型
        """
        with open(pickle_path,mode='rb') as f:
            return pickle.load(f)
        

        
    def r_auto(self,path):
        """データを読み込む関数

        引数に入れられたパスから自動でファイル形式を判断して読み込みを行ってデータを返す

        Args:
            path (str): ファイルパス名[.txt .csv .json .pickle]
        
        Returns:
            any (any): データ[list dict]
        
        """
        ext = os.path.splitext(path)[1]
        if (ext == ".txt") or (ext == ".csv"):
            content_list = None
            
            if self.__isTSV(path):
                content_list = self.r_tsv(path)
            else:
                content_list = self.r_csv(path)

            #二次元のリストの中身が1つの場合、一次元リストにする
            if len([len(v) for v in content_list if len(v) == 1]) == len(content_list):
                return [v[0] for v in content_list]

            return content_list

        elif ext == ".json":
            return self.r_json(path)
        elif ext == ".pickle":
            return self.r_pickle(path)
        else:
            raise ValueError(f"自動で読込処理ができない値: {os.path.basename(path)}")

    def w_txt(self,txt,filename = ""):
        """テキストファイルを書き出す
        """
        with open(self.__getFileNameHelper(filename),mode='w',encoding='utf-8') as f:
            f.write(txt)

    def w_log(self,content,filename = ""):
        """テキストをログ形式で書き出す
        """
        if type(content) == str:
            pass
        elif type(content) == list:
            content = ",".join([str(v) for v in content])
        elif type(content) == tuple:
            content = ",".join([str(v) for v in content])
        else:
            content = str(content)

        if filename == "":
            # w_logでファイル名を指定した際に、tmpファイルを行ごとに作成させないため。
            filename = self.yyyymmdd       

        with open(self.__getFileNameHelper(filename),mode='a',encoding='utf-8') as f:
            f.write(f"{content}\n")

    def w_list(self,content_list,filename = ""):
        """改行区切りのリストを書き出す
        """
        with open(self.__getFileNameHelper(filename),mode='w',encoding='utf-8') as f:
            for v in content_list:
                f.write(f"{v}\n")

    def w_list_lf(self,content_list,filename = ""):
        """改行区切りのリストを書き出す(改行コード:LF)
        """
        with open(self.__getFileNameHelper(filename),mode='w',encoding='utf-8',newline='\n') as f:
            for v in content_list:
                f.write(f"{v}\n")

    def w_csv(self,content_list,filename = ""):
        """CSVを書き出す
        """
        with open(self.__getFileNameHelper(filename),mode='w',encoding='utf-8',newline='\n') as f:
            csv.writer(f).writerows(content_list)

    def w_csv_lf(self,content_list,filename = ""):
        """CSVを書き出す(改行コード:LF)
        """
        with open(self.__getFileNameHelper(filename),mode='w',encoding='utf-8',newline='') as f:
            csv.writer(f,lineterminator="\n").writerows(content_list)

    def w_tsv(self,content_list,filename = ""):
        """TSVを書き出す
        """
        with open(self.__getFileNameHelper(filename),mode='w',encoding='utf-8',newline='\n') as f:
            csv.writer(f,delimiter="\t").writerows(content_list)

    def w_dict(self,dic,filename = ""):
        """辞書型を整形してテキストファイルで書き出す
        """
        with open(self.__getFileNameHelper(filename),mode='w',encoding='utf-8') as f:
            pprint(dic,stream=f)

    def w_json(self,dic,filename = ""):
        """辞書型をJSONファイルで書き出す
        """
        with open(self.__getFileNameHelper(filename,ext=".json"),mode='w',encoding='utf-8') as f:
            json.dump(dic,f,indent=2,ensure_ascii=False)

    def w_pickle(self,dic,filename = ""):
        """辞書型をPickleファイルで書き出す
        """
        with open(self.__getFileNameHelper(filename,ext=".pickle"),mode='wb') as f:
            pickle.dump(dic,f)

    def w_auto(self,any_data,filename=""):
        """データを書き出す関数

        引数に入れられたデータ型から自動でファイル形式を判断して書き出しを行う。

        Args:
            any_data (any): データ[str,list,dict]
            filename (str): ファイル名やファイルパス名(オプション)
        
        """
        if type(any_data) == str:
            self.w_txt(any_data,filename)
        elif type(any_data) == list:
            if len(any_data) == 0:
                raise ValueError("リストの中身が空です。")
            
            if type(any_data[0]) == list:
                self.w_csv(any_data,filename)
            else:
                self.w_list(any_data,filename)
        elif type(any_data) == dict:
            self.w_dict(any_data,filename)
        else:
            raise ValueError("引数が文字列かリストか辞書ではありません。")
        
    def str_to_list(self,raw_str):
        """改行区切りの文字列をリストにして返す。

        改行区切りの文字列を空白を取り除いてリストにして返す。

        Args:
            raw_str (str): 対象の文字列 

        Returns:
            list (list): リスト
        """
        if type(raw_str) != str:
            raise ValueError("文字列→リスト変換の引数は文字列のみ対応しています。")

        data = [v.strip() for v in raw_str.split("\n")]
        data = [v for v in data if v != ""]

        isInComma = "," in raw_str
        isInTab = "\t" in raw_str
        
        if isInComma and isInTab:
            raise ValueError("「,」とタブ文字が混在しているものは変換できません。")
        elif isInComma:
            data = [v.split(",") for v in data]
        elif isInTab:
            data = [v.split("\t") for v in data]

        if self.__isSameContentLength_2dList(data):
            return data
        else:
            raise ValueError("想定外の入力値 リストに変換できません。")

    @property
    def yyyymmdd(self):
        """YYYYMMDD形式の日付文字列を返す"""
        return datetime.datetime.now().strftime("%Y%m%d")
