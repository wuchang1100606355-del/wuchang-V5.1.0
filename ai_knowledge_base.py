"""
AI 知識庫管理系統
用於加載、學習和記憶社區分析數據
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

class AIKnowledgeBase:
    """AI 知識庫管理器 - 用於學習和記憶社區數據"""
    
    def __init__(self, knowledge_base_path='wuchang_community_knowledge_base.json'):
        """
        初始化知識庫
        
        Args:
            knowledge_base_path: 知識庫 JSON 文件路徑
        """
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_data = {}
        self.learning_history = []
        self.memory_cache = {}
        self.index_path = 'wuchang_community_knowledge_index.json'
        self.index_data: Dict[str, Any] = {}
        self.load_knowledge_base()
        self.load_index()
    
    def load_knowledge_base(self):
        """加載知識庫數據"""
        try:
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    self.knowledge_data = json.load(f)
                # Avoid unicode output issues on some Windows consoles
                print(f"[OK] knowledge base loaded: {self.knowledge_base_path}")
                return True
            else:
                print(f"[WARN] knowledge base file not found: {self.knowledge_base_path}")
                return False
        except Exception as e:
            print(f"[ERROR] failed to load knowledge base: {e}")
            return False

    def load_index(self) -> bool:
        """加載（可選）索引檔，用於更快的檢索。"""
        try:
            if os.path.exists(self.index_path):
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    self.index_data = json.load(f)
                print(f"[OK] knowledge index loaded: {self.index_path}")
                return True
            self.index_data = {}
            return False
        except Exception as e:
            print(f"[WARN] failed to load knowledge index: {e}")
            self.index_data = {}
            return False
    
    def learn_and_memorize(self, topic: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        學習並記憶數據
        
        Args:
            topic: 主題/類別
            data: 要學習的數據
            
        Returns:
            dict: 學習結果
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # 記錄學習歷史
            learning_record = {
                'topic': topic,
                'timestamp': timestamp,
                'data_summary': self._summarize_data(data),
                'data_size': len(str(data))
            }
            self.learning_history.append(learning_record)
            
            # 存儲到記憶緩存
            if topic not in self.memory_cache:
                self.memory_cache[topic] = []
            
            self.memory_cache[topic].append({
                'data': data,
                'learned_at': timestamp,
                'access_count': 0
            })
            
            # 保持最近 1000 條記憶
            if len(self.memory_cache[topic]) > 1000:
                self.memory_cache[topic] = self.memory_cache[topic][-1000:]
            
            return {
                'success': True,
                'message': f'已學習並記憶主題: {topic}',
                'timestamp': timestamp,
                'topics_learned': list(self.memory_cache.keys())
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def query_knowledge(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        查詢知識庫
        
        Args:
            query: 查詢關鍵詞或問題
            category: 可選的類別限制（如 'demographics', 'housing', 'commercial' 等）
            
        Returns:
            dict: 查詢結果
        """
        try:
            results = []
            query_lower = query.lower()
            
            # 如果指定了類別，只在該類別中搜索
            search_data = {}
            if category and category in self.knowledge_data:
                search_data[category] = self.knowledge_data[category]
            else:
                search_data = self.knowledge_data
            
            # 遞歸搜索匹配的數據
            matches = self._search_recursive(search_data, query_lower)
            
            # 更新訪問計數
            for match in matches:
                if 'topic' in match and match['topic'] in self.memory_cache:
                    for memory in self.memory_cache[match['topic']]:
                        memory['access_count'] += 1
            
            return {
                'success': True,
                'query': query,
                'category': category,
                'matches_found': len(matches),
                'results': matches[:20],  # 限制返回前 20 個結果
                'total_knowledge_topics': len(self.knowledge_data)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def query_index(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        使用索引檔進行快速檢索（若索引不存在則回退到遞歸搜索）。

        Returns:
            dict: 檢索結果（items 為索引條目，包含 path/snippet/keywords 等）
        """
        try:
            q = (query or '').strip()
            if not q:
                return {'success': False, 'error': 'query is required'}

            # If no index loaded, fallback
            if not self.index_data or 'items' not in self.index_data:
                fallback = self.query_knowledge(q)
                return {
                    'success': True,
                    'query': q,
                    'mode': 'fallback_recursive',
                    'matches_found': fallback.get('matches_found', 0),
                    'items': fallback.get('results', [])[:limit],
                }

            items = self.index_data.get('items', [])
            inv = self.index_data.get('inverted_index', {})
            tokenized = self._tokenize(q)
            candidate_ids = set()
            for t in tokenized:
                for item_id in inv.get(t, []):
                    candidate_ids.add(item_id)

            # If no token matches, do substring scan over snippets (small KB)
            if not candidate_ids:
                q_lower = q.lower()
                scored = []
                for it in items:
                    snippet = str(it.get('snippet', ''))
                    title = str(it.get('title', ''))
                    hay = (title + ' ' + snippet).lower()
                    if q_lower in hay:
                        scored.append((3, it))
                scored.sort(key=lambda x: x[0], reverse=True)
                out = [it for _, it in scored[:limit]]
                return {
                    'success': True,
                    'query': q,
                    'mode': 'index_substring_scan',
                    'matches_found': len(out),
                    'items': out
                }

            # Score candidates by token overlap + substring match
            scored = []
            q_lower = q.lower()
            by_id = {it.get('id'): it for it in items}
            for cid in candidate_ids:
                it = by_id.get(cid)
                if not it:
                    continue
                kw = set(it.get('keywords', []))
                base = len(kw.intersection(set(tokenized)))
                text = (str(it.get('title', '')) + ' ' + str(it.get('snippet', ''))).lower()
                if q_lower in text:
                    base += 2
                scored.append((base, it))

            scored.sort(key=lambda x: x[0], reverse=True)
            out = [it for _, it in scored[:limit]]
            return {
                'success': True,
                'query': q,
                'mode': 'index',
                'matches_found': len(out),
                'items': out
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _tokenize(self, text: str) -> List[str]:
        """
        混合中英數 tokenization：
        - 英數：依單字切分
        - 中文：抓連續中文片段（2~12 字）作為 token，並補 2~4 字 n-grams 以利查詢（例如「老化 指數」可命中「老化指數高達...」）
        """
        s = (text or '').strip().lower()
        if not s:
            return []
        tokens: List[str] = []
        # English/number tokens
        tokens.extend([t for t in re.split(r'[^a-z0-9_]+', s) if len(t) >= 2])
        # Chinese segments
        for seg in re.findall(r'[\u4e00-\u9fff]{2,12}', text):
            tokens.append(seg)
            # add 2~4 char ngrams
            for n in (2, 3, 4):
                if len(seg) >= n:
                    for i in range(0, len(seg) - n + 1):
                        tokens.append(seg[i:i+n])
        # Dedup while preserving order
        seen = set()
        out = []
        for t in tokens:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out
    
    def _search_recursive(self, data: Any, query: str, path: str = '', depth: int = 0) -> List[Dict[str, Any]]:
        """
        遞歸搜索數據
        
        Args:
            data: 要搜索的數據
            query: 查詢關鍵詞
            path: 當前路徑
            depth: 搜索深度
            
        Returns:
            list: 匹配結果列表
        """
        matches = []
        max_depth = 10  # 限制搜索深度
        
        if depth > max_depth:
            return matches
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # 檢查鍵是否匹配
                if query in key.lower():
                    matches.append({
                        'path': current_path,
                        'key': key,
                        'value': value,
                        'type': 'key_match'
                    })
                
                # 遞歸搜索值
                matches.extend(self._search_recursive(value, query, current_path, depth + 1))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                matches.extend(self._search_recursive(item, query, current_path, depth + 1))
        
        elif isinstance(data, (str, int, float)):
            # 檢查值是否匹配
            if query in str(data).lower():
                matches.append({
                    'path': path,
                    'value': data,
                    'type': 'value_match'
                })
        
        return matches
    
    def get_knowledge_summary(self) -> Dict[str, Any]:
        """
        獲取知識庫摘要
        
        Returns:
            dict: 知識庫摘要信息
        """
        try:
            summary = {
                'knowledge_base_version': self.knowledge_data.get('knowledge_base_version', 'unknown'),
                'last_updated': self.knowledge_data.get('last_updated', 'unknown'),
                'community_name': self.knowledge_data.get('community_name', 'unknown'),
                'total_topics': len(self.knowledge_data),
                'topics': list(self.knowledge_data.keys()),
                'learning_history_count': len(self.learning_history),
                'memory_cache_topics': list(self.memory_cache.keys()),
                'total_memories': sum(len(memories) for memories in self.memory_cache.values())
            }
            
            # 添加關鍵統計數據
            if 'key_statistics' in self.knowledge_data:
                summary['key_statistics'] = self.knowledge_data['key_statistics']
            
            # 添加關鍵洞察
            if 'critical_insights' in self.knowledge_data:
                summary['critical_insights'] = self.knowledge_data['critical_insights']
            
            return summary
        except Exception as e:
            return {'error': str(e)}
    
    def get_context_for_ai(self, query: str, max_context_length: int = 2000) -> str:
        """
        為 AI 生成上下文提示
        
        Args:
            query: 查詢或問題
            max_context_length: 最大上下文長度（字符數）
            
        Returns:
            str: 格式化的上下文字符串
        """
        try:
            # 查詢相關知識
            query_result = self.query_knowledge(query)
            
            if not query_result.get('success') or query_result.get('matches_found', 0) == 0:
                # 如果沒有找到匹配，返回知識庫摘要
                summary = self.get_knowledge_summary()
                return f"知識庫摘要:\n{json.dumps(summary, ensure_ascii=False, indent=2)}"
            
            # 構建上下文
            context_parts = []
            context_parts.append(f"# 五常社區知識庫查詢結果\n")
            context_parts.append(f"查詢: {query}\n")
            context_parts.append(f"找到 {query_result['matches_found']} 個相關結果\n\n")
            
            # 添加匹配結果
            for i, result in enumerate(query_result['results'][:10], 1):
                context_parts.append(f"## 結果 {i}\n")
                context_parts.append(f"路徑: {result.get('path', 'N/A')}\n")
                if 'key' in result:
                    context_parts.append(f"關鍵字: {result['key']}\n")
                if 'value' in result:
                    value_str = str(result['value'])
                    if len(value_str) > 200:
                        value_str = value_str[:200] + "..."
                    context_parts.append(f"內容: {value_str}\n")
                context_parts.append("\n")
            
            context = "\n".join(context_parts)
            
            # 如果超過最大長度，截斷
            if len(context) > max_context_length:
                context = context[:max_context_length] + "...\n[內容已截斷]"
            
            return context
        except Exception as e:
            return f"生成上下文時發生錯誤: {str(e)}"
    
    def _summarize_data(self, data: Any) -> str:
        """生成數據摘要"""
        try:
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                return f"字典包含 {len(data)} 個鍵: {', '.join(keys)}"
            elif isinstance(data, list):
                return f"列表包含 {len(data)} 個項目"
            else:
                data_str = str(data)
                return data_str[:100] + "..." if len(data_str) > 100 else data_str
        except:
            return "無法生成摘要"
    
    def save_learning_history(self, file_path: str = 'ai_learning_history.json'):
        """保存學習歷史"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'learning_history': self.learning_history,
                    'memory_cache_summary': {
                        topic: len(memories) for topic, memories in self.memory_cache.items()
                    }
                }, f, ensure_ascii=False, indent=2)
            return {'success': True, 'message': f'學習歷史已保存到: {file_path}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_community_analysis(self):
        """加載並學習社區分析數據"""
        try:
            if not self.knowledge_data:
                return {'success': False, 'error': '知識庫未加載'}
            
            # 學習各個主題
            topics_learned = []
            
            # 地理分析
            if 'geographic_analysis' in self.knowledge_data:
                self.learn_and_memorize('geographic_analysis', self.knowledge_data['geographic_analysis'])
                topics_learned.append('geographic_analysis')
            
            # 住宅分析
            if 'housing_analysis' in self.knowledge_data:
                self.learn_and_memorize('housing_analysis', self.knowledge_data['housing_analysis'])
                topics_learned.append('housing_analysis')
            
            # 人口統計
            if 'demographics' in self.knowledge_data:
                self.learn_and_memorize('demographics', self.knowledge_data['demographics'])
                topics_learned.append('demographics')
            
            # 商業生態
            if 'commercial_ecosystem' in self.knowledge_data:
                self.learn_and_memorize('commercial_ecosystem', self.knowledge_data['commercial_ecosystem'])
                topics_learned.append('commercial_ecosystem')
            
            # 交通運輸
            if 'transportation' in self.knowledge_data:
                self.learn_and_memorize('transportation', self.knowledge_data['transportation'])
                topics_learned.append('transportation')
            
            # 社會企業解決方案
            if 'social_enterprise_solutions' in self.knowledge_data:
                self.learn_and_memorize('social_enterprise_solutions', self.knowledge_data['social_enterprise_solutions'])
                topics_learned.append('social_enterprise_solutions')
            
            # 戰略建議
            if 'strategic_recommendations' in self.knowledge_data:
                self.learn_and_memorize('strategic_recommendations', self.knowledge_data['strategic_recommendations'])
                topics_learned.append('strategic_recommendations')
            
            # 系統整合點
            if 'system_integration_points' in self.knowledge_data:
                self.learn_and_memorize('system_integration_points', self.knowledge_data['system_integration_points'])
                topics_learned.append('system_integration_points')
            
            return {
                'success': True,
                'message': '社區分析數據已學習並記憶',
                'topics_learned': topics_learned,
                'total_topics': len(topics_learned)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


if __name__ == '__main__':
    # 測試知識庫系統
    print("=" * 60)
    print("AI 知識庫系統測試")
    print("=" * 60)
    
    kb = AIKnowledgeBase()
    
    # 加載並學習社區分析
    print("\n📚 加載並學習社區分析數據...")
    result = kb.load_community_analysis()
    print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 獲取知識庫摘要
    print("\n📊 知識庫摘要:")
    summary = kb.get_knowledge_summary()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    # 測試查詢
    print("\n🔍 測試查詢: '人口'")
    query_result = kb.query_knowledge('人口')
    print(f"找到 {query_result.get('matches_found', 0)} 個匹配結果")
    
    # 生成 AI 上下文
    print("\n🤖 生成 AI 上下文:")
    context = kb.get_context_for_ai('五常里人口結構')
    print(context[:500] + "..." if len(context) > 500 else context)
    
    print("\n" + "=" * 60)
