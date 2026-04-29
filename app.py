from flask import Flask, render_template, request, jsonify
from data_loader import DataLoader
from recommendation_engine import RecommendationEngine

app = Flask(__name__)

# Load data and initialize recommender
CSV_PATH = "Video Youtube algorythm.csv"
data_loader = DataLoader(str(CSV_PATH))
recommendation_engine = RecommendationEngine(data_loader)

# Default video pool used for initial recommendations
INITIAL_VIDEO_ROWS = [
    70, 71, 64, 89, 91, 80, 81, 74, 73, 13,
    82, 86, 48, 16, 51, 49, 44, 42, 20, 7
]


@app.route('/')
def index():
    
    videos = data_loader.get_all_videos()

    instrument_types = sorted({v.instrument_type for v in videos if v.instrument_type})
    target_goals = sorted({v.target_goal for v in videos if v.target_goal})
    functions = sorted({v.function for v in videos if v.function})

    return render_template(
        'index.html',
        instrument_types=instrument_types,
        target_goals=target_goals,
        functions=functions,
        initial_video_count=len(INITIAL_VIDEO_ROWS)
    )


@app.route('/api/recommend', methods=['POST'])
def recommend():
   
    try:
        data = request.get_json()

        user_inputs = {
            'target_goal': data.get('target_goal', ''),
            'main_goals': data.get('main_goals', ''),
            'user_level': int(data.get('user_level', 5)) if data.get('user_level') else 5,
            'user_skills': data.get('user_skills', ''),
            'function': data.get('function', ''),
            'cognitive_load_preference': data.get('cognitive_load', ''),
            'physical_load_preference': data.get('physical_load', ''),
            'instrument_type': data.get('instrument_type', ''),
            'max_level': int(data.get('max_level')) if data.get('max_level') else None,
            'min_level': int(data.get('min_level')) if data.get('min_level') else None,
            'previous_video_heavy': data.get('previous_video_heavy', False)
        }

        filter_videos = INITIAL_VIDEO_ROWS if data.get('use_initial_set', True) else None
        max_results = int(data.get('max_results', 10))

        recommendations = recommendation_engine.get_recommendations_with_explanation(
            user_inputs,
            max_results=max_results,
            filter_videos=filter_videos
        )

        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Fetch videos with optional filters."""
    try:
        videos = data_loader.filter_videos(
            instrument_type=request.args.get('instrument_type'),
            target_goal=request.args.get('target_goal'),
            function=request.args.get('function'),
            max_level=request.args.get('max_level', type=int),
            min_level=request.args.get('min_level', type=int)
        )

        return jsonify({
            'success': True,
            'videos': [v.to_dict() for v in videos],
            'count': len(videos)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Dataset overview and distribution stats."""
    videos = data_loader.get_all_videos()

    stats = {
        'total_videos': len(videos),
        'instrument_types': {},
        'target_goals': {},
        'functions': {},
        'level_distribution': {},
        'initial_set_count': len(INITIAL_VIDEO_ROWS)
    }

    for v in videos:
        stats['instrument_types'][v.instrument_type] = stats['instrument_types'].get(v.instrument_type, 0) + 1
        stats['target_goals'][v.target_goal] = stats['target_goals'].get(v.target_goal, 0) + 1
        stats['functions'][v.function] = stats['functions'].get(v.function, 0) + 1
        stats['level_distribution'][v.level] = stats['level_distribution'].get(v.level, 0) + 1

    return jsonify({'success': True, 'stats': stats})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
