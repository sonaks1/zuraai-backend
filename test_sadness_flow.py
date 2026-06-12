
import httpx
import asyncio
import json

async def test_sadness_flow():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8005", timeout=30.0) as client:
        # 1. User says "I'm feeling sad"
        print("User: I'm feeling sad")
        response = await client.post("/chat/", json={"message": "I'm feeling sad"})
        data = response.json()
        print(f"ZuraAI: {data['reply']}")
        
        # 2. User says "No" (to the AI's question about talking)
        print("\nUser: No")
        response = await client.post("/chat/", json={"message": "No"})
        data = response.json()
        print(f"ZuraAI: {data['reply']}")
        
        # Verify if the menu is shown
        if "Try a calming exercise" in data['reply']:
            print("\nSUCCESS: menu shown.")
        else:
            print("\nFAILURE: menu NOT shown.")
            return

        # 3. User selects "2" (Mood check)
        print("\nUser: 2")
        response = await client.post("/chat/", json={"message": "2"})
        data = response.json()
        print(f"ZuraAI: {data['reply']}")
        
        # Verify if the first question of depression assessment is shown
        if "Little interest or pleasure in activities?" in data['reply']:
            print("\nSUCCESS: Depression assessment started.")
        else:
            print("\nFAILURE: Depression assessment NOT started.")

if __name__ == "__main__":
    # Note: This test assumes the server is running and uses mock user ID 1
    # You may need to clear redis/cache if state persists from previous runs
    asyncio.run(test_sadness_flow())
