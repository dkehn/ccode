#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import random
import unittest
import lru_cache


class Test_Decorators(unittest.TestCase):
    def test_decorator_lru_cache(self):
        class LRU_Test(object):
            """class"""
            def __init__(self):
                self.num = 0

            @lru_cache.lru_cache(maxsize=10, timeout=3)
            def test_method(self, num):
                """test_method_doc"""
                self.num += num
                return self.num

        @lru_cache.lru_cache(maxsize=10, timeout=3)
        def test_func(num):
            """test_func_doc"""
            return num

        @lru_cache.lru_cache(maxsize=10, timeout=3)
        def test_func_time(num):
            """test_func_time_doc"""
            return time.time()

        @lru_cache.lru_cache(maxsize=10, timeout=None)
        def test_func_args(*args, **kwargs):
            return random.randint(1, 10000000)

        # Init vars:
        c1 = LRU_Test()
        c2 = LRU_Test()
        m1 = c1.test_method
        m2 = c2.test_method
        f1 = test_func

        # Test basic caching functionality:
        self.assertEqual(m1(1), m1(1))
        self.assertEqual(c1.num, 1)     # c1.num now equals 1 - once cached, once real
        self.assertEqual(f1(1), f1(1))

        # Test caching is different between instances - once cached, once not cached:
        self.assertNotEqual(m1(2), m2(2))
        self.assertNotEqual(m1(2), m2(2))

        # Validate the cache_clear funcionality only on one instance:
        prev1 = m1(1)
        prev2 = m2(1)
        prev3 = f1(1)
        m1.cache_clear()
        self.assertNotEqual(m1(1), prev1)
        self.assertEqual(m2(1), prev2)
        self.assertEqual(f1(1), prev3)

        # Validate the docstring and the name are set correctly:
        self.assertEqual(m1.__doc__, "test_method_doc")
        self.assertEqual(f1.__doc__, "test_func_doc")
        self.assertEqual(m1.__name__, "test_method")
        self.assertEqual(f1.__name__, "test_func")

        # Test the limit of the cache, cache size is 10, fill 15 vars,
        # the first 5 will be overwritten for each and the other 5 are untouched. Test that:
        c1.num = 0
        c2.num = 10
        m1.cache_clear()
        m2.cache_clear()
        f1.cache_clear()
        temp_list = map(lambda i: (test_func_time(i), m1(i), m2(i)), range(15))

        for i in range(5, 10):
            self.assertEqual(temp_list[i], (test_func_time(i), m1(i), m2(i)))
        for i in range(0, 5):
            self.assertNotEqual(temp_list[i], (test_func_time(i), m1(i), m2(i)))
        # With the last run the next 5 vars were overwritten, now it should have
        # only 0..4 and 10..14:
        for i in range(5, 10):
            self.assertNotEqual(temp_list[i], (test_func_time(i), m1(i), m2(i)))

        # Test different vars don't collide:
        self.assertNotEqual(test_func_args(1), test_func_args('1'))
        self.assertNotEqual(test_func_args(1.0), test_func_args('1.0'))
        self.assertNotEqual(test_func_args(1.0), test_func_args(1))
        self.assertNotEqual(test_func_args(None), test_func_args('None'))
        self.assertEqual(test_func_args(test_func), test_func_args(test_func))
        self.assertEqual(test_func_args(LRU_Test), test_func_args(LRU_Test))
        self.assertEqual(test_func_args(object), test_func_args(object))
        self.assertNotEqual(test_func_args(1, num=1), test_func_args(1, num='1'))
        # Test the sorting of kwargs:
        self.assertEqual(test_func_args(1, aaa=1, bbb=2), test_func_args(1, bbb=2, aaa=1))
        self.assertNotEqual(test_func_args(1, aaa='1', bbb=2), test_func_args(1, bbb=2, aaa=1))

        # Sanity validation of values
        c1.num = 0
        c2.num = 10
        m1.cache_clear()
        m2.cache_clear()
        f1.cache_clear()
        self.assertEqual((f1(0), m1(0), m2(0)), (0, 0, 10))
        self.assertEqual((f1(0), m1(0), m2(0)), (0, 0, 10))
        self.assertEqual((f1(1), m1(1), m2(1)), (1, 1, 11))
        self.assertEqual((f1(2), m1(2), m2(2)), (2, 3, 13))
        self.assertEqual((f1(2), m1(2), m2(2)), (2, 3, 13))
        self.assertEqual((f1(3), m1(3), m2(3)), (3, 6, 16))
        self.assertEqual((f1(3), m1(3), m2(3)), (3, 6, 16))
        self.assertEqual((f1(4), m1(4), m2(4)), (4, 10, 20))
        self.assertEqual((f1(4), m1(4), m2(4)), (4, 10, 20))

        # Test timeout - sleep, it should refresh cache, and then check it was cleared:
        prev_time = test_func_time(0)
        self.assertEqual(test_func_time(0), prev_time)
        self.assertEqual(m1(4), 10)
        self.assertEqual(m2(4), 20)
        time.sleep(3.5)
        self.assertNotEqual(test_func_time(0), prev_time)
        self.assertNotEqual(m1(4), 10)
        self.assertNotEqual(m2(4), 20)


if __name__ == '__main__':
    unittest.main()
