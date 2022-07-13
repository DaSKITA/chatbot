import os
from typing import List


class TiltDefaultFiller:

    def __init__(self) -> None:
        pass

    def replace_values(self, tilt_dict: dict) -> dict:
        for key, value in tilt_dict.items():
            if value == [] or value is None:
                tilt_dict[key] = self._set_default_value()
            elif isinstance(value, list):
                tilt_dict[key] = self._process_list(value)
            elif isinstance(value, dict):
                tilt_dict[key] = self.replace_values(value)
        return tilt_dict

    def _set_default_value(self):
        return "Keine Angabe in der Policy."

    def _process_list(self, tilt_list: List) -> List:
        for idx, entry in enumerate(tilt_list):
            if isinstance(entry, dict):
                tilt_list[idx] = self.replace_values(entry)
            elif isinstance(entry, list):
                tilt_list[idx] = self._process_list(entry)
            else:
                tilt_list[idx] = self._set_default_value()
        return tilt_list


if __name__ == "__main__":
    import json
    tilt_default_filler = TiltDefaultFiller()
    tilt_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tests/test_tilt.json")
    with open(tilt_path) as f:
        tilt_dict = json.load(f)
    print(tilt_default_filler.replace_values(tilt_dict))
