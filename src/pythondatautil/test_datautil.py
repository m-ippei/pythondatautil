"""
datautil.py のテストコード

実行方法:
    pytest test_datautil.py -v
"""

import json
import pickle
import re

# import tempfile
from pathlib import Path

import pytest

from .datautil import DataUtil


@pytest.fixture
def du():
    return DataUtil()


@pytest.fixture
def tmp_dir(tmp_path, monkeypatch):
    """カレントディレクトリを一時ディレクトリに切り替えるフィクスチャ"""
    monkeypatch.chdir(tmp_path)
    return tmp_path


# ============================================================
# __getTmpName (間接テスト: w_txt でファイル名を省略した場合)
# ============================================================


class TestGetTmpName:
    def test_first_tmp_is_tmp1(self, du, tmp_dir):
        du.w_txt("hello", "")
        assert (tmp_dir / "tmp1.txt").exists()

    def test_increments_when_tmp_exists(self, du, tmp_dir):
        (tmp_dir / "tmp1.txt").write_text("x")
        du.w_txt("hello", "")
        assert (tmp_dir / "tmp2.txt").exists()

    def test_uses_max_plus_one(self, du, tmp_dir):
        (tmp_dir / "tmp3.txt").write_text("x")
        du.w_txt("hello", "")
        assert (tmp_dir / "tmp4.txt").exists()


# ============================================================
# __getFileNameHelper (間接テスト)
# ============================================================


class TestGetFileNameHelper:
    def test_empty_returns_tmp(self, du, tmp_dir):
        name = du._DataUtil__getFileNameHelper("")
        assert re.match(r"tmp\d+\.txt", name)

    def test_adds_ext_when_missing(self, du, tmp_dir):
        name = du._DataUtil__getFileNameHelper("output")
        assert name == "output.txt"

    def test_keeps_correct_ext(self, du, tmp_dir):
        name = du._DataUtil__getFileNameHelper("output.txt")
        assert name == "output.txt"

    def test_raises_on_wrong_ext(self, du, tmp_dir):
        with pytest.raises(ValueError):
            du._DataUtil__getFileNameHelper(str(tmp_dir / "output.csv"), ext=".txt")

    def test_raises_if_dir_path_given(self, du, tmp_dir):
        with pytest.raises(ValueError):
            du._DataUtil__getFileNameHelper(str(tmp_dir))

    def test_raises_on_nonexistent_parent(self, du, tmp_dir):
        with pytest.raises(ValueError):
            du._DataUtil__getFileNameHelper(str(tmp_dir / "no_such_dir" / "file.txt"))

    def test_raises_if_not_string(self, du, tmp_dir):
        with pytest.raises(ValueError):
            du._DataUtil__getFileNameHelper(123)

    def test_with_existing_parent_dir(self, du, tmp_dir):
        subdir = tmp_dir / "sub"
        subdir.mkdir()
        name = du._DataUtil__getFileNameHelper(str(subdir / "file"))
        assert name == str(subdir / "file.txt")


# ============================================================
# __isSameContentLength_2dList
# ============================================================


class TestIsSameContentLength2dList:
    def test_valid_2d_list(self, du):
        assert du._DataUtil__isSameContentLength_2dList([[1, 2], [3, 4]]) is True

    def test_empty_list(self, du):
        assert du._DataUtil__isSameContentLength_2dList([]) is True

    def test_flat_list_ok(self, du):
        assert du._DataUtil__isSameContentLength_2dList([1, 2, 3]) is True

    def test_mixed_raises(self, du):
        with pytest.raises(ValueError):
            du._DataUtil__isSameContentLength_2dList([[1, 2], 3])

    def test_unequal_rows_raises(self, du):
        with pytest.raises(ValueError):
            du._DataUtil__isSameContentLength_2dList([[1, 2], [3]])

    def test_not_list_raises(self, du):
        with pytest.raises(ValueError):
            du._DataUtil__isSameContentLength_2dList("abc")


# ============================================================
# r_txt / w_txt
# ============================================================


class TestTxt:
    def test_write_and_read(self, du, tmp_dir):
        path = tmp_dir / "test.txt"
        du.w_txt("hello world", str(path))
        assert du.r_txt(str(path)) == "hello world"

    def test_read_with_pathlib(self, du, tmp_dir):
        path = tmp_dir / "test.txt"
        path.write_text("pathlib", encoding="utf-8")
        assert du.r_txt(path) == "pathlib"

    def test_write_auto_tmp(self, du, tmp_dir):
        du.w_txt("auto")
        assert (tmp_dir / "tmp1.txt").read_text(encoding="utf-8") == "auto"


# ============================================================
# r_csv / w_csv
# ============================================================


