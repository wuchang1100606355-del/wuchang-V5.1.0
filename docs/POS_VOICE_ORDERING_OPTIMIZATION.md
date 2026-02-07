# POS 語音對話式點餐優化方案

**文件日期**: 2025-01-07  
**系統版本**: Wuchang OS V5.1.0  
**目標**: 使用 Google Cloud 抵免額度優化 POS 語音對話式點餐

---

## 🎯 方案概述

### 使用另一筆抵免額度

**Google 非營利組織免費額度**：
- **Speech-to-Text API**: 每月 60 分鐘免費
- **Text-to-Speech API**: 每月 400 萬字元免費
- **本地 AI (Ollama)**: 完全免費

---

## 🏗️ 架構設計

### 完整流程

```
┌─────────────┐
│  員工語音   │
│  "我要點餐" │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Speech-to-Text API  │ ← Google Cloud（免費額度）
│ 語音 → 文字         │
└──────┬──────────────┘
       │ "我要點餐"
       ▼
┌─────────────────────┐
│ 本地 AI (Ollama)    │ ← 本地運行（免費）
│ 理解意圖、處理對話  │
└──────┬──────────────┘
       │ "好的，請告訴我要點什麼？"
       ▼
┌─────────────────────┐
│ Text-to-Speech API  │ ← Google Cloud（免費額度）
│ 文字 → 語音         │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│  語音回應   │
│  "好的..."  │
└─────────────┘
```

---

## 🔧 技術實作

### 1. Speech-to-Text API 整合

#### 啟用 API

1. **訪問 Google Cloud Console**
   - 網址：https://console.cloud.google.com/apis/library
   - 搜尋「Cloud Speech-to-Text API」
   - 啟用 API

2. **建立 API Key**
   - 進入「API 和服務」→「憑證」
   - 建立新的 API Key
   - 設定限制（僅 Speech-to-Text API）

#### 實作範例

```python
from google.cloud import speech
import io

def speech_to_text(audio_file_path, language_code='zh-TW'):
    """將語音轉換為文字"""
    client = speech.SpeechClient()
    
    with io.open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=True,
    )
    
    response = client.recognize(config=config, audio=audio)
    
    # 取得轉換結果
    for result in response.results:
        return result.alternatives[0].transcript
    
    return None
```

---

### 2. Text-to-Speech API 整合

#### 啟用 API

1. **訪問 Google Cloud Console**
   - 搜尋「Cloud Text-to-Speech API」
   - 啟用 API

2. **使用相同的 API Key**
   - 或建立專用的 API Key

#### 實作範例

```python
from google.cloud import texttospeech

def text_to_speech(text, output_file, language_code='zh-TW', voice_name='zh-TW-Wavenet-C'):
    """將文字轉換為語音"""
    client = texttospeech.TextToSpeechClient()
    
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
    
    return output_file
```

---

### 3. 本地 AI 對話處理

#### 使用 Ollama 處理對話

```python
import requests

def process_voice_order(user_text, conversation_history=[]):
    """處理語音點餐對話"""
    
    # 建立對話上下文
    context = "\n".join([
        f"用戶: {h['user']}\n小J: {h['assistant']}"
        for h in conversation_history[-5:]  # 最近 5 輪對話
    ])
    
    prompt = f"""
你是 POS 語音點餐助手小J。

對話歷史：
{context}

用戶說：{user_text}

請理解用戶的點餐意圖，並：
1. 確認餐點項目和數量
2. 詢問是否需要調整（甜度、冰塊等）
3. 確認總金額
4. 完成點餐流程

回應要簡潔、親切、專業。
"""
    
    # 呼叫本地 Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2:1.5b",
            "prompt": prompt,
            "stream": False
        }
    )
    
    return response.json()["response"]
```

---

### 4. 完整整合流程

```python
class VoiceOrderingSystem:
    def __init__(self):
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.conversation_history = []
    
    def process_voice_input(self, audio_file):
        """處理語音輸入的完整流程"""
        
        # 1. 語音轉文字
        user_text = self.speech_to_text(audio_file)
        print(f"用戶說: {user_text}")
        
        # 2. 本地 AI 處理對話
        assistant_text = self.process_voice_order(user_text, self.conversation_history)
        print(f"小J 回應: {assistant_text}")
        
        # 3. 文字轉語音
        audio_output = self.text_to_speech(assistant_text)
        
        # 4. 更新對話歷史
        self.conversation_history.append({
            "user": user_text,
            "assistant": assistant_text
        })
        
        return {
            "user_text": user_text,
            "assistant_text": assistant_text,
            "audio_output": audio_output
        }
    
    def speech_to_text(self, audio_file):
        # ... (實作如上)
        pass
    
    def text_to_speech(self, text):
        # ... (實作如上)
        pass
    
    def process_voice_order(self, user_text, history):
        # ... (實作如上)
        pass
```

