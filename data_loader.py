
import csv
from typing import List, Dict, Optional
from pathlib import Path


class VideoData:
   

    def __init__(self, row_data: Dict[str, str]):
        self.video_id = row_data.get('video_id', '').strip()
        self.url = row_data.get('url', '').strip()
        self.name = row_data.get('name', '').strip()
        self.instrument_type = row_data.get('instrument_type', '').strip()
        self.main_goals = [g.strip() for g in row_data.get('main_goals', '').split(',') if g.strip()]
        self.target_goal = row_data.get('target_goal', '').strip()
        self.function = row_data.get('function', '').strip()
        self.fatigue_related = row_data.get('fatigue_related', '').strip()
        self.prerequisites = [p.strip() for p in row_data.get('prerequisites', '').split(',') if p.strip()]
        self.level = self._parse_level(row_data.get('level', '').strip())
        self.cognitive_load = row_data.get('cognitive_load', '').strip().lower()
        self.physical_load = row_data.get('physical_load', '').strip().lower()

    def _parse_level(self, level_str: str) -> int:
      
        try:
            return int(level_str)
        except (ValueError, TypeError):
            return 0

    def to_dict(self) -> Dict:
        
        return {
            'video_id': self.video_id,
            'url': self.url,
            'name': self.name,
            'instrument_type': self.instrument_type,
            'main_goals': self.main_goals,
            'target_goal': self.target_goal,
            'function': self.function,
            'fatigue_related': self.fatigue_related,
            'prerequisites': self.prerequisites,
            'level': self.level,
            'cognitive_load': self.cognitive_load,
            'physical_load': self.physical_load
        }


class DataLoader:
    

    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.videos: List[VideoData] = []
        self._load_data()

    def _load_data(self):
        
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader, None)  # skip header

            for row in reader:
                if len(row) < 12:
                    continue

                video_data = {
                    'video_id': row[0].strip(),
                    'url': row[1].strip(),
                    'name': row[2].strip(),
                    'instrument_type': row[3].strip(),
                    'main_goals': row[4].strip(),
                    'target_goal': row[5].strip(),
                    'function': row[6].strip(),
                    'fatigue_related': row[7].strip(),
                    'level': row[8].strip(),
                    'cognitive_load': row[9].strip(),
                    'physical_load': row[10].strip(),
                    'prerequisites': row[11].strip()
                }

                video = VideoData(video_data)
                if video.video_id and video.url:
                    self.videos.append(video)

    def get_video_by_id(self, video_id: str) -> Optional[VideoData]:
        
        for video in self.videos:
            if video.video_id == str(video_id):
                return video
        return None

    def get_videos_by_ids(self, video_ids: List[int]) -> List[VideoData]:
        
        return [v for v in self.videos if int(v.video_id) in video_ids]

    def get_all_videos(self) -> List[VideoData]:
        
        return self.videos

    def filter_videos(
        self,
        instrument_type: Optional[str] = None,
        target_goal: Optional[str] = None,
        function: Optional[str] = None,
        max_level: Optional[int] = None,
        min_level: Optional[int] = None
    ) -> List[VideoData]:
    
        filtered = self.videos

        if instrument_type:
            filtered = [v for v in filtered if v.instrument_type.lower() == instrument_type.lower()]

        if target_goal:
            filtered = [v for v in filtered if v.target_goal.lower() == target_goal.lower()]

        if function:
            filtered = [v for v in filtered if function.lower() in v.function.lower()]

        if max_level is not None:
            filtered = [v for v in filtered if v.level <= max_level]

        if min_level is not None:
            filtered = [v for v in filtered if v.level >= min_level]

        return filtered
