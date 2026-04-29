from typing import List, Dict, Optional, Tuple
from data_loader import VideoData, DataLoader


class RecommendationEngine:
        
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        
        # Weight configuration for scoring
        self.weights = {
            'target_goal_match': 0.30,      # Match with user's target goal
            'main_goals_match': 0.20,       # Match with user's main goals
            'level_appropriateness': 0.15,  # How well level matches user level
            'prerequisites_met': 0.15,       # User has prerequisites
            'function_match': 0.10,         # Match with desired function (warm up, core, etc.)
            'fatigue_recovery': 0.05,       # Recovery after heavy video
            'cognitive_load': 0.03,         # Appropriate cognitive load
            'physical_load': 0.02           # Appropriate physical load
        }
    
    def calculate_score(self, video: VideoData, user_inputs: Dict) -> float:
        
        score = 0.0
        
        # 1. Target goal match (highest weight)
        if user_inputs.get('target_goal'):
            if video.target_goal.lower() == user_inputs['target_goal'].lower():
                score += self.weights['target_goal_match']
            elif user_inputs['target_goal'].lower() in video.target_goal.lower():
                score += self.weights['target_goal_match'] * 0.7
        
        # 2. Main goals match
        if user_inputs.get('main_goals'):
            user_goals = [g.strip().lower() for g in user_inputs['main_goals'].split(',')]
            video_goals = [g.lower() for g in video.main_goals]
            matches = sum(1 for ug in user_goals if any(ug in vg or vg in ug for vg in video_goals))
            if matches > 0:
                score += self.weights['main_goals_match'] * (matches / max(len(user_goals), len(video_goals)))
        
        # 3. Level appropriateness
        user_level = user_inputs.get('user_level', 5)
        if video.level > 0:
            level_diff = abs(video.level - user_level)
            if level_diff == 0:
                score += self.weights['level_appropriateness']
            elif level_diff == 1:
                score += self.weights['level_appropriateness'] * 0.8
            elif level_diff == 2:
                score += self.weights['level_appropriateness'] * 0.5
            elif level_diff <= 3:
                score += self.weights['level_appropriateness'] * 0.2
        
        # 4. Prerequisites met
        if video.prerequisites:
            user_skills = [s.strip().lower() for s in user_inputs.get('user_skills', '').split(',')]
            if user_skills:
                prereq_met = all(
                    any(pr.lower() in skill or skill in pr.lower() 
                        for skill in user_skills)
                    for pr in video.prerequisites
                )
                if prereq_met:
                    score += self.weights['prerequisites_met']
                else:
                    # Partial match
                    met_count = sum(
                        1 for pr in video.prerequisites
                        if any(pr.lower() in skill or skill in pr.lower() for skill in user_skills)
                    )
                    if met_count > 0:
                        score += self.weights['prerequisites_met'] * (met_count / len(video.prerequisites))
        else:
            # No prerequisites means accessible to all
            score += self.weights['prerequisites_met'] * 0.5
        
        # 5. Function match
        if user_inputs.get('function'):
            if user_inputs['function'].lower() in video.function.lower():
                score += self.weights['function_match']
        
        # 6. Fatigue recovery (if user just did a heavy video)
        if user_inputs.get('previous_video_heavy', False):
            if video.fatigue_related and video.fatigue_related.lower() != 'rest':
                if video.physical_load in ['basso', 'medio']:
                    score += self.weights['fatigue_recovery']
        
        # 7. Cognitive load appropriateness
        desired_cognitive = user_inputs.get('cognitive_load_preference', '').lower()
        if desired_cognitive:
            if video.cognitive_load == desired_cognitive:
                score += self.weights['cognitive_load']
            elif desired_cognitive == 'medio' and video.cognitive_load in ['basso', 'alto']:
                score += self.weights['cognitive_load'] * 0.5
        
        # 8. Physical load appropriateness
        desired_physical = user_inputs.get('physical_load_preference', '').lower()
        if desired_physical:
            if video.physical_load == desired_physical:
                score += self.weights['physical_load']
            elif desired_physical == 'medio' and video.physical_load in ['basso', 'alto']:
                score += self.weights['physical_load'] * 0.5
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_recommendations(self, 
                           user_inputs: Dict,
                           max_results: int = 10,
                           filter_videos: Optional[List[int]] = None) -> List[Tuple[VideoData, float]]:
        
        # Get candidate videos
        if filter_videos:
            candidates = self.data_loader.get_videos_by_ids(filter_videos)
        else:
            candidates = self.data_loader.get_all_videos()
        
        # Apply additional filters if specified
        if user_inputs.get('instrument_type'):
            candidates = [v for v in candidates 
                        if v.instrument_type.lower() == user_inputs['instrument_type'].lower()]
        
        if user_inputs.get('max_level'):
            candidates = [v for v in candidates if v.level <= user_inputs['max_level']]
        
        if user_inputs.get('min_level'):
            candidates = [v for v in candidates if v.level >= user_inputs['min_level']]
        
        # Score all candidates
        scored_videos = []
        for video in candidates:
            score = self.calculate_score(video, user_inputs)
            scored_videos.append((video, score))
        
        # Sort by score descending
        scored_videos.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return scored_videos[:max_results]
    
    def get_recommendations_with_explanation(self,
                                            user_inputs: Dict,
                                            max_results: int = 10,
                                            filter_videos: Optional[List[int]] = None) -> List[Dict]:
        
        recommendations = self.get_recommendations(user_inputs, max_results, filter_videos)
        
        result = []
        for video, score in recommendations:
            explanation = self._generate_explanation(video, score, user_inputs)
            result.append({
                'video': video.to_dict(),
                'score': round(score, 3),
                'explanation': explanation
            })
        
        return result
    
    def _generate_explanation(self, video: VideoData, score: float, user_inputs: Dict) -> str:
        reasons = []
        
        if user_inputs.get('target_goal') and video.target_goal.lower() == user_inputs['target_goal'].lower():
            reasons.append(f"Matches your target goal: {video.target_goal}")
        
        if user_inputs.get('main_goals'):
            user_goals = [g.strip().lower() for g in user_inputs['main_goals'].split(',')]
            matching_goals = [g for g in user_goals if any(g in vg.lower() or vg.lower() in g for vg in video.main_goals)]
            if matching_goals:
                reasons.append(f"Addresses your goals: {', '.join(matching_goals)}")
        
        if user_inputs.get('user_level'):
            level_diff = abs(video.level - user_inputs['user_level'])
            if level_diff == 0:
                reasons.append(f"Perfect level match (Level {video.level})")
            elif level_diff <= 2:
                reasons.append(f"Appropriate level (Level {video.level})")
        
        if video.prerequisites:
            user_skills = [s.strip().lower() for s in user_inputs.get('user_skills', '').split(',')]
            if user_skills and all(any(pr.lower() in skill or skill in pr.lower() for skill in user_skills) for pr in video.prerequisites):
                reasons.append("You have the required prerequisites")
        
        if user_inputs.get('function') and user_inputs['function'].lower() in video.function.lower():
            reasons.append(f"Suitable for {video.function}")
        
        if not reasons:
            reasons.append("General recommendation based on your profile")
        
        return "; ".join(reasons)
