from memory.mem0_client import client


def store_facts_from_conversation(student_id, messages):

    formatted_messages = [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in messages
    ]

    client.add(
        formatted_messages,
        user_id=student_id,
        metadata={"type": "factual"}
    )


def get_relevant_facts(student_id, query):
    results = client.search(
        query=query,
        user_id=student_id,
        filters={"type": "factual"},
        limit=8
    )
    if not results:
        return "No prior facts."
    return "\n".join(
        f"- {memory['memory']}"
        for memory in results
    )