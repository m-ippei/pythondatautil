import csv
import datetime
import json
import pickle
import re
from typing import Any
from pathlib import Path
from pprint import pprint


class DataUtil:
    """DataUtilクラス"""

    def __getTmpName(self, ext: str = ".txt") -> str:
        """一時的なファイル名の作成

        DataUtilが実行された階層のファイル名を確認してtmp<数字>のファイル名を作成

        Args:
            ext (str): 拡張子

        Returns:
            tmpName (str): tmp<数字>.<拡張子>

        """
        re_obj = re.compile(r"tmp(\d+)")

        tmp_num_list = [
            int(m.group(1))
            for p in Path.cwd().iterdir()
            if (m := re_obj.search(p.name))
        ]

        return f"tmp{max(tmp_num_list, default=0) + 1}{ext}"

    def __getFileNameHelper(self, order_file_name: str, ext: str = ".txt") -> str:
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

        if order_file_name == "":
            return self.__getTmpName(ext)

        path = Path(order_file_name)

        if path.is_dir():
            raise ValueError("フォルダパスを含める場合はファイル名も指定してください")

        order_ext = path.suffix

        if path.parent != Path(".") and path.parent.exists():
            # 親ディレクトリが明示されていて存在する場合
            if order_ext:
                if ext != order_ext:
                    raise ValueError(f"有効な拡張子ではありません。{path.name}")
            else:
                path = path.with_suffix(ext)

        else:
            if path.parent == Path("."):
                # ディレクトリ指定なし（カレントディレクトリ）
                if not order_ext:
                    path = path.with_suffix(ext)
            else:
                raise ValueError("存在するフォルダを指定してください。")

        return str(path)

    def __isTSV(self, path: str | Path) -> bool:
        """TSVのパスを読み込んでTSVかどうかを判断する

        Args:
            path (str | Path): パス名

        Returns:
            bool
        """
        return "\t" in Path(path).read_text(encoding="utf-8").splitlines()[0]

    def __isSameContentLength_2dList(self, content_list: list[Any]) -> bool:
        """2次元Listの中身のListの個数が揃っているかのチェック

        ・List型のデータが全てList型として入っている場合は、それぞれの個数が合っているかの確認
        ・List型のデータが全てList型として入っていない場合で、List型が含まれる場合はエラーとする

        Args:
            content_list (list): チェックデータ

        Returns:
            bool
        """

        if not content_list:
            return True

        list_in_list_len = sum(1 for v in content_list if isinstance(v, list))

        if list_in_list_len == len(content_list):
            # 全要素がリストの場合：各行の長さが揃っているか確認
            item_len = len(content_list[0])
            for index, v in enumerate(content_list[1:], start=2):
                if item_len != len(v):
                    raise ValueError(
                        f"一致しないデータ数 1行目:{item_len}個,{index}行目:{len(v)}個"
                    )
        elif list_in_list_len > 0:
            raise ValueError("list型の中にList型とそれ以外を混在させることできません。")

        return True

    def r_txt(self, path: str | Path) -> str:
        """テキストファイルのパスから中身の文字列を返す

        Args:
            path (str | Path): パス名

        Returns:
            content (str): 文字列
        """
        return Path(path).read_text(encoding="utf-8")

    def r_csv(self, path: str | Path, read_encoding: str = "utf-8") -> list[Any]:
        """CSVのパスを読み込んでリストにして返す

        read_encoding -> utf-8,cp932

        Args:
            path (str | Path): パス名
            read_encoding (str): 文字コード

        Returns:
            list (list): リスト
        """
        with Path(path).open(mode="r", encoding=read_encoding, newline="") as f:
            return list(csv.reader(f))

    def r_tsv(self, path: str | Path) -> list[Any]:
        """TSVのパスを読み込んでリストにして返す

        Args:
            path (str | Path): パス名

        Returns:
            list (list): リスト
        """
        with Path(path).open(mode="r", encoding="utf-8", newline="") as f:
            return list(csv.reader(f, delimiter="\t"))

    def r_json(self, json_path: str | Path) -> dict[Any, Any]:
        """JSONのパスを読み込んで辞書型にして返す

        Args:
            json_path (str | Path): パス名

        Returns:
            dict (dict): 辞書型
        """
        return json.loads(Path(json_path).read_text(encoding="utf-8"))

    def r_pickle(self, pickle_path: str | Path):
        """Pickleファイルのパスを読み込んで辞書型またはリスト型にして返す

        Args:
            pickle_path (str | Path): パス名

        Returns:
            dict_or_list (dict or list): 辞書型またはリスト
        """
        with Path(pickle_path).open(mode="rb") as f:
            return pickle.load(f)

    def r_auto(self, path: str | Path):
        """データを読み込む関数

        引数に入れられたパスから自動でファイル形式を判断して読み込みを行ってデータを返す

        Args:
            path (str | Path): ファイルパス名[.txt .csv .tsv .json .pickle]

        Returns:
            any (any): データ[list dict]


        """
        p = Path(path)
        ext = p.suffix

        if ext in (".txt", ".csv", ".tsv"):
            if self.__isTSV(p):
                content_list = self.r_tsv(p)
            else:
                content_list = self.r_csv(p)

            # 全行が要素0か1の場合、1次元リストに平坦化する
            if content_list and isinstance(content_list[0], list):
                if all(len(v) <= 1 for v in content_list):
                    return [v[0] if v else "" for v in content_list]

            return content_list

        elif ext == ".json":
            return self.r_json(p)
        elif ext == ".pickle":
            return self.r_pickle(p)
        else:
            raise ValueError(f"自動で読込処理ができない値: {p.name}")

    def w_txt(self, txt: str, filename: str = "") -> None:
        """テキストファイルを書き出す"""
        ext = ".txt"

        if Path(filename).suffix == ".md":
            ext = ".md"

        Path(self.__getFileNameHelper(filename, ext=ext)).write_text(
            txt, encoding="utf-8"
        )

    def w_log(self, content: str, filename: str = "") -> None:
        """テキストをログ形式で書き出す"""
        if isinstance(content, (list, tuple)):
            content = ",".join(str(v) for v in content)
        else:
            content = str(content)

        if filename == "":
            # ファイル名省略時は日付ファイル名にして書き込みごとに新規tmpファイルが作成されるのを防ぐ
            filename = self.yyyymmdd

        with Path(self.__getFileNameHelper(filename, ext=".txt")).open(
            mode="a", encoding="utf-8"
        ) as f:
            f.write(f"{content}\n")

    def w_list(self, content_list: list[Any], filename: str = "") -> None:
        """改行区切りのリストを書き出す"""
        text = "".join(f"{v}\n" for v in content_list)
        Path(self.__getFileNameHelper(filename, ext=".txt")).write_text(
            text, encoding="utf-8"
        )

    def w_list_lf(self, content_list: list[Any], filename: str = "") -> None:
        """改行区切りのリストを書き出す(改行コード:LF)"""
        with Path(self.__getFileNameHelper(filename, ext=".txt")).open(
            mode="w", encoding="utf-8", newline="\n"
        ) as f:
            for v in content_list:
                f.write(f"{v}\n")

    def w_csv(
        self, content_list: list[Any], filename: str = "", write_encoding: str = "utf-8"
    ) -> None:
        """CSVを書き出す


        write_encoding -> utf-8,cp932
        """
        with Path(self.__getFileNameHelper(filename, ext=".csv")).open(
            mode="w", encoding=write_encoding, newline="\n"
        ) as f:
            csv.writer(f).writerows(content_list)

    def w_csv_lf(
        self, content_list: list[Any], filename: str = "", write_encoding: str = "utf-8"
    ) -> None:
        """CSVを書き出す(改行コード:LF)

        write_encoding -> utf-8,cp932
        """
        with Path(self.__getFileNameHelper(filename, ext=".csv")).open(
            mode="w", encoding=write_encoding, newline=""
        ) as f:
            csv.writer(f, lineterminator="\n").writerows(content_list)

    def w_tsv(self, content_list: list[Any], filename: str = "") -> None:
        """TSVを書き出す"""
        with Path(self.__getFileNameHelper(filename, ext=".tsv")).open(
            mode="w", encoding="utf-8", newline="\n"
        ) as f:
            csv.writer(f, delimiter="\t").writerows(content_list)

    def w_tsv_lf(self, content_list: list[Any], filename: str = "") -> None:
        """TSVを書き出す(改行コード:LF)"""
        with Path(self.__getFileNameHelper(filename, ext=".tsv")).open(
            mode="w", encoding="utf-8", newline=""
        ) as f:
            csv.writer(f, delimiter="\t", lineterminator="\n").writerows(content_list)

    def w_dict(self, dic: dict[Any, Any], filename: str = "") -> None:
        """辞書型を整形してテキストファイルで書き出す"""
        with Path(self.__getFileNameHelper(filename, ext=".txt")).open(
            mode="w", encoding="utf-8"
        ) as f:
            pprint(dic, stream=f)

    def w_json(
        self, dic_or_list: dict[Any, Any] | list[Any], filename: str = ""
    ) -> None:
        """辞書型またはリスト型をJSONファイルで書き出す"""
        text = json.dumps(dic_or_list, indent=2, ensure_ascii=False)
        Path(self.__getFileNameHelper(filename, ext=".json")).write_text(
            text, encoding="utf-8"
        )

    def w_pickle(self, dic: dict[Any, Any], filename: str = "") -> None:
        """辞書型またはリスト型をPickleファイルで書き出す"""
        with Path(self.__getFileNameHelper(filename, ext=".pickle")).open(
            mode="wb"
        ) as f:
            pickle.dump(dic, f)

    def w_auto(
        self,
        any_data: dict[Any, Any] | list[Any] | str | None,
        filename: str = "",
        isNullable: bool = False,
    ) -> None:
        """データを書き出す関数

        引数に入れられたデータ型から自動でファイル形式を判断して書き出しを行う。

        Args:
            any_data (any): データ[str,list,set,dict]
            filename (str): ファイル名やファイルパス名(オプション)
            isNullable (bool): Nullを許容するか Trueの時に何も書き出ししない


        """
        if isinstance(any_data, dict) or isinstance(any_data, list):
            if hasattr(any_data, "__len__") and len(any_data) == 0:
                if isNullable:
                    return
                else:
                    raise ValueError(
                        f"中身が空のため書き出し出来ません。 {type(any_data)} {any_data}"
                    )
        else:
            if isinstance(any_data, str):
                if any_data == "":
                    if isNullable:
                        return
                    else:
                        raise ValueError(
                            f"中身が空のため書き出し出来ません。 {type(any_data)} {any_data}"
                        )
            else:
                raise ValueError(
                    f"中身が空のため書き出し出来ません。 {type(any_data)} {any_data}"
                )

        if isinstance(any_data, set):
            any_data = sorted(any_data)

        if isinstance(any_data, list):
            if isinstance(any_data[0], list):
                self.w_tsv(any_data, filename)
            else:
                self.w_list(any_data, filename)
        elif isinstance(any_data, dict):
            self.w_json(any_data, filename)
        elif isinstance(any_data, str):  # type: ignore
            self.w_txt(any_data, filename)
        else:
            raise ValueError(f"書き出しが出来ませんでした。型:{type(any_data)}")

    def str_to_list(self, raw_str: str, isSideTrim: bool = True) -> list[Any]:
        """改行区切りの文字列をリストにして返す。

        改行区切りの文字列を空白を取り除いてリストにして返す。

        Args:
            raw_str (str): 対象の文字列
            isSideTrim (bool): 改行区切りで取得するときに両サイドの空白を除去するか

        Returns:
            list (list): リスト
        """

        lines = raw_str.split("\n")
        data = [v.strip() if isSideTrim else v for v in lines]
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
    def yyyymmdd(self) -> str:
        """YYYYMMDD形式の日付文字列を返す"""
        return datetime.datetime.now().strftime("%Y%m%d")

    @property
    def now(self) -> str:
        """RFC3339とISO8601に則ったOSのタイムゾーン付きでミリセカンドまでの時刻を返す"""
        return datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")


du = DataUtil()
