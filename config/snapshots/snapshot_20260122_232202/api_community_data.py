"""
社區數據 API
提供五常社區分析數據的 API 接口
"""

from flask import Blueprint, jsonify
from community_data_integration import community_data
from ai_knowledge_base import AIKnowledgeBase
import os
import json

community_api = Blueprint('community', __name__)
kb = AIKnowledgeBase()

@community_api.route('/api/community/demographics')
def get_demographics():
    """獲取人口結構數據"""
    try:
        data = community_data.get_demographics()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@community_api.route('/api/community/commercial')
def get_commercial():
    """獲取商業生態數據"""
    try:
        data = community_data.get_commercial_ecosystem()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@community_api.route('/api/community/transportation')
def get_transportation():
    """獲取交通物流數據"""
    try:
        data = community_data.get_transportation()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@community_api.route('/api/community/happiness-coin')
def get_happiness_coin():
    """獲取幸福幣配置"""
    try:
        data = community_data.get_happiness_coin_config()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@community_api.route('/api/community/optimization')
def get_optimization():
    """獲取系統優化建議"""
    try:
        data = community_data.get_system_optimization()
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@community_api.route('/api/community/location')
def get_location():
    """獲取地理邊界和街道"""
    try:
        bounds = community_data.get_location_bounds()
        streets = community_data.get_main_streets()
        return jsonify({
            'success': True,
            'bounds': bounds,
            'streets': streets
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@community_api.route('/api/community/insights')
def get_insights():
    """獲取關鍵洞察"""
    try:
        insights = community_data.get_key_insights()
        return jsonify({'success': True, 'insights': insights})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@community_api.route('/api/community/summary')
def get_summary():
    """獲取社區數據摘要"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'name': '五常生活圈',
                'location': '新北市三重區',
                'villages': ['五常里', '五順里', '仁忠里'],
                'population': '9,000-10,000人',
                'elderly_percentage': 19.3,
                'motorcycles': '4,200-5,800輛',
                'main_streets': len(community_data.get_main_streets()),
                'key_insights': len(community_data.get_key_insights())
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@community_api.route('/api/community/knowledge-base')
def get_community_knowledge_base():
    """獲取五常社區知識庫（原始 JSON）"""
    try:
        kb_path = kb.knowledge_base_path
        if not os.path.exists(kb_path):
            return jsonify({'success': False, 'error': 'knowledge base file not found'}), 404
        with open(kb_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@community_api.route('/api/community/knowledge/index')
def get_community_knowledge_index():
    """獲取知識庫索引（不含全量 inverted_index 的超大 payload）"""
    try:
        if not kb.index_data:
            kb.load_index()
        if not kb.index_data:
            return jsonify({'success': False, 'error': 'index not found'}), 404

        safe = dict(kb.index_data)
        # Avoid sending the full inverted_index unless needed
        if 'inverted_index' in safe:
            safe['inverted_index'] = {'_omitted': True, 'terms': len(kb.index_data.get('inverted_index', {}))}
        return jsonify({'success': True, 'data': safe})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@community_api.route('/api/community/knowledge/search')
def search_community_knowledge():
    """
    知識庫快速檢索（索引優先，無索引則回退遞歸搜索）

    Query params:
      - q: string (required)
      - limit: int (optional, default 20)
    """
    try:
        from flask import request
        q = request.args.get('q', '').strip()
        limit_raw = request.args.get('limit', '').strip()
        limit = 20
        if limit_raw.isdigit():
            limit = max(1, min(100, int(limit_raw)))

        result = kb.query_index(q, limit=limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
