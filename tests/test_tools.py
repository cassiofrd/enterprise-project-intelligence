import unittest

from src.project_intelligence.tools import (
    calculate_project_kpis,
    get_project_status,
    list_project_ids,
)


class TestTools(unittest.TestCase):
    def test_list_ids(self):
        self.assertEqual(list_project_ids(), ["P001", "P002", "P003"])

    def test_status(self):
        result = get_project_status("p001")
        self.assertEqual(result["project"]["name"], "Modernização do ERP")
        self.assertEqual(result["currency"], "BRL")

    def test_unknown_project(self):
        with self.assertRaises(ValueError):
            get_project_status("P999")

    def test_kpis_p001(self):
        result = calculate_project_kpis("P001")
        self.assertEqual(result["kpis"]["SPI"], 0.88)
        self.assertEqual(result["kpis"]["CPI"], 0.88)
        self.assertEqual(result["kpis"]["SV"], -60000)
        self.assertEqual(result["kpis"]["CV"], -60000)
        self.assertAlmostEqual(result["kpis"]["EAC"], 1136363.64, places=2)

    def test_kpis_p002(self):
        result = calculate_project_kpis("P002")
        self.assertEqual(result["kpis"]["SPI"], 1.05)
        self.assertAlmostEqual(result["kpis"]["CPI"], 1.0667, places=4)

    def test_no_mutation_of_source(self):
        status = get_project_status("P001")
        status["project"]["bac"] = -1
        self.assertEqual(get_project_status("P001")["project"]["bac"], 1000000)


if __name__ == "__main__":
    unittest.main()