---

## 💰 成本分析

### Google Cloud 免費額度

| API | 免費額度 | 預估使用 | 費用 |
|-----|---------|---------|------|
| **Speech-to-Text** | 60 分鐘/月 | 30-40 分鐘/月 | $0 |
| **Text-to-Speech** | 400 萬字元/月 | 50-100 萬字元/月 | $0 |
| **本地 AI (Ollama)** | 無限制 | 無限制 | $0 |

**總成本**：$0（完全在免費額度內）

---

## 🎯 優化重點

### 1. 語音識別優化

**使用場景特定模型**：
- 餐廳點餐專用詞彙
- 餐點名稱識別
- 數量、規格識別

**優化建議**：
- 建立自訂詞彙表（餐點名稱）
- 使用語音適應（Speech Adaptation）
- 提高中文識別準確度

### 2. 對話流程優化

**多輪對話處理**：
- 記住上下文
- 確認機制
- 錯誤恢復

**範例流程**：
```
員工: "我要點餐"
小J: "好的，請告訴我要點什麼？"

員工: "一杯拿鐵"
小J: "一杯拿鐵，請問要冰的還是熱的？"

員工: "熱的"
小J: "熱拿鐵一杯，請問甜度？"

員工: "半糖"
小J: "熱拿鐵一杯，半糖，總共 120 元，確認嗎？"

員工: "確認"
小J: "好的，已為您點餐完成！"
```

### 3. 本地 AI 優化

**針對點餐場景優化**：
- 理解點餐意圖
- 處理餐點資訊
- 確認訂單

**提示詞優化**：
```
你是 POS 語音點餐助手小J。

你的任務：
1. 理解員工的點餐需求
2. 確認餐點項目、數量、規格
3. 計算總金額
4. 完成點餐流程

回應風格：
- 簡潔、親切、專業
- 一次只問一個問題
- 確認重要資訊
```

---

## 📊 預期效果

### 性能指標

| 指標 | 目標 | 說明 |
|------|------|------|
| **語音識別準確度** | > 95% | 使用 Google Speech-to-Text |
| **回應速度** | < 2 秒 | 本地 AI + 語音合成 |
| **對話成功率** | > 90% | 多輪對話完成點餐 |
| **成本** | $0 | 完全使用免費額度 |

### 效益

1. **提升效率**
   - 免持點餐，雙手自由
   - 快速完成點餐流程

2. **降低成本**
   - 使用免費額度
   - 減少人工錯誤

3. **改善體驗**
   - 自然的語音對話
   - 親切的 AI 助手

---

## 🛠️ 實作步驟

### Phase 1: 基礎整合（1-2 週）

- [ ] 啟用 Speech-to-Text API
- [ ] 啟用 Text-to-Speech API
- [ ] 建立 API Key
- [ ] 實作基礎語音轉文字
- [ ] 實作基礎文字轉語音

### Phase 2: AI 整合（2-3 週）

- [ ] 整合本地 AI (Ollama)
- [ ] 實作對話流程
- [ ] 優化提示詞
- [ ] 測試多輪對話

### Phase 3: POS 整合（2-3 週）

- [ ] 整合 POS 系統
- [ ] 實作點餐流程
- [ ] 測試完整流程
- [ ] 優化使用者體驗

### Phase 4: 優化與部署（1-2 週）

- [ ] 性能優化
- [ ] 錯誤處理
- [ ] 使用者測試
- [ ] 正式部署

---

## 📋 檢查清單

### API 設定

- [ ] Speech-to-Text API 已啟用
- [ ] Text-to-Speech API 已啟用
- [ ] API Key 已建立並設定限制
- [ ] 免費額度已確認

### 本地 AI

- [ ] Ollama 服務運行中
- [ ] 模型已升級（qwen2:1.5b 或更好）
- [ ] 快取機制已實作
- [ ] 提示詞已優化

### 整合測試

- [ ] 語音轉文字測試通過
- [ ] 文字轉語音測試通過
- [ ] 對話流程測試通過
- [ ] POS 整合測試通過

---

**文件版本**: 1.0  
**最後更新**: 2025-01-07  
**維護者**: 小J (Little J)