class TestCsv:
    def test_write_and_read(self, du, tmp_dir):
        data = [["a", "b"], ["1", "2"]]
        path = str(tmp_dir / "test.csv")
        du.w_csv(data, path)
        assert du.r_csv(path) == data

    def test_write_and_read_lf(self, du, tmp_dir):
        data = [["x", "y"], ["3", "4"]]
        path = str(tmp_dir / "lf.csv")
        du.w_csv_lf(data, path)
        assert du.r_csv(path) == data

    def test_cp932_encoding(self, du, tmp_dir):
        data = [["名前", "値"], ["テスト", "123"]]
        path = str(tmp_dir / "sjis.csv")
        du.w_csv(data, path, write_encoding="cp932")
        assert du.r_csv(path, read_encoding="cp932") == data


# ============================================================
# r_tsv / w_tsv
# ============================================================


class TestTsv:
    def test_write_and_read(self, du, tmp_dir):
        data = [["a", "b"], ["1", "2"]]
        path = str(tmp_dir / "test.tsv")
        du.w_tsv(data, path)
        assert du.r_tsv(path) == data

    def test_write_and_read_lf(self, du, tmp_dir):
        data = [["x", "y"], ["3", "4"]]
        path = str(tmp_dir / "lf.tsv")
        du.w_tsv_lf(data, path)
        assert du.r_tsv(path) == data


# ============================================================
# r_json / w_json
# ============================================================


class TestJson:
    def test_dict(self, du, tmp_dir):
        data = {"key": "value", "num": 42}
        path = str(tmp_dir / "test.json")
        du.w_json(data, path)
        assert du.r_json(path) == data

    def test_list(self, du, tmp_dir):
        data = [1, 2, 3]
        path = str(tmp_dir / "test.json")
        du.w_json(data, path)
        assert du.r_json(path) == data

    def test_japanese(self, du, tmp_dir):
        data = {"名前": "テスト"}
        path = str(tmp_dir / "ja.json")
        du.w_json(data, path)
        text = Path(path).read_text(encoding="utf-8")
        assert "テスト" in text  # ensure_ascii=False が効いている
        assert du.r_json(path) == data


# ============================================================
# r_pickle / w_pickle
# ============================================================


class TestPickle:
    def test_dict(self, du, tmp_dir):
        data = {"a": 1}
        path = str(tmp_dir / "test.pickle")
        du.w_pickle(data, path)
        assert du.r_pickle(path) == data

    def test_list(self, du, tmp_dir):
        data = [1, "two", 3.0]
        path = str(tmp_dir / "test.pickle")
        du.w_pickle(data, path)
        assert du.r_pickle(path) == data


# ============================================================
# w_list / w_list_lf
# ============================================================


class TestWList:
    def test_w_list(self, du, tmp_dir):
        path = str(tmp_dir / "list.txt")
        du.w_list(["a", "b", "c"], path)
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        assert lines == ["a", "b", "c"]

    def test_w_list_lf(self, du, tmp_dir):
        path = str(tmp_dir / "list_lf.txt")
        du.w_list_lf(["x", "y"], path)
        content = Path(path).read_bytes()
        assert b"\r" not in content


# ============================================================
# w_log
# ============================================================


class TestWLog:
    def test_string_content(self, du, tmp_dir):
        path = str(tmp_dir / "log.txt")
        du.w_log("line1", path)
        du.w_log("line2", path)
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        assert lines == ["line1", "line2"]

    def test_list_content(self, du, tmp_dir):
        path = str(tmp_dir / "log.txt")
        du.w_log(["a", "b", "c"], path)
        assert Path(path).read_text(encoding="utf-8").strip() == "a,b,c"

    def test_int_content(self, du, tmp_dir):
        path = str(tmp_dir / "log.txt")
        du.w_log(42, path)
        assert Path(path).read_text(encoding="utf-8").strip() == "42"

    def test_empty_filename_uses_date(self, du, tmp_dir):
        du.w_log("hello", "")
        date_files = list(tmp_dir.glob("????????.txt"))
        assert len(date_files) == 1


# ============================================================
# w_dict
# ============================================================


class TestWDict:
    def test_w_dict(self, du, tmp_dir):
        path = str(tmp_dir / "dict.txt")
        du.w_dict({"a": 1, "b": [1, 2]}, path)
        content = Path(path).read_text(encoding="utf-8")
        assert "a" in content
        assert "b" in content


# ============================================================
# r_auto
# ============================================================


