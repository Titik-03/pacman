from typing import List, Dict
import json


class Score:

    def __init__(self) -> List[Dict]:

        self.score: List[Dict] = []
    
    def load_score(self):
        try:
            with open("src/outputs/high_score.json", "r") as fp:
                self.score = json.load(fp)
            print(self.score)

        except Exception as e:
            print(e)
        return self.score

    def write_score(self, new_data: Dict) -> List[Dict]:
        existing_data: List = []
        try:
            with open("src/outputs/high_score.json", "r") as fp:
                existing_data = json.load(fp)
            
            existing_data.append(new_data)

            with open("src/outputs/high_score.json", "w") as fp:
                json.dump(existing_data, fp, indent=4)

        except Exception as e:
            print(e)
        
        return existing_data
