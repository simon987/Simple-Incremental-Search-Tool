import os
from unittest import TestCase


from parsing import GenericFileParser, Md5CheckSumCalculator, Sha1CheckSumCalculator, Sha256CheckSumCalculator, ExtensionMimeGuesser


class GenericFileParserTest(TestCase):

    def setUp(self):
        if os.path.exists("test_parse.txt"):
            os.remove("test_parse.txt")

        test_file = open("test_parse.txt", "w")
        test_file.write("12345678")
        test_file.close()
        os.utime("test_parse.txt", (1330123456, 1330654321))

        self.parser = GenericFileParser([Md5CheckSumCalculator()])

    def tearDown(self):
        os.remove("test_parse.txt")

    def test_parse_size(self):
        result = self.parser.parse("test_parse.txt")

        self.assertEqual(result["size"], 8)

    def test_parse_name(self):
        result = self.parser.parse("test_parse.txt")

        self.assertEqual(result["name"], "test_parse")

    def test_parse_ext(self):
        result = self.parser.parse("test_parse.txt")

        self.assertEqual(result["extension"], "txt")

    def test_parse_md5(self):
        result = self.parser.parse("test_parse.txt")

        self.assertEqual(result["md5"], "25D55AD283AA400AF464C76D713C07AD")

    def test_mtime(self):

        result = self.parser.parse("test_parse.txt")

        self.assertEqual(result["mtime"], 1330654321)


class Md5CheckSumCalculatorTest(TestCase):

    def setUp(self):
        if os.path.exists("test_md5_1"):
            os.remove("test_md5_1")

        test_file = open("test_md5_1", "w")
        test_file.write("789456123")
        test_file.close()

        if os.path.exists("test_md5_2"):
            os.remove("test_md5_2")

        test_file = open("test_md5_2", "w")
        test_file.write("cj3w97n7RY378WRXEN68W7RExnw6nr8276b473824")
        test_file.close()

        self.calculator = Md5CheckSumCalculator()

    def tearDown(self):
        os.remove("test_md5_1")
        os.remove("test_md5_2")

    def test_md5_checksum(self):

        result = self.calculator.checksum("test_md5_1")
        self.assertEqual(result, "9FAB6755CD2E8817D3E73B0978CA54A6")

        result = self.calculator.checksum("test_md5_2")
        self.assertEqual(result, "39A1AADE23E33A7F37C11C7FF9CDC9EC")


class Sha1CheckSumCalculatorTest(TestCase):

    def setUp(self):
        if os.path.exists("test_sha1_1"):
            os.remove("test_sha1_1")

        test_file = open("test_sha1_1", "w")
        test_file.write("sxjkneycbu")
        test_file.close()

        if os.path.exists("test_sha1_2"):
            os.remove("test_sha1_2")

        test_file = open("test_sha1_2", "w")
        test_file.write("xoimoqxy38e")
        test_file.close()

        self.calculator = Sha1CheckSumCalculator()

    def tearDown(self):
        os.remove("test_sha1_1")
        os.remove("test_sha1_2")

    def test_md5_checksum(self):

        result = self.calculator.checksum("test_sha1_1")
        self.assertEqual(result, "A80315387730DB5743061F397EB66DE0DDAE19E5")

        result = self.calculator.checksum("test_sha1_2")
        self.assertEqual(result, "E7B5A2B6F6838E766A0BC7E558F640726D70A8D6")


class Sha256CheckSumCalculatorTest(TestCase):

    def setUp(self):
        if os.path.exists("test_sha256_1"):
            os.remove("test_sha256_1")

        test_file = open("test_sha256_1", "w")
        test_file.write("eaur5t84nc7i")
        test_file.close()

        if os.path.exists("test_sha256_2"):
            os.remove("test_sha256_2")

        test_file = open("test_sha256_2", "w")
        test_file.write("xkwerci47ixryw7r6wxadwd")
        test_file.close()

        self.calculator = Sha256CheckSumCalculator()

    def tearDown(self):
        os.remove("test_sha256_1")
        os.remove("test_sha256_2")

    def test_md5_checksum(self):

        result = self.calculator.checksum("test_sha256_1")
        self.assertEqual(result, "DA7606DC763306B700685A71E2E72A2D95F1291209E5DA344B82DA2508FC27C5")

        result = self.calculator.checksum("test_sha256_2")
        self.assertEqual(result, "C39C7E0E7D84C9692F3C9C22E1EA0327DEBF1BF531B5738EEA8E79FE27EBC570")



