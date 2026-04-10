import os
import tempfile
import unittest
from parser import detect_format, parse_scan


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.nmap_sample = """Nmap scan report for 192.168.1.1
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2
80/tcp open  http    Apache 2.4.41
"""
        self.masscan_sample = (
            "Discovered open port 80/tcp on 10.0.0.1\n"
            "Discovered open port 22/tcp on 10.0.0.2\n"
        )

    def write_temp(self, content: str) -> str:
        handle = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        handle.write(content)
        handle.close()
        return handle.name

    def test_nmap_parsing(self) -> None:
        path = self.write_temp(self.nmap_sample)
        result = parse_scan(path, fmt="nmap")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ip"], "192.168.1.1")
        self.assertEqual(len(result[0]["ports"]), 2)
        self.assertEqual(result[0]["ports"][0]["port"], "22")
        os.unlink(path)

    def test_masscan_parsing(self) -> None:
        path = self.write_temp(self.masscan_sample)
        result = parse_scan(path, fmt="masscan")
        self.assertEqual(len(result), 2)
        os.unlink(path)

    def test_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            parse_scan("/nonexistent/path.txt")

    def test_auto_detect_nmap(self) -> None:
        path = self.write_temp(self.nmap_sample)
        self.assertEqual(detect_format(path), "nmap")
        os.unlink(path)


if __name__ == "__main__":
    unittest.main()
