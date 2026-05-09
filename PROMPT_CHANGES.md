# Prompt Değişiklik Raporu

Bu dosyada, projenin yapay zeka (LLM) entegrasyonu sırasında varsayılan promptlarda yapılan değişiklikler listelenmiştir.

* **Değiştirilen Prompt:** [Hangi prompt değiştirildi?]
* **Yeni Prompt:** [Yeni yazılan prompt buraya eklenecek]
* **Değişim Sebebi:** [Yapay zeka daha iyi Türkçe yanıt versin diye vb. açıklama]

## PC-001 — US-J LLM Tutoring Prompt

### What changed
Added a structured LLM prompt for student tutoring responses.

### Why it changed
The system needs to guide students step by step, ask exactly one question, respond in English, and avoid revealing hidden learning objectives.

### Expected effect
The LLM should produce short academic guiding questions that help the student reason through the activity without giving the final answer directly.

### Rules added
- Respond in English.
- Ask exactly one guiding question.
- Do not reveal learning objectives.
- Do not give the final answer directly.
- Use activity terminology.
- Keep the response short and supportive.