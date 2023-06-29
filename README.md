# pythondatautil
Pythonのファイル処理をより楽に行うためのライブラリ


## シェルコマンド一覧
#### インストール
```console
python -m pip install git+https://github.com/m-ippei/pythondatautil.git
```
#### アップデート
```console
python -m pip install git+https://github.com/m-ippei/pythondatautil.git -U
```
#### アンインストール
```console
python -m pip uninstall pythondatautil
```

## 使い方

```Python
from pythondatautil import DataUtil

du = DataUtil()

# テキストファイルの自動読み込み
"""tmp1.txt
Hi!
"""

data = du.r_auto("tmp1.txt")
print(data) # Hi!

# データの自動書き込み
du.w_auto([1,2,3]) 

"""tmp2.txt
1
2
3
"""
```

## 簡易リファレンス

r_auto,w_auto の自動読み込みおよび自動書き込み対象は⭐️マーク その他は直接指定が必要

### r:Read系
* r_auto(path_string) 拡張子または中身から自動変換読み込み ※1次元の改行区切り文字列はr_csvで読み込んで1次元のリストにする
* r_txt(path_string) テキストファイル→文字列
* r_csv(path_string) CSVファイル→リスト ⭐️
* r_tsv(path_string) TSVファイル→リスト ⭐️
* r_json(path_string) JSONファイル→辞書 ⭐️
* r_pickle(path_string) pickleファイル→辞書 ⭐️

### w:Write系
* w_auto(any_data) ファイルの中身から判断して自動でファイル書き出し ※辞書型のデフォルト書き出しはw_dict(dict)
* w_txt(some_string) テキスト書き込み
* w_log(string or list ...) ログテキスト書き込み　追記+改行
* w_list(list) リスト書き込み 改行区切り ⭐️
* w_list_lf(list) w_listの改行コードがLFバージョン
* w_csv(list) 2次元リスト書き込み　通常CSV書き込み 拡張子は.txt ※エクセルで直接開くことが可能な文字コードShift_JIS形式のcsv書き出しは対応していません ⭐️
* w_csv_lf(list) w_csvの改行コードがLFバージョン
* w_tsv(list) w_csvのtsvバージョン
* w_dict(dict) 辞書型を整形してテキストファイルで書き出す(pprintによるファイル書き出し) ⭐️
* w_json(dict) 辞書型をJSONファイルで書き出す
* w_pickle(dict) 辞書型をPickleファイルで書き出す

#### その他

* str_to_list(some_string) 改行の区切りの文字列を直接引数から受け取ってリストにして返す　空白行は除去する
* yyyymmdd YYYYMMDD形式の現在の日付文字列を返す　→例:print(du.yyyymmdd)

#### ファイル書き込み時のfilename省略
* 同じ階層からtmp<数字>のファイル名を見つけ出し、<maxの数字>+1の連番で作成。
* w_logの場合でfilenameを省略した場合は、yyyymmdd.txtでファイルを作成

## 備考
文字コードはUTF-8のみが対象


