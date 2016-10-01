import unittest
import common.util as util


class moduletest_get_edit_dinstace(unittest.TestCase):
    # Replace
    def test_get_edit_dinstace_1(self):
        self.assertEqual(util.get_edit_distance("하하", "하허"), 1)

    # Replace
    def test_get_edit_dinstace_2(self):
        self.assertEqual(util.get_edit_distance("한국", "한궁"), 1)

    # Delete
    def test_get_edit_dinstace_3(self):
        self.assertEqual(util.get_edit_distance("한국", "한구"), 1)

    # Add
    def test_get_edit_dinstace_4(self):
        self.assertEqual(util.get_edit_distance("배포", "배퐁"), 1)

    # Long Sentence
    def test_get_edit_dinstace_5(self):
        self.assertEqual(util.get_edit_distance("1. 제대로 놀아보자 Yo!", "1. 제대로 골자보자 YO!"), 3)

    # 한글 분리
    def test_split_character_1(self):
        self.assertEqual(util.split_character("한글"), "ㅎㅏㄴㄱㅡㄹ")

    # 영어 분리
    def test_split_character_2(self):
        self.assertEqual(util.split_character("abcd"), "abcd")

    # 영어+한글 분리
    def test_split_character_3(self):
        self.assertEqual(util.split_character("abcd함"), "abcdㅎㅏㅁ")

    # 영어+한글+숫자 분리
    def test_split_character_4(self):
        self.assertEqual(util.split_character("abcd함 123"), "abcdㅎㅏㅁ 123")

    #
    def test_get_accuracy_1(self):
        self.assertEqual(util.get_accuracy("ㅅㅓㅇㅜㄹ", 1), 80)

    #
    def test_get_speed_1(self):
        self.assertEqual(util.get_speed("ㅅㅓㅇㅜㄹ!", 1000), 360)

        
"""
class ModuleTest_2(unittest.TestCase):
    def setUp(self):
        self.bag = [True, True]
    def tearDown(self):
        del self.bag
    def test_true(self):
        for element in self.bag:
            self.assertTrue(element)
class ModuleTest_3(unittest.TestCase):
    def test_substract_1(self):
        self.assertEqual(substract(4, 2), 2)
class ModuleTest_4(unittest.TestCase):
    def setUp(self):
        self.multiplier = multiplier.Multiplier()
    def test_multiplier_multiply_1(self):
        self.assertEqual(self.multiplier.multiply(2, 2), 4)
"""


def makeSuite(testcase, tests):
    return unittest.TestSuite(map(testcase, tests))


suite_1 = makeSuite(moduletest_get_edit_dinstace,
                    ['test_get_edit_dinstace_1', 'test_get_edit_dinstace_2',
                     'test_get_edit_dinstace_3', 'test_get_edit_dinstace_4',
                     'test_get_edit_dinstace_5',
                     'test_split_character_1', 'test_split_character_2',
                     'test_split_character_3', 'test_split_character_4',
                     'test_get_accuracy_1', 'test_get_speed_1'])


def run_unit_test():
    allsuites = unittest.TestSuite([suite_1])
    unittest.TextTestRunner(verbosity=2).run(allsuites)