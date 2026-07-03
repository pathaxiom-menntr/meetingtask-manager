import json

from openai import AzureOpenAI

from app.core.config import settings


client = AzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
)


SYSTEM_PROMPT = """
You are an AI meeting assistant.

Read the meeting transcript carefully and extract ONLY actionable tasks.

Return ONLY valid JSON.

The JSON must follow this exact format:

{
  "tasks": [
    {
      "title": "Task title",
      "description": "Task description",
      "assignee": "Person name",
      "priority": "medium",
      "due_date": "2025-07-15"
    }
  ]
}

Rules:

1. Return ONLY JSON.
2. Do NOT use markdown.
3. Do NOT explain anything.
4. Ignore discussions that are not action items.
5. If no assignee is mentioned, use null.
6. Keep task titles short and clear.
7. Description should contain enough detail for the assignee.
8. priority must be one of: "low", "medium", "high", "critical". Infer from urgency cues in the transcript. Default to "medium".
9. due_date must be an ISO date string (YYYY-MM-DD) if a deadline is mentioned, otherwise null.
10. If no tasks are present, return:

{
  "tasks": []
}
"""


class AIService:

    @staticmethod
    def generate_tasks(transcript: str) -> list[dict]:
        try:
            response = client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": transcript,
                    },
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if content is None:
                return []

            data = json.loads(content)
            return data.get("tasks", [])
        except Exception as e:
            from fastapi import HTTPException
            print(f"AI Service Error: {str(e)}")
            raise HTTPException(status_code=502, detail=f"AI Processing failed: {str(e)}")