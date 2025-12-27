# 📚 Примеры использования

---
**📚 Навигация:** [🏠 Главная](README.md) | [📦 Установка](installation.md) | [🚀 Запуск](running.md) | [🎯 Лончеры](launchers.md) | [📖 Использование](usage.md) | [⚙️ Настройка](configuration.md) | [📊 Примеры](examples.md) | [🛠️ Рецепты](howto.md) | [🔌 MCP](mcp_integration.md) | [🌍 Туннели](tunnel_guide.md) | [🐳 Docker](docker.md) | [🛠️ Разработка](development.md) | [🚀 Развертывание](deployment.md) | [🔧 cURL](curl_commands.md) | [📋 Проект](project_info.md)
---

Практические примеры работы с FastAPI Foundry для различных сценариев использования.

## 🐍 Python клиенты

В директории `examples/` находятся готовые Python клиенты для демонстрации работы с API.

- **[example_client.py](../examples/example_client.py)**: Демонстрация основных вызовов API (статус, генерация, RAG).
- **[example_rag_client.py](../examples/example_rag_client.py)**: Углубленная демонстрация RAG-системы.
- **[example_mcp_client.py](../examples/example_mcp_client.py)**: Пример взаимодействия с MCP-совместимым сервером.
- **[example_model_client.py](../examples/example_model_client.py)**: Демонстрация управления моделями.

### Базовый асинхронный клиент
Этот код показывает, как создать простого асинхронного клиента для взаимодействия с API.

```python
import aiohttp
import asyncio

class AsyncFoundryClient:
    def __init__(self, base_url="http://localhost:9696", api_key=None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def generate(self, prompt, **kwargs):
        data = {"prompt": prompt, **kwargs}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/v1/generate",
                headers=self.headers,
                json=data
            ) as response:
                return await response.json()

# Использование
async def main():
    client = AsyncFoundryClient()
    result = await client.generate("Объясни машинное обучение", use_rag=True)
    if result.get("success"):
        print(result["content"])

asyncio.run(main())
```

## 🌐 JavaScript клиент (Node.js)

Пример клиента для использования API в среде Node.js.

```javascript
const axios = require('axios');

class FoundryClient {
    constructor(baseURL = 'http://localhost:9696', apiKey = null) {
        this.client = axios.create({
            baseURL: baseURL + '/api/v1',
            headers: {
                'Content-Type': 'application/json',
                ...(apiKey && { 'Authorization': `Bearer ${apiKey}` })
            }
        });
    }
    
    async generate(prompt, options = {}) {
        try {
            const response = await this.client.post('/generate', { prompt, ...options });
            return response.data;
        } catch (error) {
            throw new Error(`Generation failed: ${error.response?.data?.error || error.message}`);
        }
    }
}

// Использование
async function example() {
    const client = new FoundryClient();
    try {
        const result = await client.generate('Объясни Node.js', { temperature: 0.7 });
        console.log('Ответ:', result.content);
    } catch (error) {
        console.error('Ошибка:', error.message);
    }
}

example();
```

## 🚀 Продвинутые сценарии

### Создание чат-бота
```python
class ChatBot:
    def __init__(self, foundry_client):
        self.client = foundry_client
        self.conversation_history = []
    
    async def chat(self, user_message):
        self.conversation_history.append(f"Пользователь: {user_message}")
        context = "\n".join(self.conversation_history[-10:])
        prompt = f"Контекст разговора:\n{context}\n\nОтветь на последнее сообщение."
        
        result = await self.client.generate(prompt, use_rag=True)
        
        if result.get("success"):
            bot_response = result["content"]
            self.conversation_history.append(f"Бот: {bot_response}")
            return bot_response
        return "Извините, произошла ошибка."

# Использование
# client = AsyncFoundryClient()
# bot = ChatBot(client)
# response = await bot.chat("Как мне использовать RAG?")
# print(response)
```

## 🎮 Запуск примеров из веб-интерфейса

Вы можете запускать демонстрационные скрипты прямо из браузера.

1.  Откройте [http://localhost:9696](http://localhost:9696)
2.  Перейдите на вкладку **"Examples"**.
3.  Нажмите на кнопку нужного примера.
4.  Смотрите вывод в реальном времени.

Подробнее в **[руководстве по запуску примеров](examples_guide.md)**.

---
## 🛠️ Навигация по разделу "Практика"

| Документ | Описание |
|----------|----------|
| [📊 Примеры](examples.md) | Готовые примеры кода и сценарии |
| [🛠️ Рецепты](howto.md) | Практические рецепты и настройки |

## 🔗 Другие разделы

| Раздел | Документы |
|--------|-----------|
| **📖 Начало работы** | [📦 Установка](installation.md) • [🚀 Запуск](running.md) • [🎯 Лончеры](launchers.md) • [📖 Использование](usage.md) • [⚙️ Настройка](configuration.md) |
| **🌐 Интеграция** | [🔌 MCP](mcp_integration.md) • [🌍 Туннели](tunnel_guide.md) |
| **🚀 Развертывание** | [🐳 Docker](docker.md) • [🚀 Deployment](deployment.md) |
| **👨‍💻 Разработка** | [🛠️ Development](development.md) • [🔧 cURL](curl_commands.md) • [📋 Проект](project_info.md) |

---

**📚 Быстрые ссылки:** [⬅️ Назад к оглавлению](README.md) | [📖 Все документы](README.md#-документация)

**FastAPI Foundry** - часть экосистемы AiStros  
© 2025 AiStros Team