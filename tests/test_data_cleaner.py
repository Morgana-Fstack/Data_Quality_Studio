import unittest

import pandas as pd

from data_cleaner import clean_dataframe, inspect_data, profile_data


class TestDataCleaner(unittest.TestCase):
    def test_cleaning_pipeline(self):
        source = pd.DataFrame({"Nome Empresa": [" Acme ", " Acme ", ""], "Plano!": ["Pro", "Pro", None]})
        result = clean_dataframe(source)
        self.assertEqual(result.columns.tolist(), ["nome_empresa", "plano"])
        self.assertEqual(len(result), 2)
        self.assertEqual(result.loc[0, "nome_empresa"], "Acme")
        self.assertTrue(pd.isna(result.loc[1, "nome_empresa"]))

    def test_profile(self):
        source = pd.DataFrame({"a": [1, 1, None], "b": ["x", "x", " "]})
        self.assertEqual(profile_data(source), {"rows": 3, "columns": 2, "missing": 2, "duplicates": 1})

    def test_inspection_explains_visible_problems(self):
        source = pd.DataFrame({" Nome ": [" Acme ", "Acme", ""], "E-mail": ["a@x.com", "a@x.com", None]})
        result = inspect_data(source)
        self.assertEqual(result["headers"], 2)
        self.assertEqual(result["whitespace"], 1)
        self.assertEqual(result["blank_strings"], 1)
        self.assertEqual(result["duplicates_after_trim"], 1)


if __name__ == "__main__":
    unittest.main()