class TestRAuto:
    def test_csv(self, du, tmp_dir):
        data = [["a", "b"], ["1", "2"]]
        path = tmp_dir / "data.csv"
        path.write_text("a,b\n1,2\n", encoding="utf-8")
        assert du.r_auto(str(path)) == data

    def test_tsv(self, du, tmp_dir):
        path = tmp_dir / "data.tsv"
        path.write_text("a\tb\n1\t2\n", encoding="utf-8")
        assert du.r_auto(str(path)) == [["a", "b"], ["1", "2"]]

    def test_single_column_csv_flattened(self, du, tmp_dir):
        path = tmp_dir / "col.csv"
        path.write_text("a\nb\nc\n", encoding="utf-8")
        assert du.r_auto(str(path)) == ["a", "b", "c"]

    def test_json(self, du, tmp_dir):
        data = {"k": "v"}
        path = tmp_dir / "data.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        assert du.r_auto(str(path)) == data

    def test_pickle(self, du, tmp_dir):
        data = [1, 2, 3]
        path = tmp_dir / "data.pickle"
        path.write_bytes(pickle.dumps(data))
        assert du.r_auto(str(path)) == data

    def test_unsupported_ext_raises(self, du, tmp_dir):
        path = tmp_dir / "data.xyz"
        path.write_text("x")
        with pytest.raises(ValueError):
            du.r_auto(str(path))


# ============================================================
# w_auto
# ============================================================


class TestWAuto:
    def test_str(self, du, tmp_dir):
        path = str(tmp_dir / "out.txt")
        du.w_auto("hello", path)
        assert Path(path).read_text(encoding="utf-8") == "hello"

    def test_flat_list(self, du, tmp_dir):
        path = str(tmp_dir / "out.txt")
        du.w_auto(["a", "b"], path)
        assert Path(path).read_text(encoding="utf-8").splitlines() == ["a", "b"]

    def test_2d_list_writes_tsv(self, du, tmp_dir):
        path = str(tmp_dir / "out.tsv")
        du.w_auto([["a", "b"], ["1", "2"]], path)
        content = Path(path).read_text(encoding="utf-8")
        assert "\t" in content

    def test_dict_writes_json(self, du, tmp_dir):
        path = str(tmp_dir / "out.json")
        du.w_auto({"k": "v"}, path)
        assert json.loads(Path(path).read_text(encoding="utf-8")) == {"k": "v"}

    def test_set_sorted(self, du, tmp_dir):
        path = str(tmp_dir / "out.txt")
        du.w_auto({"c", "a", "b"}, path)
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        assert lines == ["a", "b", "c"]

    def test_empty_raises(self, du, tmp_dir):
        with pytest.raises(ValueError):
            du.w_auto([], str(tmp_dir / "out.txt"))

    def test_empty_nullable(self, du, tmp_dir):
        path = str(tmp_dir / "out.txt")
        du.w_auto([], path, isNullable=True)
        assert not Path(path).exists()

    def test_unsupported_type_raises(self, du, tmp_dir):
        with pytest.raises(ValueError):
            du.w_auto(123, str(tmp_dir / "out.txt"))


# ============================================================
# str_to_list
# ============================================================


class TestStrToList:
    def test_simple(self, du):
        result = du.str_to_list("a\nb\nc")
        assert result == ["a", "b", "c"]

    def test_strips_whitespace(self, du):
        result = du.str_to_list("  a  \n  b  ")
        assert result == ["a", "b"]

    def test_no_strip(self, du):
        result = du.str_to_list("  a  \n  b  ", isSideTrim=False)
        assert result == ["  a  ", "  b  "]

    def test_comma_separated(self, du):
        result = du.str_to_list("a,b\nc,d")
        assert result == [["a", "b"], ["c", "d"]]

    def test_tab_separated(self, du):
        result = du.str_to_list("a\tb\nc\td")
        assert result == [["a", "b"], ["c", "d"]]

    def test_comma_and_tab_raises(self, du):
        with pytest.raises(ValueError):
            du.str_to_list("a,b\tc")

    def test_non_string_raises(self, du):
        with pytest.raises(ValueError):
            du.str_to_list(123)

    def test_empty_lines_removed(self, du):
        result = du.str_to_list("a\n\nb\n\nc")
        assert result == ["a", "b", "c"]

    def test_uneven_comma_rows_raises(self, du):
        with pytest.raises(ValueError):
            du.str_to_list("a,b\nc")


# ============================================================
# yyyymmdd / now プロパティ
# ============================================================


class TestProperties:
    def test_yyyymmdd_format(self, du):
        result = du.yyyymmdd
        assert re.fullmatch(r"\d{8}", result)

    def test_now_is_iso8601(self, du):
        result = du.now
        # ISO8601 with timezone: 2024-01-01T12:34:56.789+09:00
        assert re.match(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{2}:\d{2}", result
        )
