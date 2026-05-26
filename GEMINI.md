## State-Driven Architecture (Chat vs. Flow Mode)
ZuraAI operates in two distinct modes to ensure therapeutic reliability:
1. **Chat Mode (OpenAI)**: Handles greetings, emotional support, and natural conversation. It provides the "empathetic hook" but never improvises wellness exercises.
2. **Flow Mode (Backend Engine)**: Takes absolute priority during active wellness exercises (breathing, grounding, etc.). The backend manages step-by-step progress, ensuring consistency and preventing AI hallucination of exercise states.
   - **Stress-Level Adaptation**: 
     - *Mild Stress*: Use compact breathing guidance in a single response (including repetition count).
     - *High Anxiety/Panic*: Use slower, step-by-step calming guidance.

### Architectural Rules:
- **Priority**: Flow Mode > Chat Mode. If an exercise is active, the backend intercepts all messages to progress the flow.
- **State Reset**: Casual greetings (e.g., "hi") MUST reset any "awaiting confirmation" flags to prevent random context jumps.
- **Continuation**: Recognize "ok", "done", "next", and "give" as valid triggers for exercise steps.
- **AI Constraint**: The AI must never start an exercise sequence itself. It only suggests the exercise and waits for the backend Flow Engine to take over.
- **Communication Style**:
    - **Avoid**: Abrupt unfinished sentences, vague calming phrases, and empty reassurance.
    - **Instead**: Guide gently, ensure complete emotional flow, and provide clear calming direction.
