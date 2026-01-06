# ElevenLabs Survey Agent - Tool Configuration

## Tool Name
`record_survey_answer`

## Description
Records a survey answer from the participant. Call this tool after each question is answered to save the response.

## URL
```
https://apps.equalexperts.ai/survey/api/webhook/survey
```

## Method
`POST`

## Headers
| Header | Value |
|--------|-------|
| `X-API-Key` | `18800bb5f51c0a7888f104bcbf053f3d8279ed72fc5dd9b58db64d9ee45fc170` |
| `Content-Type` | `application/json` |

---

## Parameters

### conversation_id
- **Type**: string
- **Required**: Yes
- **Description**: The ElevenLabs conversation ID
- **Value**: Use `{{system__conversation_id}}` variable (note: double underscore after "system")

---

### question_id
- **Type**: string (enum)
- **Required**: Yes
- **Description**: Unique identifier for the question being answered
- **Enum values**:
  - `warmup_org_type`
  - `warmup_role`
  - `experience_focus`
  - `experience_why_matters`
  - `challenges_hardest`
  - `maturity_structure`
  - `maturity_operating_model`
  - `maturity_risk`
  - `maturity_data`
  - `maturity_tools`
  - `maturity_lifecycle`
  - `maturity_governance`
  - `maturity_comments`
  - `different_approaches`
  - `different_unique`
  - `leadership_changes`
  - `final_thoughts`

---

### section_name
- **Type**: string (enum)
- **Required**: Yes
- **Description**: The section of the survey this question belongs to
- **Enum values**:
  - `Warm-up`
  - `Experience with AI`
  - `Challenges`
  - `AI Maturity Check`
  - `What's Different About AI`
  - `Leadership and Skills`
  - `Final Thoughts`

---

### question_text
- **Type**: string
- **Required**: Yes
- **Description**: The full text of the question that was asked

---

### answer_type
- **Type**: string (enum)
- **Required**: Yes
- **Description**: The type of answer
- **Enum values**:
  - `free_text`
  - `rating`

---

### answer_text
- **Type**: string
- **Required**: No
- **Description**: The participant's answer as text. Use for free_text questions and for any comments on rating questions.

---

### answer_rating
- **Type**: integer
- **Required**: No
- **Description**: Rating value 1-5 for rating type questions only
- **Enum values**:
  - `1`
  - `2`
  - `3`
  - `4`
  - `5`

---

### raw_transcript
- **Type**: string
- **Required**: No
- **Description**: The verbatim transcript of what the participant said

---

## Question ID to Section Mapping

| question_id | section_name | answer_type |
|-------------|--------------|-------------|
| `warmup_org_type` | `Warm-up` | `free_text` |
| `warmup_role` | `Warm-up` | `free_text` |
| `experience_focus` | `Experience with AI` | `free_text` |
| `experience_why_matters` | `Experience with AI` | `free_text` |
| `challenges_hardest` | `Challenges` | `free_text` |
| `maturity_structure` | `AI Maturity Check` | `rating` |
| `maturity_operating_model` | `AI Maturity Check` | `rating` |
| `maturity_risk` | `AI Maturity Check` | `rating` |
| `maturity_data` | `AI Maturity Check` | `rating` |
| `maturity_tools` | `AI Maturity Check` | `rating` |
| `maturity_lifecycle` | `AI Maturity Check` | `rating` |
| `maturity_governance` | `AI Maturity Check` | `rating` |
| `maturity_comments` | `AI Maturity Check` | `free_text` |
| `different_approaches` | `What's Different About AI` | `free_text` |
| `different_unique` | `What's Different About AI` | `free_text` |
| `leadership_changes` | `Leadership and Skills` | `free_text` |
| `final_thoughts` | `Final Thoughts` | `free_text` |

---

## Example Tool Calls

### Free Text Answer
```json
{
  "conversation_id": "{{system__conversation_id}}",
  "question_id": "warmup_org_type",
  "section_name": "Warm-up",
  "question_text": "What type of healthcare organisation do you work in?",
  "answer_type": "free_text",
  "answer_text": "Large public hospital network in Melbourne with 5 hospitals",
  "raw_transcript": "I work at a large public hospital network in Melbourne, we have about 5 hospitals in our network"
}
```

### Rating Answer
```json
{
  "conversation_id": "{{system__conversation_id}}",
  "question_id": "maturity_structure",
  "section_name": "AI Maturity Check",
  "question_text": "Clear structure, roles and ownership for AI (1-5)",
  "answer_type": "rating",
  "answer_rating": 3,
  "answer_text": "We have some structure but it's still evolving",
  "raw_transcript": "I'd give us a 3 out of 5, we have some structure but it's still evolving"
}
```

---

## Testing

```bash
curl -X POST https://apps.equalexperts.ai/survey/api/webhook/survey \
  -H "X-API-Key: 18800bb5f51c0a7888f104bcbf053f3d8279ed72fc5dd9b58db64d9ee45fc170" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_123",
    "question_id": "warmup_org_type",
    "section_name": "Warm-up",
    "question_text": "What type of healthcare organisation do you work in?",
    "answer_type": "free_text",
    "answer_text": "Public hospital",
    "raw_transcript": "I work in a public hospital"
  }'
```

Expected response:
```json
{
  "success": true,
  "job_id": "uuid-here",
  "queue": "survey_queue",
  "message": "Survey answer queued"
}
```
